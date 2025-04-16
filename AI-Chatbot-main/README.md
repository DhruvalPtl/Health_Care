# IntelliGemini

**IntelliGemini** is a powerful and interactive chatbot application that utilizes the Gemini language model to generate human-like responses. Built with Streamlit, the app offers a seamless and customizable interface where users can engage in dynamic conversations with an AI model. It supports multiple configuration options to personalize interactions and allows users to download chat history for record-keeping.

## Features

- **Interactive Chat Interface:** Communicate with the Gemini language model in a conversational way. The model responds to user inputs in natural language.
- **Customizable Parameters:** Control the behavior of the language model by adjusting various parameters:
  - **Temperature:** Controls the randomness of the model's responses.
  - **Top-P:** Governs the cumulative probability distribution for token selection.
  - **Top-K:** Limits the model to selecting from the top-k tokens.
  - **Max Output Length:** Specifies the maximum length for the generated responses.
  - **Stop Sequences:** Define stop sequences where the model should stop generating text.
- **File Download:** Download the chat history in both JSON and CSV formats for record-keeping or further analysis.
- **Code Execution Tool:** Enable a feature that allows the model to generate and execute Python code directly within the chat. This is useful for more advanced interactions and allows for code generation or troubleshooting.
- **API Key Management:** Users can enter their own Gemini API key or use the provided key to make requests to the Gemini API. The app is designed to work both for general users and developers.

## Installation

To run **IntelliGemini** locally, you need to have Python 3.7+ installed on your system. Follow these steps to set up the project and get started:

### 1. Clone the repository
First, clone the repository to your local machine:
```bash
git clone https://github.com/DhruvalPtl/AI-Chatbot/IntelliGemini.git
```

### 2. Install dependencies
Navigate to the project directory and install the required Python packages. This will ensure that all the necessary libraries are installed for the app to work correctly.
```bash
cd IntelliGemini
pip install -r requirements.txt
```

### 3. Run the app
Once the dependencies are installed, you can run the app using Streamlit:
```bash
streamlit run app.py
```

After executing this command, the app will open automatically in your default web browser, where you can start interacting with the Gemini language model.

## Usage

Once the app is running, you can begin using it through the Streamlit interface. Here's how you can interact with the app and utilize its features:

1. **Enter a Prompt:** Type your message or question into the input field and press "Enter." The Gemini model will respond with a generated message based on your input.
2. **Adjust Parameters:** On the sidebar, you can adjust the model's settings. You can control the response's randomness, length, and even set stop sequences to define where the model should end its response.
3. **Download Chat History:** You can download your entire chat history in JSON or CSV formats for future reference. This is useful for logging conversations or keeping track of interactions.
4. **Enable Code Execution:** If you need the model to generate and run Python code, you can toggle the "Code Execution Tool" option. This enables the model to generate code and execute it based on your requests.
5. **API Key:** You can provide your own Gemini API key through the sidebar. If you don't, you can use the default key provided by the app's developer. The API key is required to authenticate and send requests to the Gemini API.

## Contributing

Contributions to **IntelliGemini** are welcome! If you find any bugs, have suggestions, or want to add new features, feel free to open an issue or submit a pull request. 

Before submitting changes, ensure your code follows the project's coding style and passes all relevant tests. Here are a few ways you can contribute:
- Report bugs or suggest new features.
- Improve documentation or help with translations.
- Add new features or improve existing functionality.
- Fix issues or update dependencies.

---
