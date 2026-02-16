# LangGraph Learning Notes

## Overview
This file tracks my learning progress with LangGraph. Each entry corresponds to a commit in the repository.

---

## Learning Log

### [Date will be added with first commit]
**Topic:** Repository Setup
**Concepts:**
- Initialized Git repository
- Connected to GitHub remote
- Set up automated learning workflow

**Key Takeaways:**
- Ready to start practicing LangGraph
- Workflow in place for documenting learning

---

### 2026-02-16
**Topic:** Basic LangGraph Chatbot with State Persistence
**File:** `backend.py`

**Concepts Learned:**
1. **StateGraph Creation** - Building a graph-based application structure
2. **State Management** - Using TypedDict with Annotated types
3. **Message Reducers** - Using `add_messages` to intelligently merge conversation history
4. **Checkpointing** - Implementing state persistence with `InMemorySaver`
5. **Graph Compilation** - Converting graph definition into a runnable application
6. **Node Functions** - Creating processing units that receive and update state

**Key Takeaways:**
- StateGraph provides the foundation for building stateful LLM applications
- Reducers (like `add_messages`) define HOW state fields are updated when merged
- Checkpointers enable conversation persistence and human-in-the-loop patterns
- The graph structure (START → node → END) defines the execution flow
- Node functions return partial state updates that get merged with existing state

**Code Structure:**
```
START → chat_node → END
         ↓
    (LLM invocation)
```

---

### 2026-02-16 (Update 2)
**Topic:** Streamlit Frontend Integration with LangGraph
**File:** `frontend.py`

**Concepts Learned:**
1. **Thread Configuration** - Using `thread_id` to identify unique conversation sessions
2. **Streamlit Session State** - Managing UI state across page reruns
3. **State Persistence Layers** - Understanding the difference between:
   - Streamlit's `session_state` (UI state during browser session)
   - LangGraph's checkpointer (conversation state across sessions)
4. **Chat Interface** - Building conversational UI with Streamlit components

**Key Takeaways:**
- `thread_id` in CONFIG is how LangGraph identifies which conversation to load/save
- Streamlit's session state is temporary (browser session only)
- LangGraph's checkpointer provides true persistence across restarts
- The two state management systems work together: UI state + conversation state

**Implementation Status:**
- ✅ Session state initialization
- ✅ Message display loop
- ✅ User input handling
- ⏳ TODO: Integrate chatbot invocation with LangGraph
- ⏳ TODO: Display AI responses

---

<!-- Future entries will be added here -->
