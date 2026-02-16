import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage

# Thread configuration for LangGraph's checkpointing system
# The thread_id uniquely identifies this conversation session
CONFIG = {'configurable': {'thread_id': 'chat_thread_1'}}

# Initialize Streamlit session state for UI persistence
# This maintains the message history during the current browser session
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
    
# Render all previous messages from the session state
# This rebuilds the chat interface on each Streamlit rerun
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])
        
# Chat input widget - captures user input
user_input = st.chat_input("Type your message here...")

# Process user input when submitted
if user_input:
    # Add user message to session state and display it
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)
    
    # CRITICAL: Invoke the LangGraph chatbot
    # - {'messages': [HumanMessage(...)]} creates the state structure
    # - HumanMessage wraps the user input in LangChain's message format
    # - config=CONFIG passes the thread_id for checkpointing
    # 
    # What happens internally:
    # 1. LangGraph loads previous conversation state using thread_id
    # 2. Adds the new HumanMessage to the conversation history
    # 3. Runs through the graph (chat_node invokes the LLM)
    # 4. Saves the updated state back to the checkpointer
    # 5. Returns the complete state including all messages
    response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=CONFIG)
    
    # Extract the AI's response from the returned state
    # response['messages'] contains the full conversation history
    # [-1] gets the last message (the AI's response)
    # .content extracts the text content from the message object
    ai_message = response['messages'][-1].content
    
    # Add AI response to session state and display it
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    with st.chat_message('assistant'):
        st.text(ai_message)