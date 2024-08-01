import os
from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage, ToolMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint import MemorySaver
from langgraph.graph import add_messages, END, StateGraph
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from src.utils.tools import find_element, get_info


class SystemState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    item_id: str
    pdf_name: str
    page_n: str


class WorkflowManager:
    def __init__(self):
        self.tools = [find_element, get_info]
        self.tool_executor = ToolExecutor(self.tools)
        self.model = ChatOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            model="gpt-4o-mini",
        ).bind_tools(self.tools)
        self.workflow = self._create_workflow()
        self.checkpointer = MemorySaver()
        self.app = self.workflow.compile(checkpointer=self.checkpointer)

    def _create_workflow(self):
        workflow = StateGraph(SystemState)
        workflow.add_node("agent", self._call_model)
        workflow.add_node("action", self._call_tool)
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges("agent", self._should_continue)
        workflow.add_edge("action", 'agent')
        return workflow

    def _should_continue(self, state: SystemState):
        messages = state['messages']
        last_message = messages[-1]
        return "action" if last_message.tool_calls else END

    def _call_model(self, state: SystemState):
        messages = state['messages']
        response = self.model.invoke(messages)
        return {"messages": [response]}

    def _call_tool(self, state: SystemState):
        messages = state["messages"]
        last_message = messages[-1]
        tool_invocations = [
            ToolInvocation(tool=tool_call["name"], tool_input=tool_call["args"])
            for tool_call in last_message.tool_calls
        ]
        responses = self.tool_executor.batch(tool_invocations, return_exceptions=True)
        tool_messages = [
            ToolMessage(content=str(response), name=tc["name"], tool_call_id=tc["id"])
            for tc, response in zip(last_message.tool_calls, responses)
        ]
        output = {"messages": tool_messages}
        for response in responses:
            for key in ["item_id", "pdf_name", "page_n"]:
                if key in response:
                    output[key] = response[key]
        return output

    def run(self, message: str, element_id: str):
        prompt = f"""
                You are an agent in a 3D XR environment, tasked with assisting users as they interact with various objects. Users may send you messages with or without an ID corresponding to an object they recently interacted with. The user might ask for information about this object or other objects within the environment.

                You have access to two tools:
                1. **Information Tool**: Provides information about an object given its ID.
                2. **Highlight Tool**: Returns the ID of a specific object and automatically highlights it in the 3D environment.
                
                You can respond in one of three ways:
                1. **Answer the question without accessing any tool or knowledge**: For example, provide generic responses or common knowledge.
                2. **Use the Information Tool** to answer questions related to the object the user is currently interacting with (if an ID is provided). For instance, if the user asks "What is this?" you can use this tool to obtain and display detailed information about the object.
                3. **Use the Highlight Tool** to answer questions about the location of a specific object or highlight something of interest when no ID is provided. For instance, if the user asks "Where is the pump?" you can use this tool to get the ID and highlight the piece in the 3D environment.
                
                If the user does not provide an ID but is looking for specific guidance, you can use the Highlight Tool to highlight a relevant piece to help them better understand the environment.
                
                **Important**: If the user refers to an existing ID, do not use the Highlight Tool to highlight a new element; only provide information or actions related to the current ID provided by the user.
                
                Examples of usage:
                - **User with ID provided**: "What is this?" (Request information using the Information Tool)
                - **User without ID**: "What can I do here?" (Use the Highlight Tool to highlight a relevant piece and provide general guidance)
                - **User with specific query**: "Where is the pump?" (Highlight the piece using the Highlight Tool)

                User's message: "{message}"
                Element ID: "{element_id}"
                """
        return self.app.invoke(
            {"messages": [HumanMessage(content=prompt)]},
            config={"configurable": {"thread_id": 42}}
        )

# Uso:
# workflow_manager = WorkflowManager()
# result = workflow_manager.run(initial_state)
