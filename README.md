# Aython: Your AI-Powered Python Assistant in IPython

Aython is an IPython extension that brings the power of large language models (LLMs) directly into your interactive Python sessions. Generate functions, get coding assistance, and streamline your workflow without ever leaving your terminal.

## Installation

1.  **Install from PyPI (once published):**

    ```bash
    pip install aython
    ```

2.  **Or, install directly from the source for development:**

    ```bash
    pip install -e .
    ```

## Usage

1.  **Load the extension in your IPython session:**

    ```ipython
    %load_ext aython
    ```

2.  **Set your desired LLM:**

    Aython uses `litellm` to connect to various LLM providers. Set your model by specifying the model name.

    ```ipython
    %set_model claude-3-opus-20240229
    ```

    Or for OpenAI:

    ```ipython
    %set_model gpt-4-turbo
    ```

    Or for Gemini:
    ```ipython
    %set_model gemini/gemini-2.0-flash-exp
    ```

    *Note: Ensure you have the necessary API keys (e.g., `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`) set as environment variables.*

3.  **Generate code with the `%code` magic:**

    Describe the function you want to create, and Aython will generate it, display it for review, and load it directly into your IPython session.

    ```ipython
    %code create a function that takes a list of numbers and returns the sum of squares
    ```

    After running the command, the generated function (e.g., `sum_of_squares`) will be available for you to use immediately.

    ```ipython
    my_list = [1, 2, 3]
    sum_of_squares(my_list)  # Output: 14
    ```

## How It Works

-   `%load_ext aython`: Loads the magic commands into your IPython environment.
-   `%set_model <model_name>`: Sets the model to be used by `litellm`.
-   `%code <description>`: Takes your natural language description, sends it to the configured LLM to generate Python code, displays the code for you, and then executes it in the current session, making the new function or class immediately available.
