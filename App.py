# app.py
import streamlit as st
from rules import apply_pre_checks
from recommender import get_llm_and_memory, get_llm_chain_response
from dotenv import load_dotenv
import os

# Load environment variables (for API keys)
load_dotenv()

st.set_page_config(layout="wide", page_title="AI Tech Stack Advisor 🤖")
st.title("🤖 AI Tech Stack Advisor")
st.caption("With LangChain, Memory, and Rule-Based Pre-checks")

# --- Initialize LLM & Memory in session state ---
# Unique session ID for each user, could be more robust in deployed apps
session_id = st.session_state.get("session_id", "default_user_session")
if "session_id" not in st.session_state:
    st.session_state.session_id = session_id

if 'llm' not in st.session_state or 'memory' not in st.session_state:
    llm, memory = get_llm_and_memory(session_id)
    if llm and memory:
        st.session_state.llm = llm
        st.session_state.memory = memory
    else:
        st.error("Could not initialize AI model or memory. Please check API key configuration.")
        st.stop()


# --- Project Details Input Form (Sidebar) ---
with st.sidebar:
    st.header("📝 Project Details")
    if 'project_details' not in st.session_state:
        st.session_state.project_details = {
            "project_description": "", 
            "app_type": "Web Application",
            "team_skills": [],
            "budget": "Medium", 
            "timeline": "Medium (3-6 months)",
            "scalability_needs": "Medium"
        }

    st.session_state.project_details["project_description"] = st.text_area(
        "Project Description:",
        st.session_state.project_details["project_description"], height=100
    )
    st.session_state.project_details["app_type"] = st.selectbox(
        "Application Type:",
        ["Web Application", "Mobile Application (Native)", "Mobile Application (Cross-Platform)", "API Backend", "Data Analytics Platform", "AI/ML Application", "Other"],
        index=["Web Application", "Mobile Application (Native)", "Mobile Application (Cross-Platform)", "API Backend", "Data Analytics Platform", "AI/ML Application", "Other"].index(st.session_state.project_details["app_type"])
    )
    st.session_state.project_details["team_skills"] = st.multiselect(
        "Team Skills:",
        ["Python", "JavaScript", "Java", "C#", "Ruby", "Go", "Swift", "Kotlin", "React", "Vue", "Angular", "Node.js", "Django", "Flask", "SQL", "NoSQL", "AWS", "Azure", "GCP", "None"],
        default=st.session_state.project_details["team_skills"]
    )
    st.session_state.project_details["budget"] = st.select_slider(
        "Budget:", ["Low", "Medium", "High"], value=st.session_state.project_details["budget"]
    )
    st.session_state.project_details["timeline"] = st.select_slider(
        "Timeline:", ["Very Short (Under 1 month)", "Short (1-3 months)", "Medium (3-6 months)", "Long (6-12 months)"],
        value=st.session_state.project_details["timeline"]
    )
    st.session_state.project_details["scalability_needs"] = st.select_slider(
        "Scalability:", ["Low", "Medium", "High", "Very High"],
        value=st.session_state.project_details["scalability_needs"]
    )

    st.markdown("---")
    if st.button("Clear Conversation History", use_container_width=True):
        st.session_state[f"conversation_memory_{session_id}"].clear()
        st.success("Conversation history cleared!")
        st.rerun()


