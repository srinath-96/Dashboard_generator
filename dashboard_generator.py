import os
import pandas as pd
import argparse
import sys
from smolagents import OpenAIServerModel, CodeAgent,HfApiModel
from dotenv import load_dotenv
import traceback
import textwrap # Keep for potential future use if needed

load_dotenv()

class DashboardGenerator:
    """
    A tool for generating Dash dashboards from datasets using SmolagentS.
    The tool analyzes datasets to identify important features and creates
    interactive dashboards based on user specifications.
    Saves the generated code to a file.
    """

    def __init__(self, api_key):
        """
        Initialize the dashboard generator with the API key.

        Args:
            api_key: Gemini API key for the LiteLLM model
        """
        self.api_key = api_key
        os.environ["GEMINI_API_KEY"] = api_key
        try:
            self.model = OpenAIServerModel(
                model_id="models/gemini-2.0-flash", # Using the model specified in the provided code
                api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
                api_key=api_key,
            )
            #self.model=HfApiModel(token=api_key)
            print("AI Model Initialized.")
        except Exception as e:
            print(f"Error initializing the AI model: {e}", file=sys.stderr)
            sys.exit(1)


        # --- Base prompt template ---
        # Keep the placeholder {dataset_path} here
        self.base_prompt_template ="""You are an expert Python developer specializing in creating runnable data visualization scripts using Plotly and Dash.

**Core Task:** Generate a **single, complete, and directly runnable Python script** (`.py` file) that creates an interactive Dash dashboard based on the provided user requirements and dataset path.

**Input Context:**
-   **User Requirements:** You will be given specific features and analyses the user wants in the dashboard ({user_requirements}).
-   **Dataset Path:** You will be given the exact file path to the CSV dataset ({dataset_path}).

**Generated Script Requirements:**
1.  **Imports:** Start the script *only* with these exact imports:
    ```python
    import dash
    from dash import dcc, html, Input, Output, dash_table
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    import numpy as np
    import os # Add os import for potential path handling if needed by generated code itself
    ```
2.  **Data Loading:** Immediately after the imports, the script MUST load the dataset using pandas with the *exact* path provided. Use this line:
    ```python
    # Load the dataset
    df = pd.read_csv(r'{dataset_path}') # Use raw string literal r'' for path compatibility
    ```
    *(Ensure you replace {dataset_path} with the actual path provided during formatting).*
3.  **Data Preprocessing:** After loading `df`, include necessary data cleaning and preprocessing steps (e.g., handling NaNs, converting data types like dates using `pd.to_datetime(df['col'], errors='coerce')`, converting numeric types using `pd.to_numeric(df['col'], errors='coerce')`). Base this on your analysis of the data structure and the user requirements.
4.  **Dash App Initialization:** Initialize the Dash app correctly:
    ```python
    app = dash.Dash(__name__)
    server = app.server # Include for deployment compatibility
    ```
5.  **Layout (`app.layout`):**
    -   Define the dashboard structure using `html.Div`, `html.H1`, `html.P`, etc.
    -   Implement filters (e.g., `dcc.Dropdown`, `dcc.Slider`) based on relevant columns identified in the data and user requirements. Populate dropdown options dynamically from the loaded `df`.
    -   Include `dcc.Graph` components with unique IDs for displaying visualizations.
6.  **Callbacks (`@app.callback`):**
    -   Create functions decorated with `@app.callback` linking `Input` (from filters) to `Output` (graph `figure` properties).
    -   Inside callbacks, filter the main DataFrame `df` based on input values.
    -   Generate Plotly figures (`px...`, `go.Figure...`) using the *filtered* data.
    -   Return the figures to the corresponding `Output`. Handle cases gracefully where filtering results in no data (e.g., return `go.Figure()` with an informative annotation).
7.  **Run Block:** The script MUST conclude with the standard Python execution block:
    ```python
    if __name__ == '__main__':
        app.run(debug=True)
    ```

**User Requirements:**
{user_requirements}

**Output Format Constraints:**
-   **CRITICAL:** Your entire response MUST be **ONLY** the Python code for the script.
-   **DO NOT** include *any* introductory text, explanations, comments *outside* the code, apologies, or markdown formatting (like ```python ... ```).
-   The generated code must be syntactically correct and ready to be saved directly as a `.py` file and executed.
-   Ensure the `pd.read_csv()` line uses the exact `{dataset_path}` provided, preferably within a raw string `r'...'`.
""" # End of optimized base_prompt_template

        # Create the dashboard agent
        self.dashboard_agent = CodeAgent(
            tools=[],
            model=self.model,
            additional_authorized_imports=[
                "numpy",
                "pandas",
                "dash",
                "dash.dependencies",
                "plotly.express",
                "plotly.graph_objects",
                "dash_table"
            ],
        )

    def generate_dashboard(self, dataset_path, user_requirements):
        """
        Generate a Dash dashboard for the given dataset based on user requirements.

        Args:
            dataset_path: Path to the dataset file
            user_requirements: Specific requirements from the user for the dashboard

        Returns:
            String containing the generated dashboard code or None on error.
        """
        try:
            # Load the dataset to provide context to the agent
            print(f"Loading dataset from '{dataset_path}' for analysis...")
            df = pd.read_csv(dataset_path)
            print("Dataset loaded successfully for analysis.")
        except FileNotFoundError:
            print(f"Error: Dataset file not found at '{dataset_path}'", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Error loading dataset '{dataset_path}': {e}", file=sys.stderr)
            traceback.print_exc()
            return None

        print("Formatting prompt...")
        # Format the prompt HERE, inserting the actual dataset path
        # Escape backslashes in path for correct string representation in the prompt
        safe_dataset_path = dataset_path.replace('\\', '\\\\')
        try:
            prompt = self.base_prompt_template.format(
                user_requirements=user_requirements,
                dataset_path=safe_dataset_path  # Inject the path here
            )
        except KeyError as e:
             print(f"Error formatting prompt: Missing key {e}. Check base_prompt_template.", file=sys.stderr)
             return None


        print("Running AI agent to generate dashboard code (this may take some time)...")
        try:
            # Run the agent with the fully formatted prompt and the dataframe for context
            response = self.dashboard_agent.run(prompt, additional_args={"dataset": df})
            print("AI agent finished.")

             # Basic check if the response looks like code
            if isinstance(response, str) and "import dash" in response:
                 # Clean up potential markdown backticks or leading 'python'
                cleaned_response = response.strip().strip('`').strip()
                if cleaned_response.startswith("python"):
                     cleaned_response = cleaned_response[len("python"):].lstrip()
                # Ensure the required if __name__ == '__main__' block exists
                if "if __name__ == '__main__':" not in cleaned_response:
                    print("Warning: Generated code missing `if __name__ == '__main__':` block. Appending a default.", file=sys.stderr)
                    cleaned_response += "\n\n# --- Main execution block ---\n"
                    cleaned_response += "if __name__ == '__main__':\n"
                    cleaned_response += "    # Make sure data loading is handled above if running standalone\n"
                    cleaned_response += "    app.run(debug=True)\n"

                return cleaned_response
            else:
                print(f"Error: Agent returned unexpected response type or content: {type(response)}", file=sys.stderr)
                print(f"Response received (first 500 chars):\n{str(response)[:500]}", file=sys.stderr)
                return None

        except Exception as e:
            print(f"Error during AI agent execution: {e}", file=sys.stderr)
            traceback.print_exc()
            return None

    def save_dashboard(self, code, output_path):
        """
        Save the generated dashboard code to a file.

        Args:
            code: The dashboard code to save
            output_path: Path where the code should be saved
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(code)
            print(f"Dashboard code saved to {output_path}")
        except Exception as e:
             print(f"Error saving dashboard code to '{output_path}': {e}", file=sys.stderr)
             traceback.print_exc()


# --- Main Execution Block ---
def main():
    parser = argparse.ArgumentParser(description="Generate a Dash dashboard script.")
    parser.add_argument("dataset_path", help="Path to the input CSV dataset file.")
    parser.add_argument("user_prompt", help="Text prompt describing the desired dashboard.")
    # Output filename is kept hardcoded as videogame_dashboard.py
    output_filename = "videogame_dashboard.py"
    args = parser.parse_args()

    # --- Get API Key ---
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: Gemini API Key not found.", file=sys.stderr)
        print("Please set the GEMINI_API_KEY environment variable or create a .env file with it.", file=sys.stderr)
        sys.exit(1)

    # --- Initialize and Generate ---
    print("Initializing Dashboard Generator...")
    dashboard_gen = DashboardGenerator(api_key)

    # The generate_dashboard method now needs the dataset path to format the prompt *and* load data for context
    dashboard_code = dashboard_gen.generate_dashboard(args.dataset_path, args.user_prompt)

    # --- Save ---
    if dashboard_code:
        # Save the dashboard code using the instance method
        dashboard_gen.save_dashboard(dashboard_code, output_filename)
        print(f"\nDashboard script generated successfully as '{output_filename}'.")
        # No runner instruction needed as per user request focus
    else:
        print("\nFailed to generate dashboard code.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()