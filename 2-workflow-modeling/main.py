"""
Event Planning Workflow System
"""

import time
import uuid

from models.event_models import EventRequest, EventType, NodeType, WorkflowNode
from orchestrator import Agent, MultiAgentOrchestrator
from recovery_handler import DisruptionType, RecoveryHandler
from state_manager import AdvancedStateManager
from workflow_modeler import WorkflowModeler


def simple_sequential_workflow():
    """
    Create a simple event planning system with these sequential steps:
    - Gather requirements
    - Find venue
    - Select vendors
    - Review and finalize
    """

    modeler = WorkflowModeler()

    nodes = [
        WorkflowNode(
            node_id="gather_requirements",
            node_type=NodeType.SEQUENTIAL,
            name="Gather Requirements",
            description="Collect event requirements and constraints",
            action="gather_requirements",
            next_node_id="find_venue",
        ),
        WorkflowNode(
            node_id="find_venue",
            node_type=NodeType.SEQUENTIAL,
            name="Find Venue",
            description="Search for and select appropriate venue",
            action="find_venue",
            next_node_id="select_vendors",
        ),
        WorkflowNode(
            node_id="select_vendors",
            node_type=NodeType.SEQUENTIAL,
            name="Select Vendors",
            description="Choose catering and entertainment vendors",
            action="select_vendors",
            next_node_id="review_plan",
        ),
        WorkflowNode(
            node_id="review_plan",
            node_type=NodeType.SEQUENTIAL,
            name="Review and Finalize",
            description="Final review of the event plan",
            action="review_plan",
            next_node_id=None,  # End of workflow
        ),
    ]

    modeler.add_nodes(nodes)

    # Register action functions
    def gather_requirements(context):
        print(f"  Gathering requirements for {context.get('event_type')} event")
        context["requirements_gathered"] = True
        context["requirements"] = ["venue", "catering", "entertainment"]
        return context

    def find_venue(context):
        attendees = context.get("attendee_count", 50)
        print(f"  Finding venue for {attendees} attendees")
        context["venue_found"] = True
        context["venue"] = "Grand Hall"
        return context

    def select_vendors(context):
        print(f"  Selecting vendors for event {context.get('event_type')} event")
        context["vendors_selected"] = True
        context["vendors"] = ["Premium Catering", "DJ Services"]
        return context

    def review_plan(context):
        print("  Reviewing complete event plan")
        context["plan_reviewed"] = True
        context["status"] = "approved"
        return context

    modeler.register_action("gather_requirements", gather_requirements)
    modeler.register_action("find_venue", find_venue)
    modeler.register_action("select_vendors", select_vendors)
    modeler.register_action("review_plan", review_plan)

    # Execute workflow
    context = {"event_type": "corporate", "attendee_count": 100, "budget": 15000}

    print("\nExecuting sequential workflow:")
    result = modeler.execute_workflow("gather_requirements", context)

    print("\nSequential workflow completed")
    print(f"Final state: venue={result.get('venue')}, vendors={result.get('vendors')}")


