from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from langchain.tools import tool
from tools import ping_device, check_device_status

# ✅ LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Wrap SSH tool (inject creds safely later via env)
@tool
def ssh_wrapper(ip: str) -> str:
    """ SSH tool to check if device is up or down"""
    try:
        return check_device_status.invoke({
            "host": ip,
            "username": "admin",
            "password": "password"
        })
    except: 
        return "ssh connection failed"

tools = [ping_device, ssh_wrapper]


prompt = """
You are a Network Operations AI Agent.

Your job is to troubleshoot a ServiceNow ticket.

Steps:
1. Call ping device from provided ip.
2. If ping fails → device unreachable →  unreachable
3. If ping succeeds → use SSH tool
4. If SSH shows device is UP → reachable
5. If SSH fails or shows DOWN →  unreachable

STRICT RULES:
- ALWAYS call ping_device first if IP exists
- ONLY call SSH if ping is successful
- NEVER hallucinate results
- FINAL OUTPUT MUST BE JSON ONLY

Output format:
{{
  "execution_output": "reachable" OR "unreachable",
  "reason": "short explanation"
}}


"""

#  Agent
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=prompt
)
# content="A network issue has been reported for a device with IP address 10.195.3.10. The device is currently experiencing node down"

# res=agent.invoke({ "messages":[{'role':'user', 'content':content}]})
# print(res['messages'][-1].content)

