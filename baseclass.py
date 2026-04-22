from typing import TypedDict, List
from langchain_openai import ChatOpenAI
llm=ChatOpenAI(model='gpt-4o-mini')

class AgentState(TypedDict):
    description: str
    category: str
    ip: str
    device_name: str
    steps: List[str]
    playbook_path: str
    execution_result: dict
    reachable: bool
    status: str
    priority: str

from pydantic import BaseModel 
from typing import List
class StepsOutput(BaseModel):
    steps: List[str]
class Ticketinfo(BaseModel):
    category: str
    ip: str
    device_name: str
    priority: str
structured_llm=llm.with_structured_output(Ticketinfo)
steps_llm=llm.with_structured_output(StepsOutput)