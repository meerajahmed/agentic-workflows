# agentic-workflows
Agentic Workflows with Google ADK

## Setup

### Prerequisites
- Python 3.9 or higher (recommended)
- Pip (Python package installer)

### Environment Configuration

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd agentic-workflows
   ```

2. **Create and activate a virtual environment:**
   - For macOS/Linux:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - For Windows:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\activate
     ```

3. **Upgrade pip and install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the root directory to store your configuration (e.g., Google API keys).
   ```text
   # Example .env content
   GOOGLE_API_KEY=your_api_key_here
   ```

## Getting Started

To run the workflow analysis example:
```bash
python3 ./1-workflow-analysis/main.py
```
