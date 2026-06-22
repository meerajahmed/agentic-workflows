"""
Advanced State Manager - Workflow State Tracking and Persistence

This module manages workflow state, enabling features like:
- Session tracking
- State persistence
- Checkpoint/restore
- State history

"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from models.event_models import (
    EventRequest,
    StateTransition,
    WorkflowMetrics,
    WorkflowSession,
    WorkflowStatus,
)


class AdvancedStateManager:
    """
    Manages workflow execution state and persistence.
    """

    def __init__(self, persistence_dir: str = "workflow_state"):
        """
        Initialize the state manager.

        Args:
            persistence_dir: Directory for storing workflow state files
        """
        self.persistence_dir = persistence_dir
        self.sessions: Dict[str, WorkflowSession] = {}
        self.metrics: Dict[str, WorkflowMetrics] = {}

        # Create persistence directory if it doesn't exist
        os.makedirs(persistence_dir, exist_ok=True)

    def create_workflow_session(
        self, session_id: str, event_request: EventRequest, entry_node_id: str
    ) -> WorkflowSession:
        """
        Create a new workflow session.

        Args:
            session_id: Unique identifier for the session
            event_request: The event request being processed
            entry_node_id: Starting node for the workflow

        Returns:
            New workflow session
        """
        session = WorkflowSession(
            session_id=session_id,
            event_request=event_request,
            current_node_id=entry_node_id,
            status=WorkflowStatus.PENDING,
        )

        self.sessions[session_id] = session
        print(f"📝 Created workflow session: {session_id}")

        return session

    def start_session(self, session_id: str) -> None:
        """
        Mark a session as started.

        Args:
            session_id: ID of the session to start
        """
        if session_id in self.sessions:
            self.sessions[session_id].status = WorkflowStatus.IN_PROGRESS
            self.sessions[session_id].started_at = datetime.now().isoformat()
            print(f"▶️  Started session: {session_id}")
        else:
            raise ValueError(f"Session {session_id} not found")

    def update_session_state(
        self,
        session_id: str,
        from_node_id: str,
        to_node_id: str,
        condition: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Update session state with a new transition.

        Args:
            session_id: ID of the session
            from_node_id: Node transitioning from
            to_node_id: Node transitioning to
            condition: Condition that triggered the transition (if any)
            context: Additional context data
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        transition = StateTransition(
            from_node_id=from_node_id,
            to_node_id=to_node_id,
            condition=condition,
            context=context or {},
        )

        session.add_transition(transition)

        # Update session context if provided
        if context:
            session.context.update(context)

        print(f"  🔄 State transition: {from_node_id} → {to_node_id}")

    def update_context(self, session_id: str, context_updates: Dict[str, Any]) -> None:
        """
        Update session context with new data.

        Args:
            session_id: ID of the session
            context_updates: Dictionary of context updates
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        self.sessions[session_id].context.update(context_updates)
        self.sessions[session_id].updated_at = datetime.now().isoformat()

    def create_checkpoint(self, session_id: str) -> None:
        """
        Create a checkpoint for the session (for recovery).

        Args:
            session_id: ID of the session
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        session.create_checkpoint()

        print(f"💾 Checkpoint created for session: {session_id}")

        # Persist checkpoint to disk
        self._persist_session(session)

    def restore_from_checkpoint(
        self, session_id: str, checkpoint_index: int = -1
    ) -> Dict[str, Any]:
        """
        Restore session state from a checkpoint.

        Args:
            session_id: ID of the session
            checkpoint_index: Index of checkpoint to restore (-1 for latest)

        Returns:
            Restored context data
        """
        if session_id not in self.sessions:
            # Try to load from disk
            self._load_session(session_id)

        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        if not session.checkpoints:
            raise ValueError(f"No checkpoints available for session {session_id}")

        checkpoint = session.checkpoints[checkpoint_index]

        # Restore state
        session.current_node_id = checkpoint["node_id"]
        session.context = checkpoint["context"].copy()
        session.status = WorkflowStatus.IN_PROGRESS

        print(f"♻️  Restored session {session_id} from checkpoint")
        print(f"   Node: {checkpoint['node_id']}")
        print(f"   Timestamp: {checkpoint['timestamp']}")

        return session.context

    def complete_session(self, session_id: str, success: bool = True) -> None:
        """
        Mark a session as completed.

        Args:
            session_id: ID of the session
            success: Whether the session completed successfully
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        if success:
            session.complete()
            print(f"✅ Session completed: {session_id}")
        else:
            session.status = WorkflowStatus.FAILED
            session.updated_at = datetime.now().isoformat()
            print(f"❌ Session failed: {session_id}")

        # Persist final state
        self._persist_session(session)

    def log_error(self, session_id: str, error: str) -> None:
        """
        Log an error for a session.

        Args:
            session_id: ID of the session
            error: Error message to log
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        self.sessions[session_id].add_error(error)
        print(f"⚠️  Error logged for session {session_id}: {error}")

    def get_session(self, session_id: str) -> Optional[WorkflowSession]:
        """
        Get a workflow session by ID.

        Args:
            session_id: ID of the session

        Returns:
            WorkflowSession if found, None otherwise
        """
        if session_id in self.sessions:
            return self.sessions[session_id]

        # Try to load from disk
        try:
            self._load_session(session_id)
            return self.sessions.get(session_id)
        except:
            return None

    def get_session_history(self, session_id: str) -> List[StateTransition]:
        """
        Get the state transition history for a session.

        Args:
            session_id: ID of the session

        Returns:
            List of state transitions
        """
        session = self.get_session(session_id)
        if session:
            return session.transitions
        return []

    def _persist_session(self, session: WorkflowSession) -> None:
        """
        Persist session state to disk.

        Args:
            session: Session to persist
        """
        filepath = os.path.join(self.persistence_dir, f"{session.session_id}.json")

        try:
            with open(filepath, "w") as f:
                json.dump(session.to_dict(), f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to persist session {session.session_id}: {str(e)}")

    def _load_session(self, session_id: str) -> None:
        """
        Load session state from disk.

        Args:
            session_id: ID of the session to load
        """
        filepath = os.path.join(self.persistence_dir, f"{session_id}.json")

        if not os.path.exists(filepath):
            raise ValueError(f"No persisted session found for {session_id}")

        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            # Reconstruct session from data
            # This is simplified - in production, use proper deserialization
            event_request = EventRequest(**data["event_request"])

            session = WorkflowSession(
                session_id=data["session_id"],
                event_request=event_request,
                current_node_id=data["current_node_id"],
                status=WorkflowStatus(data["status"]),
            )

            session.context = data["context"]
            session.checkpoints = data["checkpoints"]
            session.error_log = data["error_log"]
            session.started_at = data["started_at"]
            session.updated_at = data["updated_at"]
            session.completed_at = data.get("completed_at")

            # Reconstruct transitions
            for t_data in data["transitions"]:
                transition = StateTransition(
                    from_node_id=t_data["from_node_id"],
                    to_node_id=t_data["to_node_id"],
                    condition=t_data.get("condition"),
                    timestamp=t_data["timestamp"],
                    context=t_data.get("context", {}),
                )
                session.transitions.append(transition)

            self.sessions[session_id] = session
            print(f"📂 Loaded session from disk: {session_id}")

        except Exception as e:
            raise ValueError(f"Failed to load session {session_id}: {str(e)}")

    def track_metrics(self, workflow_name: str) -> WorkflowMetrics:
        """
        Get or create metrics tracker for a workflow.

        Args:
            workflow_name: Name of the workflow

        Returns:
            Metrics object for the workflow
        """
        if workflow_name not in self.metrics:
            self.metrics[workflow_name] = WorkflowMetrics(workflow_name=workflow_name)

        return self.metrics[workflow_name]

    def record_execution(
        self,
        workflow_name: str,
        success: bool,
        execution_time: float,
        nodes_executed: List[str],
    ) -> None:
        """
        Record metrics for a workflow execution.

        Args:
            workflow_name: Name of the workflow
            success: Whether execution was successful
            execution_time: Time taken in seconds
            nodes_executed: List of node IDs that were executed
        """
        metrics = self.track_metrics(workflow_name)
        metrics.record_execution(success, execution_time)

        for node_id in nodes_executed:
            metrics.record_node_execution(node_id)

        print(f"📊 Recorded execution metrics for {workflow_name}")

    def get_metrics_summary(self, workflow_name: str) -> Dict[str, Any]:
        """
        Get metrics summary for a workflow.

        Args:
            workflow_name: Name of the workflow

        Returns:
            Dictionary with metrics data
        """
        if workflow_name in self.metrics:
            return self.metrics[workflow_name].to_dict()
        return {}

    def display_session_summary(self, session_id: str) -> None:
        """
        Display a summary of a workflow session.

        Args:
            session_id: ID of the session to display
        """
        session = self.get_session(session_id)

        if not session:
            print(f"❌ Session {session_id} not found")
            return

        print("\n" + "=" * 60)
        print(f"WORKFLOW SESSION SUMMARY: {session_id}")
        print("=" * 60)
        print(f"Status: {session.status.value}")
        print(f"Event: {session.event_request.event_type.value}")
        print(f"Current Node: {session.current_node_id}")
        print(f"Started: {session.started_at}")
        print(f"Updated: {session.updated_at}")

        if session.completed_at:
            print(f"Completed: {session.completed_at}")

        print(f"\nTransitions: {len(session.transitions)}")
        if session.transitions:
            print("\nExecution Path:")
            for i, transition in enumerate(session.transitions, 1):
                cond = f" [{transition.condition}]" if transition.condition else ""
                print(
                    f"  {i}. {transition.from_node_id} → {transition.to_node_id}{cond}"
                )

        if session.error_log:
            print(f"\nErrors: {len(session.error_log)}")
            for error in session.error_log[-3:]:  # Show last 3 errors
                print(f"  • {error}")

        if session.checkpoints:
            print(f"\nCheckpoints: {len(session.checkpoints)}")

        print("=" * 60 + "\n")
