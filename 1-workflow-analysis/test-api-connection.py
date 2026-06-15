import logging
import os
import sys

import vertexai
from dotenv import load_dotenv
from google import genai
from google.adk.agents import LlmAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_connection():
    """
    Tests the connection to Vertex AI and Google GenAI (Agent Platform).
    """
    load_dotenv()

    project_id = os.getenv("PROJECT_ID")
    location = os.getenv("LOCATION", "us-central1")

    if not project_id:
        print("Error: PROJECT_ID is not set in .env file.")
        sys.exit(1)

    print(f"--- Testing Connection to Project: {project_id} ---")

    try:
        # Test 1: Vertex AI Initialization
        print(f"Checking Vertex AI initialization ({location})...")
        vertexai.init(project=project_id, location=location)
        print("✅ Vertex AI initialized successfully.")

        # Test 2: GenAI Client Creation and Model Generation
        print("Testing model generation (Agent Platform API)...")
        client = genai.Client(vertexai=True, project=project_id, location=location)

        # We use a very small request to verify the specific 'generate_content'
        # endpoint which is used by the Agent Platform APIs.

        llm_agent = LlmAgent(
            name="task_analyzer",
            model="gemini-2.5-flash",
            instruction="You are a helpful chat agent",
        )

        response = client.models.generate_content(
            model=llm_agent.model,
            contents=f"{llm_agent.instruction}\n\nSay 'Connection Successful'"
        )

        print("response - >", response)

        # response = client.models.generate_content(
        #    model="gemini-2.5-flash",
        #    contents="Say 'Connection Successful'"
        # )

        print(f"✅ Model response: {response.text}")
        print("\nSUCCESS: The Agent Platform API is reachable and functional.")

    except Exception as e:
        print("\nFAILURE: Could not connect to the Agent Platform API.")
        print(f"Error Details: {e}")
        if "403" in str(e):
            print(
                "\nSUGGESTION: This error usually means the 'Agent Platform API' is disabled."
            )
            print(
                f"Enable it here: https://console.developers.google.com/apis/api/aiplatform.googleapis.com/overview?project={project_id}"
            )
        sys.exit(1)


if __name__ == "__main__":
    test_connection()
