"""
Recovery Handler - Error Handling and Recovery Strategies

This module implements error detection and recovery for workflows.
It demonstrates the Strategy pattern for recovery logic.
"""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from models.event_models import NodeType, WorkflowNode


class DisruptionType(Enum):
    """Types of disruptions that can occur in event planning."""

    VENDOR_CANCELLATION = "vendor_cancellation"
    BUDGET_CUT = "budget_cut"
    VENUE_UNAVAILABLE = "venue_unavailable"
    WEATHER_ISSUE = "weather_issue"
    CAPACITY_EXCEEDED = "capacity_exceeded"
    LAST_MINUTE_CHANGE = "last_minute_change"


class RecoveryStrategy(Enum):
    """Recovery strategies for handling disruptions."""

    FIND_BACKUP = "find_backup"
    REDUCE_SCOPE = "reduce_scope"
    REPLAN = "replan"
    ESCALATE = "escalate"
    ACCEPT_RISK = "accept_risk"


class RecoveryHandler:
    """
    Handles disruptions and implements recovery strategies.

    This demonstrates professional error handling patterns
    that make workflows resilient to failures.
    """

    def __init__(self):
        """Initialize the recovery handler."""
        self.disruption_log: List[Dict[str, Any]] = []
        self.recovery_strategies: Dict[DisruptionType, RecoveryStrategy] = {
            DisruptionType.VENDOR_CANCELLATION: RecoveryStrategy.FIND_BACKUP,
            DisruptionType.BUDGET_CUT: RecoveryStrategy.REDUCE_SCOPE,
            DisruptionType.VENUE_UNAVAILABLE: RecoveryStrategy.FIND_BACKUP,
            DisruptionType.WEATHER_ISSUE: RecoveryStrategy.REPLAN,
            DisruptionType.CAPACITY_EXCEEDED: RecoveryStrategy.REPLAN,
            DisruptionType.LAST_MINUTE_CHANGE: RecoveryStrategy.ESCALATE,
        }

        # Register recovery action handlers
        self.recovery_actions: Dict[RecoveryStrategy, Callable] = {
            RecoveryStrategy.FIND_BACKUP: self._find_backup,
            RecoveryStrategy.REDUCE_SCOPE: self._reduce_scope,
            RecoveryStrategy.REPLAN: self._replan,
            RecoveryStrategy.ESCALATE: self._escalate,
            RecoveryStrategy.ACCEPT_RISK: self._accept_risk,
        }

    def handle_disruption(
        self,
        disruption_type: DisruptionType,
        context: Dict[str, Any],
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Handle a disruption and execute recovery strategy.

        Args:
            disruption_type: Type of disruption that occurred
            context: Current workflow context
            details: Additional details about the disruption

        Returns:
            Recovery results with updated context
        """
        print(f"\n⚠️  DISRUPTION DETECTED: {disruption_type.value}")

        if details:
            print(f"   Details: {details}")

        # Log the disruption
        disruption_record = {
            "type": disruption_type.value,
            "context": context.copy(),
            "details": details or {},
        }
        self.disruption_log.append(disruption_record)

        # Determine recovery strategy
        strategy = self.recovery_strategies.get(
            disruption_type, RecoveryStrategy.ESCALATE
        )

        print(f"🔧 Recovery Strategy: {strategy.value}")

        # Execute recovery action
        if strategy in self.recovery_actions:
            recovery_action = self.recovery_actions[strategy]
            result = recovery_action(context, details or {})

            print(f"✅ Recovery action completed")

            return result
        else:
            print(f"⚠️  No recovery action registered for {strategy.value}")
            return {
                "status": "unhandled",
                "disruption": disruption_type.value,
                "strategy": strategy.value,
            }

    def _find_backup(
        self, context: Dict[str, Any], details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Find backup vendors or venues.

        Args:
            context: Current workflow context
            details: Disruption details

        Returns:
            Recovery results
        """
        print("   🔍 Finding backup options...")

        vendor_type = details.get("vendor_type", "unknown")

        # Simulate finding backup based on event type
        event_type = context.get("event_type", "public")

        backup_options = {
            "catering": {
                "corporate": ["Backup Premium Catering", "Alternative Fine Dining"],
                "public": ["Local Restaurant Catering", "Community Kitchen"],
            },
            "entertainment": {
                "corporate": ["Backup DJ Service", "Live Band"],
                "public": ["Local Musicians", "Community Entertainment"],
            },
            "venue": {
                "corporate": ["Alternative Conference Center", "Hotel Ballroom"],
                "public": ["Community Center Backup", "Outdoor Pavilion"],
            },
        }

        # Get backup options for vendor type and event type
        backups = backup_options.get(vendor_type, {}).get(
            event_type, ["Generic Backup"]
        )

        print(f"   ✓ Found {len(backups)} backup options for {vendor_type}")

        return {
            "status": "recovered",
            "action": "backup_found",
            "backup_options": backups,
            "selected_backup": backups[0] if backups else None,
            "vendor_type": vendor_type,
        }

    def _reduce_scope(
        self, context: Dict[str, Any], details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Reduce event scope to fit constraints.

        Args:
            context: Current workflow context
            details: Disruption details

        Returns:
            Recovery results
        """
        print("   📉 Reducing event scope...")

        original_budget = context.get("budget", 10000)
        budget_cut = details.get("amount", original_budget * 0.2)
        new_budget = original_budget - budget_cut

        # Calculate reduction strategies
        reductions = []

        # Reduce catering cost per person
        if context.get("attendee_count", 0) > 0:
            reduction = {
                "area": "catering",
                "action": "Switch to simpler menu",
                "savings": budget_cut * 0.5,
            }
            reductions.append(reduction)

        # Reduce entertainment
        reduction = {
            "area": "entertainment",
            "action": "Switch to DJ instead of live band",
            "savings": budget_cut * 0.3,
        }
        reductions.append(reduction)

        # Reduce venue amenities
        reduction = {
            "area": "venue",
            "action": "Reduce premium amenities",
            "savings": budget_cut * 0.2,
        }
        reductions.append(reduction)

        print(f"   ✓ Identified {len(reductions)} cost reduction strategies")

        return {
            "status": "recovered",
            "action": "scope_reduced",
            "original_budget": original_budget,
            "new_budget": new_budget,
            "reductions": reductions,
            "total_savings": sum(r["savings"] for r in reductions),
        }

    def _replan(
        self, context: Dict[str, Any], details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Trigger complete replanning.

        Args:
            context: Current workflow context
            details: Disruption details

        Returns:
            Recovery results
        """
        print("   🔄 Initiating complete replan...")

        reason = details.get("reason", "Unknown disruption")

        # Create replanning strategy
        replan_steps = []

        if "weather" in reason.lower():
            replan_steps.extend(
                [
                    "Evaluate indoor venue options",
                    "Adjust timeline for new date",
                    "Confirm vendor availability for new date",
                ]
            )
        elif "capacity" in reason.lower():
            replan_steps.extend(
                [
                    "Find larger venue",
                    "Adjust catering quantities",
                    "Recalculate budget for increased capacity",
                ]
            )
        else:
            replan_steps.extend(
                [
                    "Review all vendor commitments",
                    "Re-evaluate venue suitability",
                    "Adjust timeline and budget",
                ]
            )

        print(f"   ✓ Created replan with {len(replan_steps)} steps")

        return {
            "status": "replanning",
            "action": "replan_initiated",
            "reason": reason,
            "replan_steps": replan_steps,
            "requires_approval": True,
        }

    def _escalate(
        self, context: Dict[str, Any], details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Escalate issue to human decision maker.

        Args:
            context: Current workflow context
            details: Disruption details

        Returns:
            Recovery results
        """
        print("   ⬆️  Escalating to decision maker...")

        issue = details.get("issue", "Unspecified disruption")

        escalation_info = {
            "status": "escalated",
            "action": "awaiting_human_decision",
            "issue": issue,
            "context_summary": {
                "event_type": context.get("event_type"),
                "budget": context.get("budget"),
                "attendees": context.get("attendee_count"),
            },
            "recommendations": [
                "Review alternative options",
                "Consider postponement",
                "Evaluate risk acceptance",
            ],
        }

        print(f"   ✓ Escalation package prepared")

        return escalation_info

    def _accept_risk(
        self, context: Dict[str, Any], details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Accept risk and proceed with mitigation.

        Args:
            context: Current workflow context
            details: Disruption details

        Returns:
            Recovery results
        """
        print("   ✔️  Accepting risk with mitigation...")

        risk = details.get("risk", "Unspecified risk")

        mitigation_plan = {
            "status": "risk_accepted",
            "action": "proceeding_with_mitigation",
            "risk": risk,
            "mitigation_measures": [
                "Document risk acceptance",
                "Prepare contingency resources",
                "Monitor situation closely",
                "Establish escalation threshold",
            ],
            "monitoring_required": True,
        }

        print(
            f"   ✓ Risk accepted with {len(mitigation_plan['mitigation_measures'])} mitigation measures"
        )

        return mitigation_plan

    def create_recovery_workflow(
        self, disruption_type: DisruptionType
    ) -> List[WorkflowNode]:
        """
        Create a recovery workflow for a specific disruption type.

        Args:
            disruption_type: Type of disruption

        Returns:
            List of workflow nodes for recovery
        """
        strategy = self.recovery_strategies.get(
            disruption_type, RecoveryStrategy.ESCALATE
        )

        nodes = []

        # Error detection node
        detect_node = WorkflowNode(
            node_id="detect_error",
            node_type=NodeType.ERROR_HANDLER,
            name="Detect Disruption",
            description=f"Detect and classify {disruption_type.value}",
            next_node_id="assess_impact",
        )
        nodes.append(detect_node)

        # Impact assessment node
        assess_node = WorkflowNode(
            node_id="assess_impact",
            node_type=NodeType.SEQUENTIAL,
            name="Assess Impact",
            description="Evaluate disruption impact",
            next_node_id="select_strategy",
        )
        nodes.append(assess_node)

        # Strategy selection node
        strategy_node = WorkflowNode(
            node_id="select_strategy",
            node_type=NodeType.DECISION,
            name="Select Recovery Strategy",
            description=f"Choose {strategy.value} strategy",
            conditions={f"strategy == '{strategy.value}'": "execute_recovery"},
            next_node_id="execute_recovery",
        )
        nodes.append(strategy_node)

        # Recovery execution node
        recovery_node = WorkflowNode(
            node_id="execute_recovery",
            node_type=NodeType.SEQUENTIAL,
            name="Execute Recovery",
            description=f"Execute {strategy.value}",
            action=strategy.value,
            next_node_id="validate_recovery",
        )
        nodes.append(recovery_node)

        # Validation node
        validate_node = WorkflowNode(
            node_id="validate_recovery",
            node_type=NodeType.SEQUENTIAL,
            name="Validate Recovery",
            description="Validate recovery was successful",
            next_node_id=None,  # End of recovery workflow
        )
        nodes.append(validate_node)

        return nodes

    def get_disruption_summary(self) -> Dict[str, Any]:
        """
        Get summary of all disruptions handled.

        Returns:
            Summary dictionary
        """
        if not self.disruption_log:
            return {
                "total_disruptions": 0,
                "disruption_types": {},
                "recovery_strategies_used": {},
            }

        # Count disruption types
        disruption_counts: Dict[str, int] = {}
        for record in self.disruption_log:
            dtype = record["type"]
            disruption_counts[dtype] = disruption_counts.get(dtype, 0) + 1

        # Count recovery strategies
        strategy_counts: Dict[str, int] = {}
        for dtype_str, count in disruption_counts.items():
            try:
                dtype = DisruptionType(dtype_str)
                strategy = self.recovery_strategies.get(dtype)
                if strategy:
                    sname = strategy.value
                    strategy_counts[sname] = strategy_counts.get(sname, 0) + count
            except:
                pass

        return {
            "total_disruptions": len(self.disruption_log),
            "disruption_types": disruption_counts,
            "recovery_strategies_used": strategy_counts,
            "latest_disruptions": [
                {"type": r["type"], "details": r["details"]}
                for r in self.disruption_log[-5:]  # Last 5
            ],
        }
