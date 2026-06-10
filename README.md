# 🚀 ServiceNow Ticket Automation using LangGraph & AI Agents

An intelligent *Network Operations AI System* that automates troubleshooting of ServiceNow tickets using *LLMs, Agents, and LangGraph workflows*.

This project simulates a real-world *NOC (Network Operations Center)* pipeline where tickets are analyzed, actions are executed (ping/SSH), and decisions are made automatically.

---

## 🧠 Key Features

- 🔍 *Ticket Understanding using LLM*
  - Extracts:
    - Category (node_down / interface_down / connection_issue)
    - IP Address
    - Device Name
    - Priority

- 🤖 *Agent-based Decision Making*
  - Uses tools like:
    - ping_device
    - ssh_wrapper

- 🔁 *LangGraph Workflow Orchestration*
  - Structured execution pipeline instead of free-form agent loops

- ⚙️ *Dynamic Script Generation*
  - Generates Python troubleshooting scripts using LLM

- 🧪 *Execution Engine*
  - Runs generated scripts via subprocess
  - Captures:
    - Output
    - Errors
    - Return codes

- 🎯 *Final Decision Engine*
  - Determines:
    - close_ticket
    - reassign_ticket

🔐 Key Design Decisions

✅ Why LangGraph?

* Deterministic execution
* Avoids infinite loops of agents
* Easier debugging

✅ Why Agent only for P3?

* High priority → needs intelligent reasoning
* Others → follow standard automation

✅ Why Script Generation?

* Simulates real DevOps automation
* Extensible to real infra

⸻

## ⚙️ Workflow Explanation

### 
1. 🧾 Ticket Analysis
- Uses LLM to extract structured fields:
```json
{
  "category": "node_down",
  "ip": "10.195.3.10",
  "device_name": "app-server-01",
  "priority": "P3"
}

2. 🧠 Routing Logic

* If priority == P3 → use Agent
* Else → follow deterministic pipeline


3. 🤖 Agent Execution

Agent:

* Calls ping_device
* If success → calls ssh_wrapper
* Returns:
{
  "execution_output": "reachable/unreachable",
  "reason": "short explanation"
}

4. 🧪 Script-Based Execution Path

For non-agent flow:

1. Generate troubleshooting steps (LLM)
2. Convert steps → Python script (LLM)
3. Clean script (remove markdown)
4. Execute script using subprocess


5. ⚖️ Decision Node

Evaluates result:
if error:
    reachable = False
elif "unreachable" in output:
    reachable = False
elif "reachable" in output:
    reachable = True

6.  Final Action

* close_ticket → if device is reachable
* reassign_ticket → if unreachable

example run : python main.py
Input= "A network issue has been reported for a device with IP address 172.24.48.1. The device is currently experiencing node down. Priority=P3"
Output:
{
  "description": "...",
  "category": "node_down",
  "ip": "172.24.48.1",
  "device_name": "device",
  "priority": "P3",
  "execution_result": {
    "execution_output": "unreachable",
    "reason": "SSH failed despite ping success"
  },
  "reachable": false
}
______

⚠️ Known Limitations

* No real ServiceNow integration (mocked)
* SSH uses static credentials (for demo)
* LLM output parsing assumes correct format
* No retry/backoff logic yet

⸻

🚀 Future Improvements

*  Retry mechanism for ping/SSH
*  Secure credential management
*  Real ServiceNow API integration
*  Monitoring & logging


⸻
🛠️ Tech Stack

* Python 
* LangGraph 
* LLM (via custom wrappers)
* Subprocess (script execution)

⸻

💡 Key Learning Outcomes

* Difference between Agent vs LLM vs Workflow
* When to use:
    * Agent → reasoning
    * Graph → control
* Handling:
    * Tool calls
    * Structured outputs
    * Execution pipelines

⸻
 Author

Built as a hands-on GenAI + DevOps automation project to simulate real-world NOC workflows.
