import streamlit as st
from backend import chatbot  # Fixed: correct module name is 'backend', not 'langgraph_backend'
from langchain_core.messages import HumanMessage
import uuid  # Standard library for generating universally unique identifiers

## Utility functions

def generate_thread_id():
    # uuid.uuid4() generates a random UUID (128-bit number)
    # Each call produces a globally unique string - perfect for conversation IDs
    # e.g. '3f2504e0-4f89-11d3-9a0c-0305e82c3301'
    return str(uuid.uuid4())

def reset_chat():
    # Creates a brand new conversation by assigning a fresh thread_id
    # LangGraph will treat this as a completely new conversation in the checkpointer
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id)  # Register the new thread in the sidebar list
    st.session_state['message_history'] = []  # Clear the UI message history

def add_thread(thread_id):
    # Deduplication guard: only add the thread_id if not already tracked
    # This is called both on first load AND after every reset_chat()
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

# --- Session State Initialization ---
# Streamlit reruns the entire script on every user interaction.
# These 'not in' guards ensure we only initialize state ONCE per browser session.

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'chat_threads' not in st.session_state:
    # chat_threads: a list of all thread IDs created in this browser session
    # This powers the sidebar conversation list (like ChatGPT's conversation history)
    st.session_state['chat_threads'] = []

# Register the initial thread on first load (deduplication handled inside add_thread)
add_thread(st.session_state['thread_id'])

# CONFIG is built from session_state so it reflects the CURRENT active thread
# This is critical: using a hardcoded value like 'thread-1' would mean all
# "New Chat" sessions share the same LangGraph conversation history
CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

# --- Sidebar UI ---
st.sidebar.title('LangGraph Chatbot')

# "New Chat" button: triggers reset_chat() which generates a new thread_id
# After the script reruns, CONFIG will use the new thread_id automatically
if st.sidebar.button('New Chat'):
    reset_chat()
    
st.sidebar.header('My conversations')

# Display all tracked thread IDs as a conversation list in the sidebar
# Future enhancement: make these clickable to switch between conversations
for thread_id in st.session_state['chat_threads']:
    st.sidebar.text(thread_id)

# --- Main Chat Area ---
# Replay all stored messages on every rerun to rebuild the chat interface
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    with st.chat_message('assistant'):
        # chatbot.stream() vs chatbot.invoke():
        # - invoke(): waits for the full response, then returns it all at once
        # - stream(): yields response chunks incrementally as the LLM generates them
        #
        # stream_mode="messages": yields (message_chunk, metadata) tuples
        # message_chunk.content: the text fragment produced in this chunk
        #
        # st.write_stream(): consumes the generator, displaying each chunk
        # in real time as it arrives - creates the "typing" effect
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, meta_data in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
