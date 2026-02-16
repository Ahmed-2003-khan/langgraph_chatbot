# LangGraph imports for building stateful, graph-based applications
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
# InMemorySaver: Enables state persistence in memory (for development/testing)
# In production, you'd use SqliteSaver or PostgresSaver for persistent storage
from langgraph.checkpoint.memory import InMemorySaver
# add_messages: A reducer function that intelligently merges message lists
# It prevents duplicates and maintains conversation history correctly
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

load_dotenv()

# Initialize the LLM that will power our chatbot
llm = ChatOpenAI()

# ChatState: Defines the structure of our graph's state
# TypedDict provides type hints for better IDE support and type checking
class ChatState(TypedDict):
    # Annotated[list[BaseMessage], add_messages]:
    # - The state contains a list of messages (conversation history)
    # - add_messages is a "reducer" that defines HOW to update this field
    # - When new messages are added, add_messages merges them intelligently
    #   (e.g., updates existing messages by ID, appends new ones)
    messages: Annotated[list[BaseMessage], add_messages]
    
# chat_node: A node function that processes the current state
# Node functions in LangGraph:
# 1. Receive the current state as input
# 2. Perform some operation (here: call the LLM)
# 3. Return a partial state update (merged with existing state)
def chat_node(state: ChatState):
    # Invoke the LLM with the conversation history
    response = llm.invoke(state['messages'])
    # Return only the NEW message - add_messages reducer will merge it
    return {'messages': [response]}

# InMemorySaver: Checkpoint saver for state persistence
# This enables:
# - Resuming conversations across sessions
# - Time-travel (accessing previous states)
# - Human-in-the-loop patterns (pause/resume)
checkpointer = InMemorySaver()

# Create the StateGraph with our ChatState schema
# StateGraph manages the flow of data through nodes
graph = StateGraph(ChatState)

# Add the chat_node to the graph
# Nodes are the "workers" that process state
graph.add_node('chat_node', chat_node)

# Define the graph structure with edges
# START -> chat_node: Entry point of the graph
graph.add_edge(START, 'chat_node')
# chat_node -> END: Exit point after processing
graph.add_edge('chat_node', END)

# Compile the graph into a runnable chatbot
# checkpointer=checkpointer enables state persistence
# This allows the chatbot to remember conversation history
chatbot = graph.compile(checkpointer=checkpointer)