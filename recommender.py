# llm_agent_langchain.py
import streamlit as st
import os
import json
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferWindowMemory

# Choose your LLM provider
# from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

# --- LLM and Memory Initialization ---
# This should ideally be done once per session in your Streamlit app
def get_llm_and_memory(session_id="default_session"):
    # Use Streamlit secrets for API keys
    # For Google Gemini
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.7,
            convert_system_message_to_human=True # Important for some LangChain chains with Gemini
        )
    except Exception as e:
        st.error(f"Error initializing Google Gemini: {e}")
        return None

    # Conversation Memory
    # Using a unique key for memory in session_state based on session_id if you plan multiple users
    memory_key = f"conversation_memory_{session_id}"
    if memory_key not in st.session_state:
        st.session_state[memory_key] = ConversationBufferWindowMemory(
            k=5, # Remember last 5 interactions
            return_messages=True,
            memory_key="chat_history_buffer", # LangChain's internal key for the history messages
            input_key="user_full_input" # The key for the current user input to the chain
        )
    return llm, st.session_state[memory_key]

# --- Prompt Template ---
SYSTEM_PROMPT_LANGCHAIN = """
You are an expert AI Tech Stack Advisor. Your task is to analyze the user's project requirements
and recommend up to three suitable technology stacks. Your recommendations must be thorough,
well-justified, and directly address the user's inputs. Consider the conversation history for follow-up questions.

Current Project Context (if provided by user, otherwise assume this is the first interaction):
{project_context_summary}

Instructions for your response:
1. If the user asks a follow-up question, prioritize answering that question in the context of previous recommendations OR if the new input significantly changes criteria, provide new recommendations.
2. Structure your entire response as a single JSON array. Each element in the array
   should be a JSON object representing one technology stack recommendation, containing the
   following keys:
   - "stack_name": A descriptive name for the tech stack.
   - "core_components": A list of strings detailing the main technologies.
   - "justification": A detailed explanation of why this stack is a good fit, referencing user inputs and conversation history.
   - "pros": A list of key advantages.
   - "cons": A list of key disadvantages or trade-offs.
   - "addressed_follow_up": (Optional string) Briefly mention if/how this response addresses a follow-up from the user.
3. If providing initial recommendations, be comprehensive. If answering a follow-up, be concise and targeted if possible.
"""

# Note: For Gemini with LLMChain, we often build the full prompt string rather than relying on separate system messages.
# However, ChatPromptTemplate is more standard for chat models.
# The `convert_system_message_to_human=True` for Gemini helps if the system message isn't handled as expected.

prompt_template = ChatPromptTemplate.from_messages([
    # System message can be tricky with LLMChain and Gemini.
    # It's often better to prepend it to the human message or ensure the model wrapper handles it.
    # For this example, we'll include system instructions within the initial human message context.
    MessagesPlaceholder(variable_name="chat_history_buffer"), # For Langchain memory
    ("human", "{user_full_input}") # Current user input combined with context
])

def format_user_input_with_context(project_details, user_query):
    """Combines structured project details and the current user query for the LLM."""
    context_summary = "\n".join([f"- {key.replace('_', ' ').capitalize()}: {value}" for key, value in project_details.items()])
    
    initial_prompt_guidance = f"""
    System Instructions:
    {SYSTEM_PROMPT_LANGCHAIN.format(project_context_summary=context_summary)}

    User's Current Request/Context:
    The overall project context is as follows:
    {context_summary}
    
    User's specific question for this turn: "{user_query if user_query else 'Provide initial tech stack recommendations based on the context above.'}"

    Please provide your recommendations or answer in the specified JSON format.
    """
    return initial_prompt_guidance

def get_llm_chain_response(llm, memory, project_details, user_query):
    if not llm:
        return {"error": "LLM_NOT_INITIALIZED", "details": "LLM client could not be set up."}

    chain = LLMChain(
        llm=llm,
        prompt=prompt_template, # This template expects "chat_history_buffer" and "user_full_input"
        memory=memory,
        verbose=True # For debugging LangChain process
    )

    formatted_input = format_user_input_with_context(project_details, user_query)
    raw_llm_output = "" 

    try:
        response_from_chain = chain.invoke({"user_full_input": formatted_input})
        raw_llm_output = response_from_chain.get('text', '') # 'text' is the default output key for LLMChain

        st.session_state['last_llm_raw_output'] = raw_llm_output # For debugging
        st.session_state['last_llm_formatted_input'] = formatted_input # For debugging

        # Attempt to parse JSON (robust cleaning needed)
        cleaned_output = raw_llm_output.strip()
        # Find the start and end of the JSON array
        json_start = cleaned_output.find('[')
        json_end = cleaned_output.rfind(']') + 1
        
        if json_start != -1 and json_end != 0 and json_end > json_start:
            json_str = cleaned_output[json_start:json_end]
            parsed_recommendations = json.loads(json_str)
            if not isinstance(parsed_recommendations, list):
                raise ValueError("LLM output was valid JSON, but not a list.")
            # Further validation of item structure can be added here
            return {"recommendations": parsed_recommendations, "source": "LLM via LangChain"}
        else:
            # Fallback if no JSON array is found - return raw text wrapped as an error/note
            return {
                "error": "LLM_RESPONSE_NOT_JSON_ARRAY", 
                "details": "LLM did not return a parseable JSON array. Displaying raw text.", 
                "raw_text_fallback": cleaned_output,
                "source": "LLM via LangChain"
            }

    except json.JSONDecodeError as e:
        error_detail = f"Failed to parse LLM output as JSON. Error: {e}. Raw output was: \n{raw_llm_output}"
        return {"error": "LLM_JSON_PARSE_ERROR", "details": error_detail, "raw_text_fallback": raw_llm_output}
    except Exception as e:
        error_detail = f"An unexpected error occurred: {type(e).__name__} - {e}"
        return {"error": "LLM_CHAIN_ERROR", "details": error_detail, "raw_text_fallback": raw_llm_output}