def conditional_branching():
    """
    Add conditional branching

    Creates a workflow that branches based on event type:
    - Corporate events -> formal vendor selection path
    - Public events -> community vendor selection path
    """

    print("\n" + "=" * 70)
    print("2: Conditional Branching Workflow")
    print("=" * 70)

    modeler = WorkflowModeler()

    # Define workflow with conditional branching
    nodes = [
        WorkflowNode(
            node_id="start",
            node_type=NodeType.SEQUENTIAL,
            name="Start Event Planning",
            description="Initialize event planning",
            action="initialize",
            next_node_id="event_type_decision",
        ),
        WorkflowNode(
            node_id="event_type_decision",
            node_type=NodeType.CONDITIONAL,
            name="Event Type Decision",
            description="Branch based on event type",
            conditions={
                "event_type == 'corporate'": "corporate_vendor_path",
                "event_type == 'public'": "public_vendor_path",
            },
            next_node_id="finalize",  # Default if no conditions match
        ),
        WorkflowNode(
            node_id="corporate_vendor_path",
            node_type=NodeType.SEQUENTIAL,
            name="Corporate Vendor Selection",
            description="Select premium vendors for corporate event",
            action="select_corporate_vendors",
            next_node_id="finalize",
        ),
        WorkflowNode(
            node_id="public_vendor_path",
            node_type=NodeType.SEQUENTIAL,
            name="Community Vendor Selection",
            description="Select community vendors for public event",
            action="select_community_vendors",
            next_node_id="finalize",
        ),
        WorkflowNode(
            node_id="finalize",
            node_type=NodeType.SEQUENTIAL,
            name="Finalize Plan",
            description="Complete the event plan",
            action="finalize",
            next_node_id=None,
        ),
    ]

    modeler.add_nodes(nodes)

    # Register actions
    def initialize(ctx):
        print(f"  Initializing planning for {ctx.get('event_type')} event")
        ctx["initialized"] = True
        return ctx

    def select_corporate_vendors(ctx):
        print("  Selecting PREMIUM vendors for corporate event")
        ctx["vendors"] = ["Premium Catering Co.", "Professional DJ", "Luxury Decor"]
        ctx["vendor_tier"] = "premium"
        return ctx

    def select_community_vendors(ctx):
        print("  Selecting COMMUNITY vendors for public event")
        ctx["vendors"] = ["Local Restaurant", "Community Band", "Volunteer Decorators"]
        ctx["vendor_tier"] = "community"
        return ctx

    def finalize(ctx):
        print(f"  Finalizing with {ctx.get('vendor_tier')} vendors")
        ctx["finalized"] = True
        return ctx

    modeler.register_action("initialize", initialize)
    modeler.register_action("select_corporate_vendors", select_corporate_vendors)
    modeler.register_action("select_community_vendors", select_community_vendors)
    modeler.register_action("finalize", finalize)

    # Test corporate path
    print("\nTesting Corporate Event Path:")
    context_corporate = {"event_type": "corporate", "budget": 20000}
    result_corporate = modeler.execute_workflow("start", context_corporate)
    print(f"  Result: {result_corporate.get('vendors')}")

    # Test public path
    print("\nTesting Public Event Path:")
    context_public = {"event_type": "public", "budget": 5000}
    result_public = modeler.execute_workflow("start", context_public)
    print(f"  Result: {result_public.get('vendors')}")


def parallel_execution():
    """
    Design parallel execution

    Executes multiple tasks concurrently:
    - Venue selection
    - Catering selection
    - Entertainment selection

    All run in parallel to save time.
    """

    print("\n" + "=" * 70)
    print("3: Parallel Execution Workflow")
    print("=" * 70)

    modeler = WorkflowModeler()

    # Create workflow with parallel node
    nodes = [
        WorkflowNode(
            node_id="start",
            node_type=NodeType.SEQUENTIAL,
            name="Start Planning",
            description="Initialize event planning",
            action="start_planning",
            next_node_id="parallel_vendor_selection",
        ),
        WorkflowNode(
            node_id="parallel_vendor_selection",
            node_type=NodeType.PARALLEL,
            name="Parallel Vendor Selection",
            description="Select all vendors in parallel",
            parallel_nodes=["select_venue", "select_catering", "select_entertainment"],
            next_node_id="aggregate_results",
        ),
        WorkflowNode(
            node_id="select_venue",
            node_type=NodeType.SEQUENTIAL,
            name="Select Venue",
            description="Choose event venue",
            action="select_venue",
            next_node_id=None,
        ),
        WorkflowNode(
            node_id="select_catering",
            node_type=NodeType.SEQUENTIAL,
            name="Select Catering",
            description="Choose catering service",
            action="select_catering",
            next_node_id=None,
        ),
        WorkflowNode(
            node_id="select_entertainment",
            node_type=NodeType.SEQUENTIAL,
            name="Select Entertainment",
            description="Choose entertainment",
            action="select_entertainment",
            next_node_id=None,
        ),
        WorkflowNode(
            node_id="aggregate_results",
            node_type=NodeType.SEQUENTIAL,
            name="Aggregate Results",
            description="Combine all vendor selections",
            action="aggregate",
            next_node_id=None,
        ),
    ]

    modeler.add_nodes(nodes)

    # Register actions (with simulated delays)
    def start_planning(ctx):
        print("  Starting parallel vendor selection...")
        return ctx

    def select_venue(ctx):
        print("    [Parallel] Selecting venue...")
        time.sleep(0.1)  # Simulate work
        return {"venue": "Convention Center", "venue_cost": 5000}

    def select_catering(ctx):
        print("    [Parallel] Selecting catering...")
        time.sleep(0.1)  # Simulate work
        return {"catering": "Gourmet Catering", "catering_cost": 7500}

    def select_entertainment(ctx):
        print("    [Parallel] Selecting entertainment...")
        time.sleep(0.1)  # Simulate work
        return {"entertainment": "Live Band", "entertainment_cost": 2000}

    def aggregate(ctx):
        results = ctx.get("parallel_results", [])
        print(f"  Aggregating {len(results)} parallel results...")
        for result in results:
            ctx.update(result)
        ctx["total_cost"] = sum(
            [
                ctx.get("venue_cost", 0),
                ctx.get("catering_cost", 0),
                ctx.get("entertainment_cost", 0),
            ]
        )
        return ctx

    modeler.register_action("start_planning", start_planning)
    modeler.register_action("select_venue", select_venue)
    modeler.register_action("select_catering", select_catering)
    modeler.register_action("select_entertainment", select_entertainment)
    modeler.register_action("aggregate", aggregate)

    # Execute parallel workflow
    print("\nExecuting parallel workflow:")
    start_time = time.time()
    context = {"event_type": "corporate", "budget": 20000}
    result = modeler.execute_workflow("start", context)
    execution_time = time.time() - start_time

    print(f"\nParallel execution completed in {execution_time:.2f}s")
    print(f"Total cost: ${result.get('total_cost', 0)}")
    print(f"Selections: venue={result.get('venue')}, catering={result.get('catering')}")


