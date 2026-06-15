import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from utils.workflow import AnalysisResult, TaskRequest, WorkflowPlan

logger = logging.getLogger(__name__)


class WorkflowCoordinator:
    """
    Agent responsible for coordinating workflow execution.

    This agent demonstrate:
    1. Sequencing components based on dependencies
    2. Resource allocation and conflict resolution
    3. Milestone planning and scheduling
    4. Quality gate definition
    """

    def __init__(self, project_id: str):

        self.project_id = project_id

    def create_workflow_plan(
        self, analysis_result: AnalysisResult, task_request: TaskRequest = None
    ) -> WorkflowPlan:
        """
        Create a coordinated workflow plan for analysis results.

        Args:
            analysis_result: Result from TaskAnalyzer
            test_request: Original task request (Optional)

        Returns:
            WorkflowPlan: Coordinated execution plan with sequencing and resources
        """
        print(
            f"Creating workflow plan for {len(analysis_result.components)} components..."
        )

        # Implement workflow sequencing
        execution_sequence = self._sequence_components(analysis_result)

        # Implement resource allocation
        resource_allocation = self._allocate_resources(analysis_result)

        # Create milestone schedule
        milestone_schedule = self._create_milestone_schedule(analysis_result)

        # Define quality gates
        quality_gates = self._define_quality_gates(analysis_result)

        # Create contingency plans
        contingency_plans = self._create_contingency_plans(analysis_result)

        # Define quality gates

        return WorkflowPlan(
            plan_id=f"plan_{analysis_result.task_id}",
            task_request=task_request,
            analysis_result=analysis_result,
            execution_sequence=execution_sequence,
            resource_allocation=resource_allocation,
            milestone_schedule=milestone_schedule,
            contingency_plans=contingency_plans,
            quality_gates=quality_gates,
        )

    def _sequence_components(self, analysis_results: AnalysisResult) -> List[str]:
        """
        Sequence components based on dependencies and priorities.
        """
        print("Sequencing workflow components...")

        # Implement topological sort for dependencies
        components = analysis_results.components
        dependencies = analysis_results.dependencies
        sequence = []
        remaining = {comp.name: comp for comp in components}

        # Track which component has been scheduled
        scheduled = set()

        # Continue until all components are scheduled
        while remaining:
            # Find components with no unscheduled dependencies
            ready_components = []

            for comp_name, component in remaining.items():
                # Check if all dependencies are already scheduled
                comp_deps = dependencies.get(comp_name, [])
                if all(dep in scheduled for dep in comp_deps):
                    ready_components.append((comp_name, component))

            # If no components are ready, we have a circular dependency
            if not ready_components:
                # Break the cycle by adding a component with minimal dependencies
                min_deps = min(
                    remaining.values(), key=lambda x: len(dependencies.get(x.name, []))
                )
                ready_components = [(min_deps.name, min_deps)]
                print(f"Breaking dependency cycle, scheduling {min_deps.name}")

            # Sort ready components by priority (lower number = higher priority)
            ready_components.sort(key=lambda x: x[1].priority)

            # Schedule the highest priority ready component
            next_comp_name, next_comp = ready_components[0]
            sequence.append(next_comp_name)
            scheduled.add(next_comp_name)
            del remaining[next_comp_name]

        print(f"Sequenced {len(sequence)} components")
        return sequence

    def _allocate_resources(
        self, analysis_result: AnalysisResult
    ) -> Dict[str, Dict[str, Any]]:
        """
        Allocate resources to workflow components.
        """
        print("Allocating resources...")

        allocation = {}

        # Define skill-based hourly rates
        skill_rates = {
            "project management": 120,
            "analysis": 100,
            "design": 110,
            "development": 130,
            "testing": 90,
            "deployment": 100,
            "research": 95,
            "coordination": 85,
            "logistics": 75,
            "vendor management": 90,
            "event planning": 80,
            "marketing": 105,
            "implementation": 115,
            "operations": 95,
        }

        # Track resource utilization across components
        skill_demand = {}

        for component in analysis_result.components:
            # Determine resource requirements for each component
            required_skills = component.required_skills or ["general"]

            # Calculate budget based on skills required
            avg_rate = sum(
                skill_rates.get(skill, 85) for skill in required_skills
            ) / len(required_skills)
            budget_allocation = component.estimated_hours * avg_rate

            # Track skill demand for conflict resolution
            for skill in required_skills:
                skill_demand[skill] = (
                    skill_demand.get(skill, 0) + component.estimated_hours
                )

            # Determine team assignment based on skills
            if "management" in " ".join(required_skills):
                assigned_team = "Project Management Team"
            elif "development" in " ".join(
                required_skills
            ) or "implementation" in " ".join(required_skills):
                assigned_team = "Development Team"
            elif "design" in " ".join(required_skills):
                assigned_team = "Design Team"
            elif "testing" in " ".join(required_skills):
                assigned_team = "QA Team"
            elif "marketing" in " ".join(required_skills):
                assigned_team = "Marketing Team"
            else:
                assigned_team = "General Project Team"

            # Determine tools needed based on component type
            tools_needed = []
            component_name_lower = component.name.lower()
            if "planning" in component_name_lower:
                tools_needed = ["Project Management Software", "Gantt Chart Tools"]
            elif "design" in component_name_lower:
                tools_needed = ["Design Software", "Prototyping Tools"]
            elif "development" in component_name_lower:
                tools_needed = ["IDE", "Version Control", "CI/CD Pipeline"]
            elif "testing" in component_name_lower:
                tools_needed = ["Testing Framework", "Bug Tracking System"]
            elif "marketing" in component_name_lower:
                tools_needed = ["Marketing Automation", "Analytics Tools"]
            else:
                tools_needed = ["Collaboration Tools", "Communication Platform"]

            allocation[component.name] = {
                "estimated_hours": component.estimated_hours,
                "required_skills": required_skills,
                "assigned_team": assigned_team,
                "tools_needed": tools_needed,
                "budget_allocation": budget_allocation,
                "hourly_rate": avg_rate,
                "priority": component.priority,
            }

        # Identify potential resource conflicts
        high_demand_skills = {
            skill: hours for skill, hours in skill_demand.items() if hours > 40
        }
        if high_demand_skills:
            print(f"High demand skills detected: {list(high_demand_skills.keys())}")

        print(f"Allocated resources for {len(allocation)} components")
        return allocation

    def _create_milestone_schedule(
        self, analysis_result: AnalysisResult
    ) -> Dict[str, datetime]:
        """
        Create milestone schedule with key dates.
        """
        print("Creating milestone schedule...")

        milestones = {}
        current_date = datetime.now()

        # Define milestone types based on components
        components = analysis_result.components
        total_hours = analysis_result.estimated_total_hours

        # Calculate working days (8 hours per day)
        total_days = max(1, total_hours / 8)

        # Add buffer time based on complexity (15-30% buffer)
        complexity_buffer = 0.15 + (analysis_result.complexity_score * 0.15)
        buffered_days = total_days * (1 + complexity_buffer)

        # Create milestone schedule
        milestones["Project Kickoff"] = current_date + timedelta(days=1)

        # Component completion milestones
        accumulated_hours = 0
        for i, component in enumerate(components):
            accumulated_hours += component.estimated_hours
            milestone_date = current_date + timedelta(
                days=1 + (accumulated_hours / 8) * (1 + complexity_buffer)
            )
            milestones[f"{component.name} Complete"] = milestone_date

        # Key project milestones
        milestone_dates = [
            ("Requirements Finalized", 0.15),
            ("Design Approval", 0.30),
            ("Development Complete", 0.75),
            ("Testing Complete", 0.90),
            ("Final Delivery", 1.0),
        ]

        for milestone_name, progress_ratio in milestone_dates:
            milestone_date = current_date + timedelta(
                days=1 + (buffered_days * progress_ratio)
            )
            milestones[milestone_name] = milestone_date

        # Add risk-based review points
        if analysis_result.complexity_score > 0.7:
            milestones["Mid-project Risk Review"] = current_date + timedelta(
                days=1 + (buffered_days * 0.5)
            )

        if len(analysis_result.risk_factors) > 3:
            milestones["Stakeholder Check-in"] = current_date + timedelta(
                days=1 + (buffered_days * 0.25)
            )

        print(f"Created {len(milestones)} milestones")
        return milestones

    def _define_quality_gates(self, analysis_result: AnalysisResult) -> List[str]:
        """
        Define quality gates for workflow validation.
        """
        print("Defining quality gates...")

        quality_gates = []

        # Define component-level quality gates
        for component in analysis_result.components:
            # Each component gets its own acceptance criteria gate
            quality_gates.append(f"{component.name} - Acceptance Criteria Met")

            # Add specific gates based on component type
            component_name_lower = component.name.lower()
            if "planning" in component_name_lower:
                quality_gates.append(f"{component.name} - Requirements Documented")
            elif "design" in component_name_lower:
                quality_gates.append(f"{component.name} - Design Review Approved")
            elif (
                "development" in component_name_lower
                or "implementation" in component_name_lower
            ):
                quality_gates.append(f"{component.name} - Code Review Passed")
                quality_gates.append(f"{component.name} - Unit Tests Passing")
            elif "testing" in component_name_lower:
                quality_gates.append(f"{component.name} - Test Cases Executed")
                quality_gates.append(f"{component.name} - Defects Resolved")

        # Define workflow-level quality gates
        workflow_gates = [
            "Overall Requirements Validation",
            "Stakeholder Approval Checkpoint",
            "Integration Testing Complete",
            "Performance Criteria Met",
            "Documentation Complete",
            "Final Quality Review Passed",
        ]
        quality_gates.extend(workflow_gates)

        # Include stakeholder review points based on complexity
        if analysis_result.complexity_score > 0.6:
            quality_gates.extend(
                ["Technical Architecture Review", "Risk Mitigation Verification"]
            )

        if len(analysis_result.risk_factors) > 2:
            quality_gates.extend(
                ["Risk Assessment Update", "Contingency Plan Validation"]
            )

        # Add compliance gates if indicated by requirements
        task_description = getattr(analysis_result, "task_description", "").lower()
        if any(
            word in task_description for word in ["compliance", "regulation", "audit"]
        ):
            quality_gates.extend(
                ["Regulatory Compliance Check", "Audit Trail Verification"]
            )

        print(f"Defined {len(quality_gates)} quality gates")
        return quality_gates

    def _create_contingency_plans(
        self, analysis_result: AnalysisResult
    ) -> Dict[str, str]:
        """
        Create contingency plans for identified risks.
        """
        print("Creating contingency plans...")

        contingency_plans = {}

        # Address each identified risk factor with specific mitigation strategies
        for risk in analysis_result.risk_factors:
            risk_lower = risk.lower()
            if "deadline" in risk_lower or "tight" in risk_lower:
                contingency_plans[risk] = (
                    "Prioritize critical components, parallel execution where possible, consider MVP approach"
                )
            elif "budget" in risk_lower or "cost" in risk_lower:
                contingency_plans[risk] = (
                    "Review scope for cost optimization, negotiate vendor rates, consider open-source alternatives"
                )
            elif "team" in risk_lower or "resource" in risk_lower:
                contingency_plans[risk] = (
                    "Cross-train team members, identify backup contractors, implement pair programming"
                )
            elif "stakeholder" in risk_lower or "requirement" in risk_lower:
                contingency_plans[risk] = (
                    "Establish clear communication protocols, regular check-ins, documented approval process"
                )
            elif "vendor" in risk_lower or "external" in risk_lower:
                contingency_plans[risk] = (
                    "Identify backup vendors, include SLAs in contracts, maintain vendor performance metrics"
                )
            elif "complexity" in risk_lower or "expertise" in risk_lower:
                contingency_plans[risk] = (
                    "Engage subject matter experts, implement proof of concepts, increase testing cycles"
                )
            elif "coordinate" in risk_lower or "multiple" in risk_lower:
                contingency_plans[risk] = (
                    "Implement clear communication channels, regular sync meetings, shared project dashboards"
                )
            else:
                contingency_plans[risk] = (
                    "Monitor closely, implement early warning systems, prepare alternative approaches"
                )

        # Plan for common failure modes
        common_failure_plans = {
            "Component delay": "Reallocate resources from non-critical tasks, adjust timeline with stakeholder approval, implement parallel workflows",
            "Resource unavailability": "Activate backup resource pool, temporarily outsource critical components, redistribute workload",
            "Scope creep": "Document all changes formally, assess impact on timeline/budget, require stakeholder sign-off",
            "Quality issues": "Increase review frequency, involve additional experts, implement automated testing",
            "Integration problems": "Conduct early integration testing, maintain rollback procedures, implement gradual deployment",
            "Technology failure": "Maintain backup systems, implement redundancy, have technical support contracts",
            "Communication breakdown": "Establish escalation protocols, implement multiple communication channels, regular status updates",
        }
        contingency_plans.update(common_failure_plans)

        # Define escalation procedures based on complexity
        if analysis_result.complexity_score > 0.7:
            contingency_plans["High complexity escalation"] = (
                "Engage senior technical leadership, consider external consultants, implement additional oversight"
            )

        if len(analysis_result.components) > 5:
            contingency_plans["Complex coordination escalation"] = (
                "Assign dedicated project coordinator, implement project management tools, increase meeting frequency"
            )

        print(f"Created {len(contingency_plans)} contingency plans")
        return contingency_plans
