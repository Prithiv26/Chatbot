from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    api_key=os.getenv("GEMINI_API_KEY"),
    
)

class GraphState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: GraphState):
    messages = state["messages"]
    response = llm.invoke(messages)
    return {'messages': [response]}

checkpointer = InMemorySaver()

graph = StateGraph(GraphState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)


# while True:
#     msg = input("You: ")
#     if (msg == "bye"):
#         print("Conversation ended by user...")
#         break
#     msg = HumanMessage(content=msg)

#     config = {'configurable': {'thread_id' : "2"}}

#     result = chatbot.invoke({
#         "messages": [msg]
#     }, config=config)
#     print(f"AI: {result['messages'][-1].content[0]['text']}")
    
# if __name__ == "__backend__":