def orchestration_and_error_handling():
    """
    4: Wire up orchestration and error handling

    Part A - Orchestration:
      - Register multiple agents (venue, catering, entertainment, budget)
      - Create an EventRequest
      - Execute workflow through orchestrator

    Part B - Error Handling:
      - Use RecoveryHandler to handle vendor cancellation
      - Use RecoveryHandler to handle budget cuts
      - Observe recovery strategies
    """
    print("\n" + "=" * 70)
    print("4: Multi-Agent Orchestration + Error Handling")
    print("=" * 70)

    # Part A: Orchestration
    print("\n--- Part A: Multi-Agent Orchestration ---")

    state_manager = AdvancedStateManager()
    orchestrator = MultiAgentOrchestrator(state_manager)

    # Register agents with different roles
    orchestrator.register_agent(Agent("venue_selector", "venue_specialist"))
    orchestrator.register_agent(Agent("catering_agent", "catering_specialist"))
    orchestrator.register_agent(
        Agent("entertainment_agent", "entertainment_specialist")
    )
    orchestrator.register_agent(Agent("budget_agent", "budget_analyst"))

    print(f"  Registered {len(orchestrator.agents)} agents")

    # Create event request
    event_request = EventRequest(
        event_id="EVT-001",
        event_type=EventType.CORPORATE,
        attendee_count=150,
        budget=25000,
        date="2025-06-15",
        location_preference="Downtown",
    )

    # Execute workflow through orchestrator
    session_id = f"session-{uuid.uuid4().hex[:8]}"
    result = orchestrator.execute_workflow(
        "corporate_event_planning", event_request, session_id
    )

    print("  Orchestration completed")
    print(f"  Budget utilization: {result.get('utilization_percent', 0)}%")

    # Part B: Error Handling
    print("\n--- Part B: Error Handling ---")

    recovery_handler = RecoveryHandler()

    # Test 1: Vendor cancellation
    print("\nScenario 1: Vendor Cancellation")
    context = {
        "event_type": "corporate",
        "budget": 15000,
        "vendors": ["Original Catering Co.", "DJ Services"],
    }

    result = recovery_handler.handle_disruption(
        DisruptionType.VENDOR_CANCELLATION, context, {"vendor_type": "catering"}
    )

    print(f"  Recovery action: {result.get('action')}")
    print(f"  Backup vendor: {result.get('selected_backup', 'N/A')}")

    # Test 2: Budget cut
    print("\nScenario 2: Budget Cut")
    context = {"event_type": "corporate", "budget": 20000, "attendee_count": 100}

    result = recovery_handler.handle_disruption(
        DisruptionType.BUDGET_CUT, context, {"amount": 5000}
    )

    print(f"  Recovery action: {result.get('action')}")
    print(f"  New budget: ${result.get('new_budget', 0)}")
    print(f"  Total savings: ${result.get('total_savings', 0)}")


