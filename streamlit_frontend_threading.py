import streamlit as st
from backend import chatbot
# AIMessage imported alongside HumanMessage to enable isinstance() type-checking
# when converting LangChain message objects → plain dicts for Streamlit display
from langchain_core.messages import HumanMessage, AIMessage
import uuid

## Utility functions

def generate_thread_id():
    return str(uuid.uuid4())

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id)
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_thread(thread_id):
    # Switch the active thread in session state
    st.session_state['thread_id'] = thread_id
    # Build a local config for fetching — we don't update the global CONFIG here
    # because Streamlit will rebuild it from session_state on the next rerun
    CONFIG = {'configurable': {'thread_id': thread_id}}
    # chatbot.get_state(CONFIG): reads the saved checkpoint for this thread_id
    # Returns a StateSnapshot whose .values dict mirrors the graph's state schema
    # .values['messages'] gives the full LangChain message list for this conversation
    # NOTE: must return — not assign to session_state — so the caller can process it
    return chatbot.get_state(CONFIG).values['messages']

# st.session_state -> dict ->
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

add_thread(st.session_state['thread_id'])

CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()
    

st.sidebar.header('My conversations')

for thread_id in st.session_state['chat_threads']:
    if st.sidebar.button(str(thread_id)):
        # load_thread returns a list of LangChain message objects (HumanMessage, AIMessage)
        # These are NOT plain dicts — we can't do message['role'] directly on them
        # TypeError: 'HumanMessage' object is not subscriptable (if you try)
        messages = load_thread(thread_id)

        temp_messages = []

        # Convert LangChain message objects → Streamlit-compatible dicts
        # isinstance() dispatch: determine message type, then map to role string
        # This is the bridge between LangGraph's message format and Streamlit's UI format
        for message in messages:
            if isinstance(message, HumanMessage):
                temp_messages.append({'role': 'user', 'content': message.content})
            elif isinstance(message, AIMessage):
                temp_messages.append({'role': 'assistant', 'content': message.content})

        # Replace the UI message history with the loaded conversation
        st.session_state['message_history'] = temp_messages


# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    with st.chat_message('assistant'):

        ai_message = st.write_stream(
            message_chunk.content for message_chunk, meta_data in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
