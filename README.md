# AI Tech Stack Advisor 🤖💡

## Overview

The **AI Tech Stack Advisor** is an intelligent web application designed to help developers, project managers, and companies determine the most suitable technology stack for their software projects. By providing details about the project's scope, team expertise, budget, timeline, and scalability requirements, users receive tailored recommendations powered by a Large Language Model (LLM) integrated via LangChain, enhanced with a rule-based pre-checking layer and conversational memory.

This tool aims to simplify the often complex decision-making process of selecting a tech stack, offering reasoned advice and highlighting potential trade-offs.

---

## 🌟 Features

* **Intelligent Recommendations:** Leverages advanced LLMs (e.g., Google Gemini or OpenAI GPT) through LangChain to provide context-aware tech stack suggestions.
* **Rule-Based Pre-checks:** Implements a lightweight rules engine to handle obvious use cases (e.g., static sites) or detect contradictory user inputs before querying the LLM, saving resources and providing faster feedback for common scenarios.
* **Conversational Memory:** Remembers the context of the current session, allowing users to ask follow-up questions and receive relevant, evolving advice.
* **Detailed Justifications:** Each recommendation comes with explanations of why a particular stack is suitable, including pros and cons tailored to the user's input.
* **User-Friendly Interface:** Built with Streamlit for an interactive and easy-to-use web experience.
* **Customizable Inputs:** Allows users to specify:
    * Project Description
    * Application Type (Web, Mobile, API, etc.)
    * In-house Team Skills
    * Budget Constraints
    * Project Timeline
    * Scalability Needs
* **Secure API Key Management:** Uses environment variables (via `.env` file locally).

---

## 🛠️ Technology Stack

* **Backend Logic:** Python
* **Web Framework/UI:** Streamlit
* **LLM Orchestration:** LangChain
* **LLM Providers (Examples):** Google Gemini,
* **Environment Management:** `python-dotenv`

---

## 📄 File Structure


### File Descriptions:

* **`app.py`**: This is the entry point of the application. It handles the Streamlit user interface, collects user inputs, manages session state for conversation history, and orchestrates calls to the `rules_engine.py` and `llm_agent_langchain.py` modules to generate and display recommendations.
* **`rules_engine.py`**: Contains functions that implement a lightweight rule-based system. This module pre-processes user inputs to identify simple, clear-cut scenarios (like a static website needing a JAMstack) or detect contradictory inputs (e.g., "high scalability" with "no backend"). If a rule is met, it can bypass the LLM call, providing an immediate response or an error message.
* **`llm_agent_langchain.py`**: This module is responsible for all interactions with the Large Language Model (LLM) using the LangChain library. It sets up the chosen LLM (e.g., Google Gemini), configures the conversational memory (to remember past interactions within a session), crafts the detailed prompts (including system instructions, user context, and chat history), and processes the LLM's responses, including parsing the expected JSON output.
* **`.env`**: A local file (not to be committed to version control) used to store sensitive information like API keys (e.g., `GOOGLE_API_KEY`). The `python-dotenv` library loads these variables into the environment when the application starts locally.
* **`requirements.txt`**: Lists all Python dependencies required to run the project. This file allows for easy setup of the project environment using `pip install -r requirements.txt`.

---

## ⚙️ Setup and Installation

Follow these steps to get the AI Tech Stack Advisor running on your local machine:

1.  **Prerequisites:**
    * Python 3.8 or newer
    * pip (Python package installer)

2.  **Clone the Repository (if applicable):**
    ```bash
    git clone 
    cd 
    ```
    If you just have the files, ensure they are in a directory as described in "File Structure".

3.  **Install Dependencies:**
    Use the `requirements.txt` file to install all necessary libraries.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up API Keys:**
    * Create a file named `.env` in the root of your project directory (`tech_stack_agent/.env`).
    * Add your LLM provider's API key to this file. For example, for Google Gemini:
        ```env
        # .env
        GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"
        ```
    * Replace `"YOUR_..._API_KEY_HERE"` with your actual API key.
    * **Important:** The `llm_agent_langchain.py` and `app.py` files are configured to load this key using `python-dotenv` for local execution. Ensure the variable name in `.env` (e.g., `GOOGLE_API_KEY`) matches what's expected in the code (`os.getenv("GOOGLE_API_KEY")`).

---

## ▶️ How to Run the Application

1.  **Ensure your virtual environment is activated.**
2.  **Navigate to the project's root directory** in your terminal.
3.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```
4.  Streamlit will start the application and provide a local URL (usually `http://localhost:8501`) which should automatically open in your default web browser.

You can then interact with the application by providing your project details in the sidebar and asking for recommendations or follow-up questions in the chat interface.

---

## 🤔 Reasoning Behind Implementation Choices

* **Streamlit for UI:** Chosen for its simplicity and speed in building interactive data-centric web applications in Python. It allows for rapid prototyping and a clean user interface with minimal frontend code.
* **LangChain for LLM Orchestration:** LangChain simplifies the process of building applications with LLMs. It provides convenient abstractions for prompt management, LLM interaction, memory handling, and creating chains of operations, making the code more modular and maintainable.
* **LLM as Core Recommender:** Using a powerful LLM (like Gemini or GPT models) allows the advisor to understand nuanced project descriptions and provide more flexible and contextually relevant recommendations than a purely hardcoded system. The ability to request structured JSON output is also a key advantage.
* **Rule-Based Pre-check Layer:** This was added to:
    * **Efficiency:** Handle very common or simple scenarios (e.g., static websites) without the need for a potentially slower and more costly LLM call.
    * **Accuracy for Obvious Cases:** Ensure that straightforward cases get deterministic and correct advice.
    * **Input Validation:** Detect clearly contradictory user inputs early, guiding the user to refine their requirements and improving the quality of subsequent LLM queries.
* **Conversational Memory (`ConversationBufferWindowMemory`):** Implemented to allow for more natural, iterative interactions. Users can ask follow-up questions, and the AI can refer to the recent context of the conversation, making the advice more refined and specific to the user's evolving thoughts. A windowed memory is chosen to keep the context relevant and manage token limits.
* **`.env` for Local API Key Management:** A standard and secure way to handle sensitive credentials during local development, preventing them from being accidentally committed to version control. Streamlit's `st.secrets` is the preferred method for deployed applications.
* **Modular File Structure:** Separating concerns into `app.py` (UI), `rules_engine.py` (rules), and `llm_agent_langchain.py` (LLM logic) makes the project more organized, easier to understand, and scalable.

---

## Future Enhancements (Possible Ideas)

* **More Granular Rule Engine:** Expand the rule-based layer for more nuanced pre-checks.
* **LangChain Output Parsers:** Utilize LangChain's `OutputParser` classes (like `PydanticOutputParser`) for more robust and type-safe parsing of LLM responses.
* **Database for Knowledge Base:** Instead of or in addition to LLM knowledge, integrate a structured database of technologies with pros/cons that the LLM can query or use for fine-tuning.
* **User Feedback Mechanism:** Allow users to rate the quality of recommendations to help improve the system.
* **Cost Estimation:** Provide rough cost estimates associated with recommended stacks (e.g., cloud services).
* **Team Skill Gap Analysis:** Highlight potential skill gaps based on team expertise and recommended stack.
