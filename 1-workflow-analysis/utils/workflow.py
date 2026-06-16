"""
Data structure and utilities for agentic workflow analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ComponentStatus(Enum):
    """
    Status of workflow components
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass
class TaskRequest:
    """
    Represent a complex task request for analysis.
    This is a input to the workflow analysis process.
    """

    description: str
    complexity_level: str = "medium"
    deadline_days: int = 30
    resource_constraints: Dict[str, Any] = field(default_factory=dict)
    priority: str = "normal"
    stakeholders: List[str] = field(default_factory=list)
    additional_context: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """
        Validate and normalize task request data
        """
        if not self.description or self.description.strip() == "":
            raise ValueError("Task description cannot be empty")

        if self.deadline_days <= 0:
            raise ValueError("Deadline must be positive")


@dataclass
class TaskComponent:
    """
    Represents a single component of a decomposed task.
    """

    name: str
    description: str
    estimated_hours: float
    dependencies: List[str] = field(default_factory=list)
    required_skills: List[str] = field(default_factory=list)
    status: ComponentStatus = ComponentStatus.PENDING
    assigned_agent: Optional[str] = None
    priority: int = 1  # 1 = highest, 5 = lowest
    deliverables: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)

    def __post_init__(self):
        """
        Validate component data.
        """
        if self.estimated_hours < 0:
            raise ValueError("Estimated hours must be non-negative")

        if self.priority < 1 or self.priority > 5:
            raise ValueError("Priority must be between 1 and 5")


@dataclass
class AnalysisResult:
    """
    Result of task analysis containing decomposed components and metadata.
    """

    task_id: str
    components: List[TaskComponent]
    dependencies: Dict[str, List[str]]
    estimated_total_hours: float
    complexity_score: float  # 0.0 to 1.0
    risk_factors: List[str]
    assumptions: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowPlan:
    """
    Coordinated workflow plan with sequencing and resource allocation
    """

    plan_id: str
    task_request: TaskRequest
    analysis_result: AnalysisResult
    execution_sequence: List[str]  # component names in execution order
    resource_allocation: Dict[str, Dict[str, Any]]
    milestone_schedule: Dict[str, datetime]
    contingency_plans: Dict[str, str] = field(default_factory=dict)
    quality_gates: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationResult:
    """
    Result of workflow validation.

    This is the output of the OutputValidator agent.
    """

    is_valid: bool
    confidence_score: float  # 0.0 to 1.0
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    completeness_score: float = 0.0  # 0.0 to 1.0
    feasibility_score: float = 0.0  # 0.0 to 1.0
    validated_at: datetime = field(default_factory=datetime.now)

    def get_overall_score(self) -> float:
        """
        Calculate overall validation score.
        """
        return (
            self.confidence_score + self.completeness_score + self.feasibility_score
        ) / 3.0


@dataclass
class WorkflowResult:
    """
    Complete workflow execution result.

    This represents the final output of the entire workflow process.
    """

    workflow_id: str
    task_request: TaskRequest
    analysis_result: AnalysisResult
    workflow_plan: WorkflowPlan
    validation_result: ValidationResult
    execution_metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def is_successful(self) -> bool:
        """Check if the workflow completed successfully."""
        return (
            self.validation_result.is_valid
            and self.validation_result.confidence_score > 0.7
            and len(self.validation_result.validation_errors) == 0
        )

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the workflow result."""
        return {
            "workflow_id": self.workflow_id,
            "task_description": self.task_request.description[:100] + "...",
            "components_count": len(self.analysis_result.components),
            "estimated_hours": self.analysis_result.estimated_total_hours,
            "complexity_score": self.analysis_result.complexity_score,
            "validation_score": self.validation_result.get_overall_score(),
            "is_successful": self.is_successful(),
            "created_at": self.created_at.isoformat(),
        }
