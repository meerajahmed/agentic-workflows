"""
Multi-Agent Orchestrator - Coordinate Multiple Agents in Workflows

This module orchestrates multi-agent execution within workflows.
It demonstrates the Orchestrator pattern for complex coordination.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List

from models.event_models import EventPlan, EventRequest, VendorSelection
from state_manager import AdvancedStateManager
from workflow_modeler import WorkflowModeler


class Agent:
    """
    Simple agent representation for demonstration.

    In a real system, these would be LLM-based agents.
    """

    def __init__(self, name: str, role: str):
        """
        Initialize an agent.

        Args:
            name: Agent name/identifier
            role: Agent's role/specialty
        """
        self.name = name
        self.role = role

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task with the given context.

        Args:
            task: Task description
            context: Execution context

        Returns:
            Task results
        """
        print(f"  🤖 Agent {self.name} ({self.role}) executing: {task}")

        # Simulate agent work
        time.sleep(0.1)

        # Return mock results based on role
        if self.role == "venue_specialist":
            return self._select_venue(context)
        elif self.role == "catering_specialist":
            return self._select_catering(context)
        elif self.role == "entertainment_specialist":
            return self._select_entertainment(context)
        elif self.role == "budget_analyst":
            return self._analyze_budget(context)
        else:
            return {"status": "completed", "agent": self.name}

    def _select_venue(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Select a venue based on context."""
        event_type = context.get("event_type", "public")
        attendees = context.get("attendee_count", 50)

        if event_type == "corporate":
            venue = "Grand Conference Center"
            cost = 5000 + (attendees * 50)
        else:
            venue = "Community Event Hall"
            cost = 2000 + (attendees * 20)

        return {
            "venue": venue,
            "cost": cost,
            "capacity": attendees + 20,
            "amenities": ["A/V Equipment", "WiFi", "Parking"],
        }

    def _select_catering(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Select catering based on context."""
        event_type = context.get("event_type", "public")
        attendees = context.get("attendee_count", 50)

        if event_type == "corporate":
            vendor = "Premium Catering Co."
            cost = attendees * 75
        else:
            vendor = "Local Catering Services"
            cost = attendees * 35

        return {
            "vendor": vendor,
            "vendor_type": "catering",
            "cost": cost,
            "menu": ["Appetizers", "Main Course", "Dessert", "Beverages"],
        }

    def _select_entertainment(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Select entertainment based on context."""
        event_type = context.get("event_type", "public")

        if event_type == "corporate":
            vendor = "Professional DJ Services"
            cost = 1500
        else:
            vendor = "Local Band"
            cost = 800

        return {
            "vendor": vendor,
            "vendor_type": "entertainment",
            "cost": cost,
            "services": ["Music", "MC Services"],
        }

    def _analyze_budget(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze budget allocation."""
        budget = context.get("budget", 10000)
        total_cost = context.get("total_cost", 0)

        remaining = budget - total_cost
        utilization = (total_cost / budget * 100) if budget > 0 else 0

        return {
            "budget": budget,
            "total_cost": total_cost,
            "remaining": remaining,
            "utilization_percent": round(utilization, 2),
            "status": "within_budget" if remaining >= 0 else "over_budget",
        }


class MultiAgentOrchestrator:
    """
    Orchestrates multiple agents in workflow execution.
    """

    def __init__(self, state_manager: AdvancedStateManager):
        """
        Initialize the orchestrator.

        Args:
            state_manager: State manager for tracking workflow state
        """
        self.state_manager = state_manager
        self.agents: Dict[str, Agent] = {}
        self.workflow_modeler = WorkflowModeler()

    def register_agent(self, agent: Agent) -> None:
        """
        Register an agent with the orchestrator.

        Args:
            agent: Agent to register
        """
        self.agents[agent.name] = agent
        print(f"✅ Registered agent: {agent.name} ({agent.role})")

    def execute_workflow(
        self, workflow_name: str, event_request: EventRequest, session_id: str
    ) -> Dict[str, Any]:
        """
        Execute a complete workflow with multi-agent coordination.

        Args:
            workflow_name: Name of the workflow to execute
            event_request: Event planning request
            session_id: Session identifier

        Returns:
            Workflow execution results
        """
        print(f"\n{'=' * 60}")
        print(f"🎯 Starting Multi-Agent Workflow: {workflow_name}")
        print(f"{'=' * 60}\n")

        start_time = time.time()

        # Create workflow session
        session = self.state_manager.create_workflow_session(
            session_id=session_id, event_request=event_request, entry_node_id="start"
        )

        # Initialize context from event request
        context = {
            "event_type": event_request.event_type.value,
            "attendee_count": event_request.attendee_count,
            "budget": event_request.budget,
            "location": event_request.location_preference,
            "event_id": event_request.event_id,
        }

        self.state_manager.start_session(session_id)

        try:
            # Execute workflow
            results = self._execute_sequential_workflow(session_id, context)

            # Mark as successful
            self.state_manager.complete_session(session_id, success=True)

            execution_time = time.time() - start_time

            print(f"\n✅ Workflow completed successfully in {execution_time:.2f}s")

            return results

        except Exception as e:
            error_msg = f"Workflow execution failed: {str(e)}"
            print(f"\n❌ {error_msg}")

            self.state_manager.log_error(session_id, error_msg)
            self.state_manager.complete_session(session_id, success=False)

            execution_time = time.time() - start_time

            return {
                "status": "failed",
                "error": error_msg,
                "execution_time": execution_time,
            }

    def execute_parallel_agents(
        self, agent_tasks: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple agents in parallel.

        Args:
            agent_tasks: List of tasks, each with 'agent_name' and 'task'
            context: Shared execution context

        Returns:
            List of results from each agent
        """
        print(f"\n🔀 Executing {len(agent_tasks)} agents in parallel...")

        results = []

        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=len(agent_tasks)) as executor:
            # Submit all tasks
            future_to_task = {}
            for task_spec in agent_tasks:
                agent_name = task_spec["agent_name"]
                task = task_spec["task"]

                if agent_name in self.agents:
                    agent = self.agents[agent_name]
                    future = executor.submit(agent.execute, task, context)
                    future_to_task[future] = agent_name
                else:
                    print(f"⚠️  Agent {agent_name} not found")

            # Collect results as they complete
            for future in as_completed(future_to_task):
                agent_name = future_to_task[future]
                try:
                    result = future.result()
                    results.append({"agent": agent_name, "result": result})
                    print(f"  ✓ {agent_name} completed")
                except Exception as e:
                    print(f"  ✗ {agent_name} failed: {str(e)}")
                    results.append({"agent": agent_name, "error": str(e)})

        print(f"✅ Parallel execution completed: {len(results)} results")

        return results

    def _execute_sequential_workflow(
        self, session_id: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a sequential workflow with agents.

        This is a simplified implementation for demonstration.

        Args:
            session_id: Session identifier
            context: Execution context

        Returns:
            Workflow results
        """
        # Phase 1: Venue Selection
        print("\n📍 Phase 1: Venue Selection")
        if "venue_selector" in self.agents:
            venue_result = self.agents["venue_selector"].execute(
                "Select appropriate venue", context
            )
            context.update(venue_result)
            context["total_cost"] = venue_result.get("cost", 0)

        # Phase 2: Parallel Vendor Selection
        print("\n📍 Phase 2: Parallel Vendor Selection")
        vendor_tasks = [
            {"agent_name": "catering_agent", "task": "Select catering"},
            {"agent_name": "entertainment_agent", "task": "Select entertainment"},
        ]

        vendor_results = self.execute_parallel_agents(vendor_tasks, context)

        # Aggregate vendor costs
        vendors = []
        for vendor_result in vendor_results:
            if "result" in vendor_result:
                result = vendor_result["result"]
                context["total_cost"] += result.get("cost", 0)
                vendors.append(result)

        context["vendors"] = vendors

        # Phase 3: Budget Analysis
        print("\n📍 Phase 3: Budget Analysis")
        if "budget_agent" in self.agents:
            budget_result = self.agents["budget_agent"].execute(
                "Analyze budget allocation", context
            )
            context.update(budget_result)

        return context

    def create_event_plan(self, context: Dict[str, Any]) -> EventPlan:
        """
        Create an EventPlan from workflow execution context.

        Args:
            context: Workflow execution context

        Returns:
            Complete event plan
        """
        event_plan = EventPlan(
            event_id=context.get("event_id", "unknown"),
            event_type=context.get("event_type", "public"),
            venue=context.get("venue", "TBD"),
            total_cost=context.get("total_cost", 0.0),
        )

        # Add vendors
        for vendor_data in context.get("vendors", []):
            vendor = VendorSelection(
                vendor_type=vendor_data.get("vendor_type", "unknown"),
                vendor_name=vendor_data.get("vendor", "TBD"),
                cost=vendor_data.get("cost", 0.0),
                confirmed=True,
            )
            event_plan.add_vendor(vendor)

        # Add risk assessment
        if context.get("status") == "over_budget":
            event_plan.risk_assessment["budget"] = "Over budget - requires adjustment"
        else:
            event_plan.risk_assessment["budget"] = "Within budget"

        # Add contingency plans
        event_plan.contingency_plans = [
            "Backup venue identified",
            "Alternative vendor list prepared",
            "Budget reduction strategies documented",
        ]

        return event_plan

    def get_orchestration_summary(self) -> Dict[str, Any]:
        """
        Get summary of orchestrator state.

        Returns:
            Summary dictionary
        """
        return {
            "registered_agents": len(self.agents),
            "agent_names": list(self.agents.keys()),
            "agent_roles": {name: agent.role for name, agent in self.agents.items()},
        }