def complete_workflows():
    """
    5: Test complete workflows

    Run complete end-to-end workflows for both event types:
    - Corporate event with premium vendors
    - Public event with community vendors
    """
    print("\n" + "=" * 70)
    print("5: Complete Event Workflows")
    print("=" * 70)

    state_manager = AdvancedStateManager()
    orchestrator = MultiAgentOrchestrator(state_manager)

    # Setup agents
    orchestrator.register_agent(Agent("venue_selector", "venue_specialist"))
    orchestrator.register_agent(Agent("catering_agent", "catering_specialist"))
    orchestrator.register_agent(
        Agent("entertainment_agent", "entertainment_specialist")
    )
    orchestrator.register_agent(Agent("budget_agent", "budget_analyst"))

    # 1: Corporate Event
    print("\n--- Corporate Event Test ---")

    corporate_request = EventRequest(
        event_id="CORP-2025-001",
        event_type=EventType.CORPORATE,
        attendee_count=200,
        budget=35000,
        date="2025-08-20",
        location_preference="Downtown Conference Center",
        special_requirements=["A/V Equipment", "Breakout Rooms", "WiFi"],
    )

    session_id = f"corp-{uuid.uuid4().hex[:8]}"
    result = orchestrator.execute_workflow(
        "corporate_event", corporate_request, session_id
    )

    # Create event plan
    event_plan = orchestrator.create_event_plan(result)

    print(f"  Event ID: {corporate_request.event_id}")
    print(f"  Venue: {event_plan.venue}")
    print(f"  Vendors: {len(event_plan.vendors)}")
    print(f"  Total Cost: ${event_plan.total_cost:.2f}")
    print(f"  Status: {result.get('status', 'completed')}")

    # 2: Public Event
    print("\n--- Public Event Test ---")

    public_request = EventRequest(
        event_id="PUB-2025-001",
        event_type=EventType.PUBLIC,
        attendee_count=300,
        budget=12000,
        date="2025-07-04",
        location_preference="City Park",
        special_requirements=["Outdoor Setup", "Sound System"],
        accessibility_needs=["Wheelchair Access", "ASL Interpreter"],
    )

    session_id = f"pub-{uuid.uuid4().hex[:8]}"
    result = orchestrator.execute_workflow("public_event", public_request, session_id)

    # Create event plan
    event_plan = orchestrator.create_event_plan(result)

    print(f"  Event ID: {public_request.event_id}")
    print(f"  Venue: {event_plan.venue}")
    print(f"  Vendors: {len(event_plan.vendors)}")
    print(f"  Total Cost: ${event_plan.total_cost:.2f}")
    print(f"  Status: {result.get('status', 'completed')}")


def performance_analysis():
    """
    6: Analyze workflow performance

    Track and analyze workflow performance metrics:
    - Record multiple workflow executions
    - Track success rates and execution times
    - Generate performance summaries
    """
    print("\n" + "=" * 70)
    print("6: Workflow Performance Analysis")
    print("=" * 70)

    state_manager = AdvancedStateManager()

    # Simulate multiple workflow executions
    print("\nRecording workflow executions...")

    workflows = [
        ("corporate_event", True, 2.5, ["start", "venue", "catering", "finalize"]),
        ("corporate_event", True, 2.3, ["start", "venue", "catering", "finalize"]),
        ("corporate_event", True, 2.1, ["start", "venue", "catering", "finalize"]),
        ("public_event", True, 1.8, ["start", "venue", "vendors", "finalize"]),
        ("public_event", False, 3.2, ["start", "venue", "error"]),
        ("public_event", True, 1.9, ["start", "venue", "vendors", "finalize"]),
    ]

    for workflow_name, success, exec_time, nodes in workflows:
        state_manager.record_execution(workflow_name, success, exec_time, nodes)
        status = "Success" if success else "Failed"
        print(f"  [{status}] {workflow_name}: {exec_time}s ({len(nodes)} nodes)")

    # Display metrics
    print("\n" + "-" * 50)
    print("Corporate Event Metrics:")
    print("-" * 50)
    corp_metrics = state_manager.get_metrics_summary("corporate_event")
    for key, value in corp_metrics.items():
        print(f"  {key}: {value}")

    print("\n" + "-" * 50)
    print("Public Event Metrics:")
    print("-" * 50)
    pub_metrics = state_manager.get_metrics_summary("public_event")
    for key, value in pub_metrics.items():
        print(f"  {key}: {value}")

    print("\nPerformance analysis complete!")


def main():
    """
    Main entry point
    """

    demos = [
        ("Sequential Workflow", simple_sequential_workflow),
        ("Conditional Branching", conditional_branching),
        ("Parallel Execution", parallel_execution),
        ("Orchestration + Error Handling", orchestration_and_error_handling),
        ("Complete Workflows", complete_workflows),
        ("Performance Analysis", performance_analysis),
    ]

    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            demo_func()
        except Exception as e:
            print(f"\nDemo {i} error: {str(e)}")
            import traceback

            traceback.print_exc()

    print("\n\n" + "=" * 70)
    print("ALL DEMONSTRATIONS COMPLETED")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("  - Sequential workflows for linear processes")
    print("  - Conditional branching for decision points")
    print("  - Parallel execution for efficiency")
    print("  - Multi-agent orchestration for coordination")
    print("  - Error handling for resilience")
    print("  - Performance monitoring for optimization")


if __name__ == "__main__":
    main()