# --- Chat Interface ---
if 'messages' not in st.session_state:
    st.session_state.messages = [] # For displaying chat like history

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], list): # Structured recommendations
            for i, rec in enumerate(message["content"]):
                 st.markdown(f"#### Recommendation #{i+1}: **{rec.get('stack_name', 'N/A')}**")
                 st.markdown(f"**Source:** _{rec.get('source', 'AI Agent')}_")
                 st.markdown(f"**Components:** `{'`, `'.join(rec.get('core_components', []))}`")
                 st.markdown("**Justification:**")
                 st.info(rec.get('justification', 'N/A'))
                 # Display Pros & Cons if available
                 col1, col2 = st.columns(2)
                 with col1:
                    st.markdown("**👍 Pros:**")
                    if rec.get('pros') and isinstance(rec.get('pros'), list):
                        for pro in rec['pros']: st.markdown(f"- {pro}")
                    else: st.markdown("- N/A")
                 with col2:
                    st.markdown("**👎 Cons:**")
                    if rec.get('cons') and isinstance(rec.get('cons'), list):
                        for con in rec['cons']: st.markdown(f"- {con}")
                    else: st.markdown("- N/A")
                 if rec.get("addressed_follow_up"):
                    st.caption(f"Follow-up Addressed: {rec.get('addressed_follow_up')}")
                 st.markdown("---")
        elif isinstance(message["content"], dict) and "raw_text_fallback" in message["content"]: # LLM fallback
            st.warning(f"AI Response (Fallback): {message['content']['details']}")
            st.text_area("Raw AI Output:", value=message["content"]["raw_text_fallback"], height=150, disabled=True)
        else: # Simple text messages (user queries, errors)
            st.markdown(message["content"])


# Get user input (follow-up question)
user_query = st.chat_input("Ask a follow-up or type 'recommend' for initial advice:")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("🤖 AI Agent is analyzing..."):
            current_project_details = st.session_state.project_details
            
            # 1. Apply Rule-Based Pre-checks
            rule_result = apply_pre_checks(current_project_details)
            response_data = None

            if rule_result:
                if "error" in rule_result:
                    error_message = f"**Rule-Based Check Failed:** {rule_result['error']} - {rule_result['details']}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
                    response_data = None # Stop processing
                else: # Direct recommendation from rules
                    st.success(f"💡 Recommendation from Rule-Based Pre-check:")
                    response_data = rule_result["recommendations"] # List of recs
                    # Add source to each recommendation if not already there
                    for rec_item in response_data:
                        rec_item["source"] = rule_result.get("source", "Rule-Based System")
            else:
                # 2. If no rule triggered, call LLM via LangChain
                if 'llm' in st.session_state and 'memory' in st.session_state:
                    llm_response_package = get_llm_chain_response(
                        st.session_state.llm,
                        st.session_state.memory,
                        current_project_details,
                        user_query
                    )
                    if "recommendations" in llm_response_package:
                        response_data = llm_response_package["recommendations"]
                        for rec_item in response_data: # Add source
                             rec_item["source"] = llm_response_package.get("source", "LLM via LangChain")
                    elif "raw_text_fallback" in llm_response_package:
                        st.warning(f"AI Response (Fallback): {llm_response_package['details']}")
                        st.text_area("Raw AI Output:", value=llm_response_package["raw_text_fallback"], height=150, disabled=True)
                        st.session_state.messages.append({"role": "assistant", "content": llm_response_package}) # Store the fallback dict
                        response_data = None # Don't try to display as structured rec
                    elif "error" in llm_response_package:
                        error_message = f"**AI Agent Error:** {llm_response_package['error']} - {llm_response_package['details']}"
                        st.error(error_message)
                        st.session_state.messages.append({"role": "assistant", "content": error_message})
                        response_data = None
                else:
                    no_llm_error = "LLM or Memory not initialized. Cannot proceed."
                    st.error(no_llm_error)
                    st.session_state.messages.append({"role": "assistant", "content": no_llm_error})
                    response_data = None

            # Display structured recommendations if available
            if response_data and isinstance(response_data, list):
                st.session_state.messages.append({"role": "assistant", "content": response_data})
                # Rerun to display the new messages in the correct chat format
                st.rerun()


# For debugging: Show raw LLM output if available
with st.sidebar:
    st.markdown("---")
    st.header("🔍 Debug Info")
    if st.checkbox("Show Last LLM Formatted Input"):
        st.text_area("Last Formatted Input to LLM:", value=st.session_state.get('last_llm_formatted_input', 'N/A'), height=200, disabled=True)
    if st.checkbox("Show Last Raw LLM Output"):
        st.text_area("Last Raw Output from LLM:", value=st.session_state.get('last_llm_raw_output', 'N/A'), height=200, disabled=True)