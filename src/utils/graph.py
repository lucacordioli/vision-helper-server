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
            model="gpt-3.5-turbo",
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

    def run(self, message: str):
        return self.app.invoke(
            {"messages": [HumanMessage(content=message)]},
            config={"configurable": {"thread_id": 42}}
        )

# Uso:
# workflow_manager = WorkflowManager()
# result = workflow_manager.run(initial_state)
