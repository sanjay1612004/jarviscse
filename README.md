# Jarvis AI Assistant

This is a Python-based AI assistant project.

## Installation

1.  **Install Python**: Make sure you have Python installed on your system.
2.  **Install Dependencies**: Open your terminal or command prompt in this folder and run the following command to install all necessary libraries:

    ```bash
    pip install -r requirements.txt
    ```

    *Note: If you encounter issues installing `pyaudio`, you might need to install it manually using a `.whl` file or use `pipwin install pyaudio`.*

## How to Run

1.  **Run the Assistant**: To start the AI assistant, run the following command in your terminal:

    ```bash
    python Speech2.py
    ```

2.  **Using the Assistant**:
    *   The assistant will welcome you.
    *   Say **"Jarvis"** to activate it.
    *   Speak your commands (e.g., "Play [song name]", "Who is [person]", "Open Chrome", "Tell me a joke").

## Troubleshooting

*   **Microphone Issues**: Ensure your microphone is connected and working.
*   **API Keys**: Some features (like Gemini or News) require API keys. Make sure they are correctly set up in the code if needed.
