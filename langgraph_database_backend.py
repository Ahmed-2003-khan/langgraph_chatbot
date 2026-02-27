from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
import sqlite3

load_dotenv()

llm = ChatOpenAI()

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    
def chat_node(state: ChatState):
    response = llm.invoke(state['messages'])
    return {'messages': [response]}

conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)

checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node('chat_node', chat_node)

graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpointer)

def get_threads():
    # checkpointer.list(None) iterates over ALL checkpoint rows in the SQLite DB
    # Each 'thread' is a CheckpointTuple with a .config dict containing the thread_id
    # We use a set() first to deduplicate — each conversation has multiple checkpoints
    # (one per graph invocation), so raw list would contain duplicates
    threads = set()
    for thread in checkpointer.list(None):
        threads.add(thread.config['configurable']['thread_id'])
    # Convert back to list so the caller can use list operations (append, [::-1], etc.)
    return list(threads)
