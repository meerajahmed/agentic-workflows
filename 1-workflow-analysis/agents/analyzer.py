import hashlib
import json
import logging
import re

import vertexai
from google import genai
from google.adk.agents import LlmAgent
from utils.workflow import AnalysisResult, TaskComponent, TaskRequest

logger = logging.getLogger(__name__)


def clean_json_string(raw_str: str) -> str:
    """Extracts JSON from markdown blocks if present."""
    # Try to find content inside triple backticks first (e.g., ```json ... ``` or ``` ... ```)
    json_block_match = re.search(r"```(?:json)?\s*(.*?)\s*```", raw_str, re.DOTALL)
    if json_block_match:
        content = json_block_match.group(1).strip()
    else:
        match = re.search(r"(\{.*\})", raw_str, re.DOTALL)
        content = match.group(1).strip() if match else None

    return content


class TaskAnalyzer:
    """
    Agent responsible for analyzing and decomposing complex tasks.

    Pattern: LLM-based intelligent analysis with rule based fallback
    """

    def __init__(self, project_id: str):
        """
        Initialize the Task Analyzer agent with ADK.
        """
        self.project_id = project_id
        self.client = None
        self.llm_agent = None

        try:
            # Task 1a: Initialize Vertex AI
            vertexai.init(project=project_id, location="us-central1")

            # Task 1b: Create genai client
            self.client = genai.Client(
                vertexai=True, project=project_id, location="us-central1"
            )

            if self.client is None:
                raise RuntimeError("Failed to create genai.Client")

            # Task 1c: Create LLMAgent
            self.llm_agent = LlmAgent(
                name="task_analyzer",
                model="gemini-2.5-flash",
                instruction="You are an expert task analysis agent that breaks down complex task into manageable components with clear dependencies and resource requirements.",
            )

            if self.llm_agent is None:
                raise RuntimeError("Failed to create LlmAgent")

        except Exception as e:
            logger.error(f"Critical failure during TaskAnalyzer initialization: {e}")
            raise RuntimeError(f"TaskAnalyzer could not be initialized: {e}") from e

        logger.info("TaskAnalyzer initialized")

    def analyze_task(self, task_request: TaskRequest) -> AnalysisResult:
        """
        Analyze complex task and break it down into manageable components.

        Args:
            task_request: The task to analyze

        Returns:
            AnalysisResult: Structured analysis with components and dependencies
        """

        return self._analyze_with_adk(task_request)

    def _analyze_with_adk(self, task_request: TaskRequest) -> AnalysisResult:
        """
        Use ADK LLMAgent to perform intelligence task analysis.
        """

        analysis_prompt = f"""
        Analyse the following task and break it down into manageable components:

        Task: {task_request.description}
        Complexity Level: {task_request.complexity_level}
        Deadline: {task_request.deadline_days} days
        Resource Constraints: {task_request.resource_constraints}
        Stakeholders: {", ".join(task_request.stakeholders) if task_request.stakeholders else "Not specified"}

        Please provide a structures analysis with:
        1. 3-7 main components/phases with specific names and descriptions
        2. Estimated hours for each component (8-40 hours range)
        3. Required skills for each component
        4. Dependencies between components
        5. Overall complexity score (0.0 - 1.0)
        6. 2-4 potential risks or challenges
        7. Key assumptions being made

        Format your response as JSON with this structure
        {{
            "components" : [
                {{
                    "name": "Component Name",
                    "description": "Detailed description",
                    "estimated_hours": 16,
                    "required_skills": ["skill1", "skill2"],
                    "dependencies": ["component_name"]
                }}
            ],
            "complexity_score": 0.7,
            "risk_factors": ["risk1", "risk2"],
            "assumptions": ["assumption1", "assumption2"]
        }}
        """

        if self.llm_agent is None:
            raise RuntimeError("LLM Agent was not initialized correctly.")

        try:
            # Directly using the genai client as ADK context setup is missing for this standalone script
            response = self.client.models.generate_content(
                model=self.llm_agent.model,
                contents=f"{self.llm_agent.instruction}\n\n{analysis_prompt}",
            )

            print("response: ", response)

            # The response object from google-genai has a .text property for the main content
            cleaned_content = clean_json_string(response.text)
            if cleaned_content is None:
                logger.error(f"Could not extract JSON from model response: {response.text}")
                raise RuntimeError("Model response did not contain valid JSON structure.")
            
            analysis_data = json.loads(cleaned_content)

            print("analysis_data : ", analysis_data)

            # Convert to TaskComponent objects
            components = []
            for comp in analysis_data.get("components", []):
                component = TaskComponent(
                    name=comp.get("name", "Unnamed Component"),
                    description=comp.get("description", "No description provided"),
                    estimated_hours=float(comp.get("estimated_hours", 0)),
                    dependencies=comp.get("dependencies", []),
                    required_skills=comp.get("required_skills", []),
                )
                components.append(component)

            # Build dependencies dictionary
            dependencies = {}

            for comp in components:
                if comp.dependencies:
                    dependencies[comp.name] = comp.dependencies

            task_id_hash = hashlib.md5(task_request.description.encode()).hexdigest()[
                :8
            ]

            return AnalysisResult(
                task_id=f"adk_{task_id_hash}",
                components=components,
                dependencies=dependencies,
                estimated_total_hours=sum(c.estimated_hours for c in components),
                complexity_score=analysis_data.get("complexity_score", 0.5),
                risk_factors=analysis_data.get("risk_factors", []),
                assumptions=analysis_data.get("assumptions", []),
            )

        except Exception as e:
            logger.error(f"ADK analysis failed: {e}")
            raise e
