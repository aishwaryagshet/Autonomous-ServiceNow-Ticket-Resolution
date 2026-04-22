from datetime  import datetime
from baseclass import structured_llm, steps_llm, llm, AgentState
import os
import re
from datetime import datetime
from agents import agent
import json

def analyze_ticket(state):
    prompt=f"""
    Extract:
- category (node_down, interface_down, connection_issue)
- ip address 
- device name
- priority
from ticket description

Ticket description:
{state['description']}

strictly structured data. """
    res=structured_llm.invoke(prompt)
    return {"category": res.category, "ip": res.ip, "device_name": res.device_name, "priority": res.priority}

def route_category(state):
    return state['category']

def decide_agent(state):
    if state['priority'] == 'P3':
        print("P3 ticket")
        return "call_agent"
    else:
        print("Non P3 ticket ")
        return "call_node"
    
def agent_for_p3_tickets(state):
    description=state['description']
    res=agent.invoke({ "messages":[{'role':'user', 'content':description}]})
    op=res['messages'][-1].content
    result=json.loads(op)  #convert to json from string
    print("*****************agent output**************")
    print(result)
    return {'execution_result': result}




def generate_steps(state):
    prompt=f""" you are an devops engineer, you are given ticket description and category, write troubleshooting steps 
    to resolve this ticket. You can include steps involving doing SSH to the device and executing commands if necessary.
    Generate top 5 step by step troubleshooting actions.
    Generate clear steps from which I can write an python script in future.
    return steps as list of strings
    description = {state['description']}
    category - {state['category']}
    Rules:
     - return only list of string.
     - No numbering
     - No markdown(**)
     - no explanations
     """
    res= steps_llm.invoke(prompt)
    return {"steps": res.steps}
# state={"description":"""The node "app-server-01" 10.195.3.10 is currently down and not reachable over the network. Monitoring alerts indicate that the system stopped responding approximately 10 minutes ago.""","category":"node_down"}
# print((generate_steps(state)))



def generate_script(state):
    
    prompt=f"""
You are a Senior DevOps Engineer and python expert.

Your task is to generate a valid and executable python scripts for troubleshoting network issue.

Inputs:
- Ticket Description: {state['description']}
- Issue Category: {state['category']}
- Target Device IP: {state['ip']}
- Troubleshooting Steps: {state['steps']}

Instructions:
1. Generate a complete python script.
2. The script must:
   - Use the provided IP address as the target host.
   - Include appropriate functions based on the troubleshooting steps.
   - Use modules such as paramiko, shell, subprocess if needed.
3. Ensure:
   - Proper  indentation
   - No syntax errors
   - Each step is mapped to a meaningful  function
4. Include retries and delays for critical steps like ping check and connectivity.
5. Do ssh to the device and execute commands if necessary.
6. Avoid dangerous or destructive commands.
7. If a step cannot be mapped to a module, use the shell module safely.
8. Output Logic (STRICT — MUST FOLLOW):
   - If the device responds to ping → print("reachable")
   - If the device does NOT respond to ping → print("unreachable")
   - If ANY error/exception occurs → print("unreachable")
9.  CRITICAL OUTPUT RULES:
   - The script MUST print ONLY ONE of the following:
        reachable
        unreachable
   - No logs, no debug statements, no extra prints
   - No return statements, ONLY print
   - The FINAL line of the script MUST be either:
        print("reachable")
        OR
        print("unreachable")

10. Wrap all logic in try/except:
   - Any exception should result in: print("unreachable")

11. Do NOT include explanations — only output the Python script.
12. IMPORTANT:
- Return ONLY raw Python code
- DO NOT include ``` or markdown in beginning or ending

Final Constraint:
            - Under ALL circumstances, the script output MUST be exactly one word:
    reachable OR unreachable

    Only return python script.
    No extra logs or debug output.
"""
    response = llm.invoke(prompt)
    py_content = response.content.strip()
    print(py_content)
   

    #  Create directory if not exists
    output_dir = "playbooks"
    os.makedirs(output_dir, exist_ok=True)

    file_name=f"{state['category']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    file_path=os.path.join(output_dir,file_name)
    with open(file_path, "w") as f:
        f.write(py_content)

    return {"playbook_path": file_path}
