import logging
from typing import Any, Dict, List

from utils.workflow import ValidationResult, WorkflowPlan

"""
Output Validator Agent
"""

logger = logging.getLogger(__name__)


class OutputValidator:
    """
    Agent responsible for validating workflow outputs.

    This agent demonstrates:
    1. Completeness validation
    2. Feasibility assessment
    3. Quality scoring
    4. Improvement suggestions
    """

    def __init__(self, project_id: str):
        """
        Initialize the Output Validator agent.

        Args:
            project_id: GCP project ID for cloud integrations
        """

        self.project_id = project_id
        self.validation_criteria = self._define_validation_criteria()
        logger.info("OutputValidator initialized")

    def validate_workflow(self, workflow_plan: WorkflowPlan) -> ValidationResult:
        """
        Validate a complete workflow plan.

        Args:
            workflow_plan: The workflow plan to validate

        Returns:
            ValidationResult: Comprehensive validation assessment
        """
        print(f"Validating workflow plan: {workflow_plan.plan_id}")

        # Task 1: Validate completeness
        completeness_score, completeness_errors = self._validate_completeness(
            workflow_plan
        )

        # Task 2: Assess feasibility
        feasibility_score, feasibility_warnings = self._assess_feasibility(
            workflow_plan
        )

        # Task 3: Calculate confidence score
        confidence_score = self._calculate_confidence(
            workflow_plan, completeness_score, feasibility_score
        )

        # Task 4: Generate suggestions
        suggestions = self._generate_suggestions(
            workflow_plan, completeness_errors, feasibility_warnings
        )

        # Task 5: Determine overall validity
        is_valid = self._determine_validity(
            completeness_score, feasibility_score, confidence_score
        )

        return ValidationResult(
            is_valid=is_valid,
            confidence_score=confidence_score,
            validation_errors=completeness_errors,
            validation_warnings=feasibility_warnings,
            suggestions=suggestions,
            completeness_score=completeness_score,
            feasibility_score=feasibility_score,
        )

    def _define_validation_criteria(self) -> Dict[str, Any]:
        """
        Define validation criteria and thresholds.
        """
        return {
            "min_completeness_score": 0.7,
            "min_feasibility_score": 0.5,
            "min_confidence_score": 0.6,
            "max_acceptable_errors": 3,
            "max_acceptable_warnings": 7,
            "required_components": [
                "execution_sequence",
                "resource_allocation",
                "milestone_schedule",
                "quality_gates",
                "contingency_plans",
            ],
            "required_analysis_fields": [
                "components",
                "dependencies",
                "estimated_total_hours",
                "complexity_score",
                "risk_factors",
            ],
            "min_components": 1,
            "max_components": 15,
            "min_quality_gates": 2,
            "max_reasonable_hours": 2000,
            "min_reasonable_hours": 1,
        }

    def _validate_completeness(
        self, workflow_plan: WorkflowPlan
    ) -> tuple[float, List[str]]:
        """
        Validate that the workflow plan complete.
        """
        print("Validating completeness")

        errors = []
        score_components = []

        analysis_result = workflow_plan.analysis_result
        required_fields = [
            "execution_sequence",
            "resource_allocation",
            "milestone_schedule",
            "quality_gates",
        ]

        for field in required_fields:
            if not hasattr(workflow_plan, field) or not getattr(workflow_plan, field):
                errors.append(f"Missing required field: {field}")
            else:
                score_components.append(1.0)

        # Validate component details
        if analysis_result and analysis_result.components:
            for component in analysis_result.components:
                if not component.name or component.name.strip() == "":
                    errors.append("Component missing name")
                else:
                    score_components.append(1.0)

                if not component.description or component.description.strip() == "":
                    errors.append(f"Component '{component.name}' missing description")
                else:
                    score_components.append(1.0)

                if component.estimated_hours <= 0:
                    errors.append(
                        f"Component '{component.name}' has invalid estimated hours"
                    )
                else:
                    score_components.append(1.0)
        else:
            errors.append("No components found in analysis result")

        # Check dependency coverage
        if analysis_result.dependencies:
            component_names = {comp.name for comp in analysis_result.components}
            for component_name, deps in analysis_result.dependencies.items():
                for dep in deps:
                    if dep not in component_names:
                        errors.append(
                            f"Component '{component_name}' depends on non-existent component '{dep}'"
                        )
                    else:
                        score_components.append(1.0)

        # Check execution sequence covers all components
        if workflow_plan.execution_sequence:
            sequence_components = set(workflow_plan.execution_sequence)
            analysis_components = {comp.name for comp in analysis_result.components}
            missing_from_sequence = analysis_components - sequence_components
            extra_in_sequence = sequence_components - analysis_components

            if missing_from_sequence:
                errors.append(
                    f"Components missing from execution sequence: {missing_from_sequence}"
                )
            if extra_in_sequence:
                errors.append(
                    f"Unknown components in execution sequence: {extra_in_sequence}"
                )

            if not missing_from_sequence and not extra_in_sequence:
                score_components.append(1.0)
        else:
            errors.append("Execution sequence is empty")

        # Check resource allocation completeness
        if workflow_plan.resource_allocation:
            for component in analysis_result.components:
                if component.name not in workflow_plan.resource_allocation:
                    errors.append(
                        f"No resource allocation for component '{component.name}'"
                    )
                else:
                    allocation = workflow_plan.resource_allocation[component.name]
                    required_allocation_fields = [
                        "estimated_hours",
                        "required_skills",
                        "assigned_team",
                    ]
                    for field in required_allocation_fields:
                        if field not in allocation:
                            errors.append(
                                f"Resource allocation for '{component.name}' missing field: {field}"
                            )
                        else:
                            score_components.append(1.0)

        # Calculate completeness score
        if score_components:
            completeness_score = sum(score_components) / len(score_components)
        else:
            completeness_score = 0.0

        # Penalize for errors
        if errors:
            completeness_score = max(0.0, completeness_score - (len(errors) * 0.1))

        print(f"Completeness score: {completeness_score:.2f} ({len(errors)} errors)")
        return completeness_score, errors

    def _assess_feasibility(
        self, workflow_plan: WorkflowPlan
    ) -> tuple[float, List[str]]:
        """
        Assess the feasibility if the workflow plan.
        """
        print("Assessing feasibility...")

        warnings = []
        feasibility_factors = []

        # Timeline feasibility
        analysis_result = workflow_plan.analysis_result
        total_hours = analysis_result.estimated_total_hours
        task_request = workflow_plan.task_request

        if task_request:
            deadline_days = task_request.deadline_days

            # Check if timeline is realistic (assuming 8 hours per working day)
            required_days = total_hours / 8
            if required_days > deadline_days:
                warnings.append(
                    f"Timeline may be too tight: {required_days:.1f} days needed vs {deadline_days} days available"
                )
                feasibility_factors.append(0.3)  # Low feasibility for timeline
            elif required_days > deadline_days * 0.8:
                warnings.append("Time allocation may be insufficient for task complexity")
                feasibility_factors.append(0.6)  # Medium feasibility
            else:
                feasibility_factors.append(0.9)  # Good timeline feasibility
        else:
            warnings.append("No task request provided; skipping detailed timeline and resource assessment.")
            feasibility_factors.append(0.7)  # Default moderate feasibility for missing data

        # Resource feasibility
        if workflow_plan.resource_allocation:
            total_budget = sum(
                alloc.get("budget_allocation", 0)
                for alloc in workflow_plan.resource_allocation.values()
            )

            # Check if resource constraints are specified
            if task_request and (
                hasattr(task_request, "resource_constraints")
                and task_request.resource_constraints
            ):
                budget_limit = task_request.resource_constraints.get(
                    "budget", float("inf")
                )
                team_size_limit = task_request.resource_constraints.get(
                    "team_size", float("inf")
                )

                if total_budget > budget_limit:
                    warnings.append(
                        f"Budget may be exceeded: ${total_budget:.0f} estimated vs ${budget_limit:.0f} limit"
                    )
                    feasibility_factors.append(0.4)
                else:
                    feasibility_factors.append(0.8)

                # Check team size requirements
                unique_teams = set()
                for alloc in workflow_plan.resource_allocation.values():
                    unique_teams.add(alloc.get("assigned_team", "Unknown"))

                if len(unique_teams) > team_size_limit:
                    warnings.append(
                        f"Team coordination complexity: {len(unique_teams)} teams needed"
                    )
                    feasibility_factors.append(0.6)
                else:
                    feasibility_factors.append(0.8)
            elif not task_request:
                # No constraints specified, assume moderate feasibility
                feasibility_factors.append(0.7)
            else:
                # No constraints specified, assume moderate feasibility
                feasibility_factors.append(0.7)


        # Complexity assessment
        complexity_score = analysis_result.complexity_score
        if complexity_score > 0.8:
            warnings.append(
                "Very high complexity may require additional expertise or time"
            )
            feasibility_factors.append(0.5)
        elif complexity_score > 0.6:
            warnings.append("High complexity requires careful management")
            feasibility_factors.append(0.7)
        else:
            feasibility_factors.append(0.8)

        # Risk factor assessment
        risk_count = len(analysis_result.risk_factors)
        if risk_count > 4:
            warnings.append("High number of risk factors may impact delivery")
            feasibility_factors.append(0.5)
        elif risk_count > 2:
            warnings.append("Multiple risk factors require mitigation planning")
            feasibility_factors.append(0.7)
        else:
            feasibility_factors.append(0.8)

        # Dependency complexity
        if analysis_result.dependencies:
            avg_deps = sum(
                len(deps) for deps in analysis_result.dependencies.values()
            ) / len(analysis_result.dependencies)
            if avg_deps > 3:
                warnings.append("Complex dependency chain may cause delays")
                feasibility_factors.append(0.6)
            elif avg_deps > 1:
                feasibility_factors.append(0.8)
            else:
                feasibility_factors.append(0.9)

        # Milestone timing feasibility
        if workflow_plan.milestone_schedule:
            milestones = sorted(workflow_plan.milestone_schedule.values())
            for i in range(1, len(milestones)):
                days_between = (milestones[i] - milestones[i - 1]).days
                if days_between < 3:
                    warnings.append("Some milestones are very close together (<3 days)")
                    feasibility_factors.append(0.6)
                    break
            else:
                feasibility_factors.append(0.8)

        # Calculate overall feasibility score
        if feasibility_factors:
            feasibility_score = sum(feasibility_factors) / len(feasibility_factors)
        else:
            feasibility_score = 0.5  # Default moderate feasibility

        print(f"Feasibility score: {feasibility_score:.2f} ({len(warnings)} warnings)")
        return feasibility_score, warnings

    def _calculate_confidence(
        self,
        workflow_plan: WorkflowPlan,
        completeness_score: float,
        feasibility_score: float,
    ) -> float:
        """
        Calculate overall confidence in the workflow plan.
        """
        # Weight different factors
        analysis_result = workflow_plan.analysis_result

        # Base confidence from completeness and feasibility
        base_confidence = completeness_score * 0.4 + feasibility_score * 0.4

        # Complexity factor (lower complexity = higher confidence)
        complexity_factor = (1.0 - analysis_result.complexity_score) * 0.15

        # Risk factor (fewer risks = higher confidence)
        risk_factor = max(0.0, (5 - len(analysis_result.risk_factors)) / 5) * 0.1

        # Dependencies factor (simpler dependencies = higher confidence)
        if analysis_result.dependencies:
            total_deps = sum(
                len(deps) for deps in analysis_result.dependencies.values()
            )
            avg_deps = total_deps / len(analysis_result.dependencies)
            dependency_factor = max(0.0, (3 - avg_deps) / 3) * 0.05
        else:
            dependency_factor = 0.05  # No dependencies is good

        # Component count factor (not too few, not too many)
        component_count = len(analysis_result.components)
        if 3 <= component_count <= 7:
            component_factor = 0.05  # Sweet spot
        elif component_count < 3:
            component_factor = 0.02  # Too few might be under-analyzed
        else:
            component_factor = 0.03  # Too many might be over-complex

        # Quality gates factor (more gates = more confidence in quality)
        quality_gate_factor = min(0.05, len(workflow_plan.quality_gates) * 0.005)

        # Contingency planning factor
        contingency_factor = min(0.05, len(workflow_plan.contingency_plans) * 0.005)

        # Calculate total confidence
        confidence = (
            base_confidence
            + complexity_factor
            + risk_factor
            + dependency_factor
            + component_factor
            + quality_gate_factor
            + contingency_factor
        )

        return min(1.0, max(0.0, confidence))

    def _generate_suggestions(
        self, workflow_plan: WorkflowPlan, errors: List[str], warnings: List[str]
    ) -> List[str]:
        """
        Generate suggestions for improving the workflow plan.
        """
        suggestions = []
        analysis_result = workflow_plan.analysis_result

        # Suggestions based on errors
        if errors:
            suggestions.append(
                "Address validation errors before proceeding with execution"
            )
            if any("missing" in error.lower() for error in errors):
                suggestions.append(
                    "Complete all required workflow components and fields"
                )
            if any(
                "dependency" in error.lower() or "depend" in error.lower()
                for error in errors
            ):
                suggestions.append("Review and resolve dependency conflicts")

        # Suggestions based on warnings
        if warnings:
            if any(
                "time" in warning.lower() or "deadline" in warning.lower()
                for warning in warnings
            ):
                suggestions.append("Consider adding buffer time for unexpected delays")
            if any(
                "budget" in warning.lower() or "cost" in warning.lower()
                for warning in warnings
            ):
                suggestions.append(
                    "Review scope to optimize costs or secure additional budget"
                )
            if any("milestone" in warning.lower() for warning in warnings):
                suggestions.append(
                    "Adjust milestone spacing for more realistic timeline"
                )
            if any("complex" in warning.lower() for warning in warnings):
                suggestions.append(
                    "Consider breaking down complex components into smaller tasks"
                )

        # Optimization suggestions based on analysis
        if len(analysis_result.components) > 7:
            suggestions.append(
                "Consider grouping related components to reduce coordination overhead"
            )
        elif len(analysis_result.components) < 3:
            suggestions.append(
                "Ensure task analysis is sufficiently detailed for proper planning"
            )

        # Resource optimization
        if workflow_plan.resource_allocation:
            unique_teams = set()
            for alloc in workflow_plan.resource_allocation.values():
                unique_teams.add(alloc.get("assigned_team", "Unknown"))

            if len(unique_teams) > 5:
                suggestions.append(
                    "Consider consolidating team assignments to reduce coordination complexity"
                )

        # Risk mitigation suggestions
        risk_count = len(analysis_result.risk_factors)
        if risk_count > 3:
            suggestions.append(
                "Develop specific mitigation strategies for each identified risk"
            )
        if risk_count == 0:
            suggestions.append("Consider conducting additional risk assessment")

        # Quality assurance suggestions
        if len(workflow_plan.quality_gates) < 3:
            suggestions.append(
                "Consider adding more quality checkpoints throughout the workflow"
            )

        # Best practice recommendations
        if analysis_result.complexity_score > 0.7:
            suggestions.append(
                "Implement regular progress reviews for high-complexity projects"
            )
            suggestions.append(
                "Consider engaging subject matter experts for complex components"
            )

        # Timeline recommendations
        total_days = analysis_result.estimated_total_hours / 8
        if total_days > 60:
            suggestions.append(
                "Break down long-duration projects into phases with interim deliverables"
            )

        # Dependency management
        if analysis_result.dependencies:
            avg_deps = sum(
                len(deps) for deps in analysis_result.dependencies.values()
            ) / len(analysis_result.dependencies)
            if avg_deps > 2:
                suggestions.append(
                    "Review dependency chain to identify opportunities for parallel execution"
                )

        # Resource allocation suggestions
        suggestions.append("Review resource allocation for potential bottlenecks")
        suggestions.append("Ensure quality gates are clearly defined and measurable")
        suggestions.append("Validate assumptions with stakeholders before proceeding")

        # Communication recommendations
        if len(analysis_result.components) > 4:
            suggestions.append(
                "Establish clear communication protocols for multi-component workflows"
            )

        return suggestions

    def _determine_validity(
        self,
        completeness_score: float,
        feasibility_score: float,
        confidence_score: float,
    ) -> bool:
        """
        Determine overall validity of the workflow plan.
        """
        # Define validity thresholds
        # More lenient thresholds for educational/learning purposes
        min_completeness = 0.7  # Must be reasonably complete
        min_feasibility = 0.5  # Should be somewhat feasible
        min_confidence = 0.6  # Moderate confidence required

        # All thresholds must be met
        validity_checks = [
            completeness_score >= min_completeness,
            feasibility_score >= min_feasibility,
            confidence_score >= min_confidence,
        ]

        return all(validity_checks)

    def _define_validation_criteria(self) -> Dict[str, Any]:
        """
        Define validation criteria and thresholds.
        """
        return {
            "min_completeness_score": 0.7,
            "min_feasibility_score": 0.5,
            "min_confidence_score": 0.6,
            "max_acceptable_errors": 3,
            "max_acceptable_warnings": 7,
            "required_components": [
                "execution_sequence",
                "resource_allocation",
                "milestone_schedule",
                "quality_gates",
                "contingency_plans",
            ],
            "required_analysis_fields": [
                "components",
                "dependencies",
                "estimated_total_hours",
                "complexity_score",
                "risk_factors",
            ],
            "min_components": 1,
            "max_components": 15,
            "min_quality_gates": 2,
            "max_reasonable_hours": 2000,
            "min_reasonable_hours": 1,
        }
