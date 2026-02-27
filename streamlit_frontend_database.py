import streamlit as st
# Import both chatbot AND get_threads from the database backend
# get_threads() reads all past conversation IDs directly from SQLite on app startup
from langgraph_database_backend import chatbot, get_threads
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
    st.session_state['thread_id'] = thread_id
    CONFIG = {'configurable': {'thread_id': thread_id}}
    # FIXED: use .get('messages', []) instead of ['messages']
    # checkpointer.list(None) returns ALL checkpoints including empty intermediate ones
    # that LangGraph writes before a node runs — those have no 'messages' key yet
    # Direct ['messages'] access → KeyError on those empty checkpoints
    # .get('messages', []) → safely returns [] and the caller's for-loop just skips it
    return chatbot.get_state(CONFIG).values.get('messages', [])

# st.session_state -> dict ->
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'chat_threads' not in st.session_state:
    # Key upgrade vs InMemory version: instead of starting with an empty list,
    # we seed chat_threads from the SQLite database on first load
    # This means past conversations survive app restarts and appear in the sidebar immediately
    # IMPORTANT: get_threads() returns a list (converted from set), so .append() works fine
    # Earlier bug: get_threads() returned a set → AttributeError: 'set' has no attribute 'append'
    st.session_state['chat_threads'] = get_threads()

add_thread(st.session_state['thread_id'])

CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()
    
st.sidebar.header('My conversations')

for thread_id in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(thread_id)):
        messages = load_thread(thread_id)

        temp_messages = []

        for message in messages:
            if isinstance(message, HumanMessage):
                temp_messages.append({'role': 'user', 'content': message.content})
            elif isinstance(message, AIMessage):
                temp_messages.append({'role': 'assistant', 'content': message.content})

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
