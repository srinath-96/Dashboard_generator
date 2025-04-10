# AI-Powered Dash Dashboard Generator

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

This project uses an AI model (specifically Google's Gemini via `smolagents`) to automatically generate Python code for interactive Dash dashboards based on a provided CSV dataset and a natural language prompt.

## Overview

The core script, `dash_generator.py`, takes two main inputs:
1.  The path to a CSV dataset.
2.  A text prompt describing the desired dashboard features and visualizations.

It then:
1.  Loads the dataset to provide context for the AI.
2.  Constructs a detailed prompt instructing the AI on how to generate a runnable Dash application script.
3.  Uses the `smolagents` library to interact with the configured Gemini model.
4.  Receives the generated Python code from the AI.
5.  Cleans up the code slightly and adds informative header comments.
6.  Saves the final code as a `.py` file (defaulting to `videogame_dashboard.py`, but configurable).

The generated `.py` file is designed to be run directly using `python <generated_script_name.py>` to launch the Dash dashboard locally.

## Features

*   Generates Dash dashboard code automatically from prompts.
*   Uses AI (Gemini model via `smolagents`) for code generation.
*   Command-line interface for specifying dataset and prompt.
*   Configurable output filename.
*   Generated scripts include data loading, preprocessing hints, layout, callbacks, and the run command.

## Prerequisites

*   Python 3.8+
*   pip (Python package installer)
*   Access to Google AI Studio or Vertex AI for a Gemini API Key.

## Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/srinath-96/Dashboard_generator/
    cd Dashboard_generator
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv .venv
    # Activate the environment
    # On macOS/Linux:
    source .venv/bin/activate
    # On Windows (Command Prompt):
    # .venv\Scripts\activate.bat
    # On Windows (PowerShell):
    # .venv\Scripts\Activate.ps1
    ```

3.  **Install Dependencies:**
    Create a `requirements.txt` file with the following content:
    ```txt
    # requirements.txt
    dash
    plotly
    pandas
    smolagents
    google-generativeai
    python-dotenv
    numpy
    ```
    Then install them:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Key:**
    *   Create a file named `.env` in the root directory of the project.
    *   Add your Gemini API key to this file:
        ```env
        # .env
        GEMINI_API_KEY="Your-Actual-API-Key-Here"
        ```
    *   **Important:** Replace `"Your-Actual-API-Key-Here"` with your actual key. Make sure this `.env` file is listed in your `.gitignore` file to avoid committing your key.

## Usage

Run the `dash_generator.py` script from your terminal, providing the path to your dataset and your prompt.

**Syntax:**

```bash
python dash_generator.py <path_to_dataset.csv> "<your_dashboard_prompt>" [-o <output_filename.py>]