#state={"description":"","category":"node_down", "ip": "192.168.29.1", "steps":  ["""SSH into the network monitoring node and check for the status of 'app-server-01' using the command 'ping 192.168.29.1' to verify network connectivity.""", """If the ping fails, SSH into the gateway/router and check the routing table using 'show ip route' to ensure that there is a route to '192.168.29.1'.""", 
#                                                                              """If there is no routing issue, SSH into 'app-server-01' console (if accessible) and review the system logs using 'journalctl -xe' or '/var/log/syslog' to identify any hardware or application failures."""]}

#print(generate_script(state))


def clean_code(state):
    with open(state["playbook_path"], "r") as f:
        content=f.read()
    content=re.sub("```python","",content)
    content=re.sub("```","", content)
    with open(state["playbook_path"], "w") as f:
        f.write(content)
#state={"playbook_path": r"C:\Users\AISHWARYA\Desktop\GenAI\Practice\Servicenow_tickets\playbooks\node_down_20260329_143646.py"}
#print(clean_code(state=state))

import subprocess
def execute_script(state):
    print(f"""Running python script - {state["playbook_path"]}""")
    CONDA_PYTHON=r"c:\Users\AISHWARYA\anaconda3\envs\rag_env\python.exe"
    result=subprocess.run([CONDA_PYTHON, state["playbook_path"]],
        capture_output=True,
        text=True)
    print("************Python scripts output*************")
    print(result.stdout)
    return {"execution_result":{
        "execution_output": result.stdout,
        "error": result.stderr,
        "returncode": result.returncode}
    }
#state={"playbook_path": r"C:\Users\AISHWARYA\Desktop\GenAI\Practice\Servicenow_tickets\playbooks\node_down_20260329_143646.py"}
#print(execute_script(state=state))

import ast
#state={"playbook_path": r"C:\Users\AISHWARYA\Desktop\GenAI\Practice\Servicenow_tickets\playbooks\node_down_20260329_143646.py"}
#state1=execute_script(state=state)
#print(state1)
def decision_node(state):
    print(f"Evaluating results")
    result=state["execution_result"]
    output=result["execution_output"].lower()
    error=result.get("error")
    if error:
        return {"reachable": False}
    if "unreachable" in output:
        return {"reachable": False}
    if "reachable" in output:
        return {"reachable": True}
        
#print(decision_node(state=state1))

def decide_next(state):
    if state["reachable"] == True:
        return "close_ticket"
    else:
        return "reassign_ticket"
    
def close_ticket(state):
    print(f"""Troubleshoot completed....closing ticket - {state["device_name"]}""")

def reassign_ticket(state):
    print(f"""device is unreachable - reassigning ticket {state["device_name"]}""")

from langgraph.graph import StateGraph, END

builder = StateGraph(AgentState)

builder.add_node("analyze", analyze_ticket)
builder.add_node("steps", generate_steps)
builder.add_node("playbook", generate_script)
builder.add_node("clean_code",clean_code)
builder.add_node("execute", execute_script)
builder.add_node("decision_node",decision_node)
builder.add_node("decide_next",decide_next)
builder.add_node("close_ticket", close_ticket)
builder.add_node("reassign_ticket", reassign_ticket)
builder.add_node("decide_route", decide_agent)
builder.add_node("call_agent",agent_for_p3_tickets)

builder.set_entry_point("analyze")
builder.add_conditional_edges("analyze",decide_agent, 
                              {"call_agent" : "call_agent",
                               "call_node": "steps"})

builder.add_edge("call_agent","decision_node")
builder.add_edge("steps", "playbook")
builder.add_edge("playbook", "clean_code")
builder.add_edge("clean_code","execute")
builder.add_edge("execute","decision_node")

builder.add_conditional_edges(
    "decision_node",
    decide_next,
    {
        "close_ticket": "close_ticket",
        "reassign_ticket": "reassign_ticket"
    }
)

builder.add_edge("close_ticket", END)
builder.add_edge("reassign_ticket", END)

graph = builder.compile()

res=graph.invoke({"description":"A network issue has been reported for a device with IP address 172.24.48.1. The device is currently experiencing node down. Priority=P3"})
print(res)

    