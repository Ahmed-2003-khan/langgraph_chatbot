from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
# SqliteSaver: Persistent checkpointer that stores conversation state in a SQLite database file
# Unlike InMemorySaver (lost on restart), SQLite persists to disk across sessions
# Install: pip install langgraph-checkpoint-sqlite
# NOTE: correct class name is SqliteSaver (not SQLiteSaver) - casing matters at import time
from langgraph.checkpoint.sqlite import SQLiteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
# sqlite3: Python standard library for interacting with SQLite databases
# Used to create the connection object that SqliteSaver wraps
import sqlite3

load_dotenv()

llm = ChatOpenAI()

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    
def chat_node(state: ChatState):
    response = llm.invoke(state['messages'])
    return {'messages': [response]}

# SQLiteSaver persists checkpoints to a .db file on disk
# This means conversation history survives app restarts — unlike InMemorySaver
# Typical usage: SqliteSaver(conn=sqlite3.connect("checkpoints.db", check_same_thread=False))
# check_same_thread=False is required because Streamlit runs on multiple threads
checkpointer = SQLiteSaver()

graph = StateGraph(ChatState)
graph.add_node('chat_node', chat_node)

graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

# Graph compiled with SQLite-backed checkpointer
# All conversation state is now written to a .db file instead of RAM
chatbot = graph.compile(checkpointer=checkpointer)
