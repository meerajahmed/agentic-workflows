#!/usr/bin/env python3
"""
Implementing Agentic Workflows

1. Decompose complex tasks into agent-manageable steps
2. Implement basic agent coordination using ADK
3. Demonstrate workflow pattern in action
    - Sequential workflow
    - Coordinator and validator
"""

import os
import sys
from pathlib import Path

from agents.analyzer import TaskAnalyzer
from agents.coordinator import WorkflowCoordinator
from agents.validator import OutputValidator
from dotenv import load_dotenv
from utils.workflow import TaskRequest, WorkflowResult

load_dotenv()

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """
    Main workflow execution - demonstrates sequential agent coordination
    """
    print("=" * 50)
    print("Agentic Workflow Analysis")

    tasks = [
        "Plan a company retreat for 50 employees including venue, catering, and team activities"
    ]

    # Task 1: Initialize agents

    project_id = os.getenv("PROJECT_ID")

    analyzer = TaskAnalyzer(project_id)
    coordinator = WorkflowCoordinator(project_id)
    validator = OutputValidator(project_id)

    print("Agents initialized successfully")

    # Task 2: Implement workflow coordination
    print("Processing tasks through workflow...")

    for i, task in enumerate(tasks):
        print(f"--- Task {i + 1}: {task} ---")

        # Create task request
        task_request = TaskRequest(
            description=task, complexity_level="medium", deadline_days=30
        )

        # Step 1: Break down the task into components
        print("Step 1: Analyzing task components...")
        analysis_result = analyzer.analyze_task(task_request)
        print(
            f"Analysis complete: {len(analysis_result.components)} components identified"
        )

        # Step 2: Create coordination plan
        print("Step 2: Creating coordination output...")
        coordination_plan = coordinator.create_workflow_plan(
            analysis_result, task_request
        )
        print(
            f"Coordination plan created with {len(coordination_plan.execution_sequence)} steps"
        )

        # Step 3: Validate completeness and feasibility
        print("Step 3: Validating output...")
        validation_result = validator.validate_workflow(coordination_plan)
        print(
            f"Validation complete: {'Valid' if validation_result.is_valid else 'Invalid'} (Score: {validation_result.get_overall_score():.2f})"
        )

        # Step 4: Presenting structured results
        print("Step 4: Presenting results...")

        # Create complete workflow result
        workflow_result = WorkflowResult(
            workflow_id=f"workflow_{i + 1}",
            task_request=task_request,
            analysis_result=analysis_result,
            workflow_plan=coordination_plan,
            validation_result=validation_result,
        )

        # Display comprehensive results
        print("=" * 50)
        print(f"WORKFLOW ANALYSIS RESULTS - Task {i + 1}")
        print("=" * 60)

        print(f"Task: {task_request.description}")
        print(f"⏱Deadline: {task_request.deadline_days} days")
        print(f"Complexity: {task_request.complexity_level}")

        print("Analysis Summary:")
        print(f"   • Components: {len(analysis_result.components)}")
        print(f"   • Total Hours: {analysis_result.estimated_total_hours}")
        print(f"   • Complexity Score: {analysis_result.complexity_score:.2f}")
        print(f"   • Risk Factors: {len(analysis_result.risk_factors)}")

        print("Components & Dependencies:")
        for component in analysis_result.components:
            deps = (
                ", ".join(component.dependencies) if component.dependencies else "None"
            )
            print(
                f"   • {component.name} ({component.estimated_hours}h) - Deps: {deps}"
            )

        print("\n⚠️  Risk Factors:")
        for risk in analysis_result.risk_factors:
            print(f"   • {risk}")

        print("\n📋 Execution Sequence:")
        for step_num, step in enumerate(coordination_plan.execution_sequence, 1):
            print(f"   {step_num}. {step}")

        print("Validation Results:")
        print(f"   • Overall Score: {validation_result.get_overall_score():.2f}")
        print(f"   • Confidence: {validation_result.confidence_score:.2f}")
        print(f"   • Completeness: {validation_result.completeness_score:.2f}")
        print(f"   • Feasibility: {validation_result.feasibility_score:.2f}")

        if validation_result.validation_warnings:
            print("\n Warnings:")
            for warning in validation_result.validation_warnings:
                print(f"   • {warning}")

        if validation_result.suggestions:
            print("\n Suggestions:")
            for suggestion in validation_result.suggestions:
                print(f"   • {suggestion}")

        print(
            f"\n Workflow {'SUCCESS' if workflow_result.is_successful() else 'NEEDS ATTENTION'}"
        )
        print("=" * 60)

    # Test workflow with edge cases
    print("\n Running validation tests...")

    # Test workflow with edge cases
    edge_cases = [
        "Plan something with no specific details",  # Vague input
        "Plan a Mars colony for 1 million people",  # Unrealistic scope
        "Simple task with basic requirements",  # Simple input
    ]

    print("\n🔍 Testing Edge Cases:")
    print("-" * 40)

    for case_num, edge_case in enumerate(edge_cases, 1):
        print(f"\n Edge Case {case_num}: {edge_case}")

        if not edge_case.strip():  # Handle empty input
            print("Empty input detected - skipping analysis")
            continue

        try:
            # Create edge case task request
            edge_request = TaskRequest(
                description=edge_case,
                complexity_level="medium",
                deadline_days=30,
                resource_constraints={},
            )

            # Run through workflow
            edge_analysis = analyzer.analyze_task(edge_request)
            edge_plan = coordinator.create_workflow_plan(edge_analysis)
            edge_validation = validator.validate_workflow(edge_plan)

            print(f"   • Components: {len(edge_analysis.components)}")
            print(f"   • Complexity: {edge_analysis.complexity_score:.2f}")
            print(
                f"   • Validation: {'✅ Valid' if edge_validation.is_valid else '❌ Invalid'}"
            )
            print(f"   • Score: {edge_validation.get_overall_score():.2f}")

            if edge_validation.validation_errors:
                print("   • Errors found:")
                for error in edge_validation.validation_errors[
                    :2
                ]:  # Show first 2 errors
                    print(f"     - {error}")

        except Exception as e:
            print(f"   ❌ Edge case failed: {str(e)}")

    print("\n✅ Edge case testing complete")

    print("\n🎉 Lesson 1 Complete!")
    print("\nNext Steps:")
    print("1. Review your workflow design - did it handle edge cases?")
    print("2. Test with different complex inputs")
    print("3. Prepare for Lesson 2: Advanced Workflow Modeling")


if __name__ == "__main__":
    main()
