"""
Workflow Modeler - Execute Workflow Designs

This module implements the workflow execution engine.
"""

from typing import Any, Callable, Dict, List, Optional

from models.event_models import NodeType, WorkflowNode


class WorkflowModeler:
    """
    Executes workflow designs
    """

    def __init__(self):
        """Initialize the workflow modeler."""
        self.nodes: Dict[str, WorkflowNode] = {}
        self.actions: Dict[str, Callable] = {}

    def add_node(self, node: WorkflowNode) -> None:
        """
        Add a node to the workflow.

        Args:
            node: The workflow node to add
        """
        self.nodes[node.node_id] = node

    def add_nodes(self, nodes: List[WorkflowNode]) -> None:
        """
        Add multiple nodes to the workflow.

        Args:
            nodes: List of workflow nodes to add
        """
        for node in nodes:
            self.add_node(node)

    def register_action(self, action_name: str, action_func: Callable) -> None:
        """
        Register an action function that can be called by nodes.

        Args:
            action_name: Name of the action
            action_func: Function to execute for this action
        """
        self.actions[action_name] = action_func

    def execute_workflow(
        self, entry_node_id: str, context: Dict[str, Any], max_iterations: int = 100
    ) -> Dict[str, Any]:
        """
        Execute a workflow starting from the entry node.

        Args:
            entry_node_id: ID of the node to start execution
            context: Initial execution context
            max_iterations: Maximum number of nodes to execute (prevents infinite loops)

        Returns:
            Final execution context with results
        """
        self.current_context = context.copy()
        self.execution_history = []
        current_node_id = entry_node_id
        iterations = 0

        print(f"\n🚀 Starting workflow execution from node: {entry_node_id}")

        while current_node_id and iterations < max_iterations:
            iterations += 1

            if current_node_id not in self.nodes:
                error_msg = f"Node {current_node_id} not found in workflow"
                print(f"❌ Error: {error_msg}")
                self.current_context["error"] = error_msg
                break

            current_node = self.nodes[current_node_id]
            self.execution_history.append(current_node_id)

            print(
                f"\n📍 Executing node: {current_node.name} ({current_node.node_type.value})"
            )

            try:
                # Execute based on node type
                if current_node.node_type == NodeType.SEQUENTIAL:
                    current_node_id = self._execute_sequential_node(current_node)

                elif current_node.node_type == NodeType.CONDITIONAL:
                    current_node_id = self._execute_conditional_node(current_node)

                elif current_node.node_type == NodeType.PARALLEL:
                    current_node_id = self._execute_parallel_node(current_node)

                elif current_node.node_type == NodeType.DECISION:
                    current_node_id = self._execute_decision_node(current_node)

                elif current_node.node_type == NodeType.ERROR_HANDLER:
                    current_node_id = self._execute_error_handler_node(current_node)

                else:
                    print(f"⚠️  Unknown node type: {current_node.node_type}")
                    current_node_id = current_node.next_node_id

            except Exception as e:
                error_msg = f"Error executing node {current_node_id}: {str(e)}"
                print(f"❌ {error_msg}")
                self.current_context["error"] = error_msg

                # Try to use error handler if available
                if current_node.error_handler_id:
                    current_node_id = current_node.error_handler_id
                else:
                    break

        if iterations >= max_iterations:
            print(f"⚠️  Workflow stopped: maximum iterations ({max_iterations}) reached")
            self.current_context["warning"] = "Maximum iterations reached"

        print("\n✅ Workflow execution completed")
        print(f"📊 Nodes executed: {len(self.execution_history)}")
        print(f"🛤️  Execution path: {' → '.join(self.execution_history)}")

        return self.current_context

    def _execute_sequential_node(self, node: WorkflowNode) -> Optional[str]:
        """
        Execute a sequential node - perform action and move to next.

        Args:
            node: The node to execute

        Returns:
            ID of the next node to execute
        """
        if node.action:
            self._execute_action(node.action)

        return node.next_node_id

    def _execute_conditional_node(self, node: WorkflowNode) -> Optional[str]:
        """
        Execute a conditional node - evaluate condition and branch.

        Args:
            node: The node to execute

        Returns:
            ID of the next node based on condition evaluation
        """
        if node.action:
            self._execute_action(node.action)

        # Evaluate conditions to determine next node
        for condition_key, next_node_id in node.conditions.items():
            if self._evaluate_condition(condition_key):
                print(f"  ✓ Condition '{condition_key}' evaluated to True")
                return next_node_id

        # Default to next_node_id if no conditions match
        print("  → Using default path (no conditions matched)")
        return node.next_node_id

    def _execute_parallel_node(self, node: WorkflowNode) -> Optional[str]:
        """
        Execute a parallel node - execute multiple nodes concurrently.

        Note: This is a simplified implementation that executes sequentially
        but could be extended to use threads/async for true parallelism.

        Args:
            node: The node to execute

        Returns:
            ID of the next node after parallel execution
        """
        print(f"  🔀 Executing {len(node.parallel_nodes)} nodes in parallel")

        results = []
        for parallel_node_id in node.parallel_nodes:
            if parallel_node_id in self.nodes:
                parallel_node = self.nodes[parallel_node_id]
                print(f"    ⚡ Executing: {parallel_node.name}")

                if parallel_node.action:
                    result = self._execute_action(parallel_node.action)
                    results.append(result)
            else:
                print(f"    ⚠️  Parallel node {parallel_node_id} not found")

        # Store parallel execution results
        self.current_context["parallel_results"] = results

        return node.next_node_id

    def _execute_decision_node(self, node: WorkflowNode) -> Optional[str]:
        """
        Execute a decision node - make a routing decision based on context.

        Args:
            node: The node to execute

        Returns:
            ID of the next node based on decision logic
        """
        if node.action:
            self._execute_action(node.action)

        # Decision nodes use conditions similar to conditional nodes
        # but are typically more complex business logic decisions
        for condition_key, next_node_id in node.conditions.items():
            if self._evaluate_condition(condition_key):
                print(f"  🎯 Decision: '{condition_key}' -> {next_node_id}")
                return next_node_id

        print("  → Using default decision path")
        return node.next_node_id

    def _execute_error_handler_node(self, node: WorkflowNode) -> Optional[str]:
        """
        Execute an error handler node - handle errors and determine recovery.

        Args:
            node: The node to execute

        Returns:
            ID of the next node after error handling
        """
        print(
            f"  🔧 Handling error: {self.current_context.get('error', 'Unknown error')}"
        )

        if node.action:
            self._execute_action(node.action)

        # Clear error if handled successfully
        if "error" in self.current_context:
            self.current_context["last_error"] = self.current_context.pop("error")
            print("  ✓ Error handled successfully")

        return node.next_node_id

    def _execute_action(self, action_name: str) -> Any:
        """
        Execute a registered action function.

        Args:
            action_name: Name of the action to execute

        Returns:
            Result of the action execution
        """
        if action_name in self.actions:
            action_func = self.actions[action_name]
            print(f"  ▶️  Executing action: {action_name}")

            try:
                result = action_func(self.current_context)
                return result
            except Exception as e:
                error_msg = f"Action '{action_name}' failed: {str(e)}"
                print(f"  ❌ {error_msg}")
                self.current_context["error"] = error_msg
                raise
        else:
            print(f"  ⚠️  Action '{action_name}' not registered")
            return None

    def _evaluate_condition(self, condition: str) -> bool:
        """
        Evaluate a condition string against the current context.

        Supports simple conditions like:
        - "event_type == 'corporate'"
        - "budget > 10000"
        - "attendee_count >= 100"

        Args:
            condition: Condition string to evaluate

        Returns:
            True if condition is met, False otherwise
        """
        try:
            # Simple condition evaluation
            # In production, use a proper expression evaluator
            if "==" in condition:
                key, value = [s.strip().strip("'\"") for s in condition.split("==")]
                return str(self.current_context.get(key, "")).lower() == value.lower()

            elif ">" in condition:
                key, value = condition.split(">")
                return float(self.current_context.get(key.strip(), 0)) > float(
                    value.strip()
                )

            elif "<" in condition:
                key, value = condition.split("<")
                return float(self.current_context.get(key.strip(), 0)) < float(
                    value.strip()
                )

            elif ">=" in condition:
                key, value = condition.split(">=")
                return float(self.current_context.get(key.strip(), 0)) >= float(
                    value.strip()
                )

            elif "<=" in condition:
                key, value = condition.split("<=")
                return float(self.current_context.get(key.strip(), 0)) <= float(
                    value.strip()
                )

            elif condition in self.current_context:
                # Boolean condition - check if key exists and is truthy
                return bool(self.current_context[condition])

            else:
                print(f"  ⚠️  Could not evaluate condition: {condition}")
                return False

        except Exception as e:
            print(f"  ⚠️  Error evaluating condition '{condition}': {str(e)}")
            return False

    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the last workflow execution.

        Returns:
            Dictionary with execution statistics
        """
        return {
            "nodes_executed": len(self.execution_history),
            "execution_path": self.execution_history,
            "final_context": self.current_context,
            "has_error": "error" in self.current_context,
        }

    def visualize_workflow(self) -> str:
        """
        Generate a text-based visualization of the workflow structure.

        Returns:
            String representation of the workflow
        """
        if not self.nodes:
            return "Empty workflow - no nodes defined"

        output = ["\n" + "=" * 60]
        output.append("WORKFLOW STRUCTURE")
        output.append("=" * 60 + "\n")

        for node_id, node in self.nodes.items():
            output.append(f"📦 {node.name} ({node.node_id})")
            output.append(f"   Type: {node.node_type.value}")

            if node.action:
                output.append(f"   Action: {node.action}")

            if node.conditions:
                output.append("   Conditions:")
                for cond, next_id in node.conditions.items():
                    output.append(f"      • {cond} → {next_id}")

            if node.parallel_nodes:
                output.append(f"   Parallel nodes: {', '.join(node.parallel_nodes)}")

            if node.next_node_id:
                output.append(f"   Next: {node.next_node_id}")

            if node.error_handler_id:
                output.append(f"   Error handler: {node.error_handler_id}")

            output.append("")

        output.append("=" * 60 + "\n")

        return "\n".join(output)
