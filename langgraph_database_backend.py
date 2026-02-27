from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
# FIXED: correct class name is SqliteSaver (camelCase), NOT SQLiteSaver (all-caps)
# ImportError: cannot import name 'SQLiteSaver' → fix: SqliteSaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
# HumanMessage needed here for the test invocation at the bottom
# FIXED: was missing from imports → NameError: name 'HumanMessage' is not defined
from langchain_core.messages import HumanMessage
# sqlite3: Python standard library — provides the database connection SqliteSaver wraps
import sqlite3

load_dotenv()

llm = ChatOpenAI()

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    
def chat_node(state: ChatState):
    response = llm.invoke(state['messages'])
    return {'messages': [response]}

# sqlite3.connect() creates (or opens) a SQLite database file on disk
# database='chatbot.db' → file path for the .db file (created automatically if it doesn't exist)
# check_same_thread=False → SQLite's default only allows access from the thread that created it
#   This flag disables that restriction — required for Streamlit (multi-threaded) and async usage
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)

# SqliteSaver wraps the connection and implements the LangGraph checkpointer interface
# All graph state (conversation history) is now written to chatbot.db after every invocation
# FIXED: SQLiteSaver() with no args → SqliteSaver(conn=conn) — connection is required
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node('chat_node', chat_node)

graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

# Graph compiled with SQLite-backed checkpointer
# Every chatbot.invoke() call saves state to chatbot.db automatically
chatbot = graph.compile(checkpointer=checkpointer)


# --- Test invocation ---
# Hardcoded thread_id='1' to test that the graph runs and checkpointer saves correctly
# Response includes full state: both HumanMessage input + AIMessage response in messages list
CONFIG = {'configurable': {'thread_id': '1'}}
response = chatbot.invoke({'messages': [HumanMessage(content='Hello')]}, config=CONFIG)
print(response)
