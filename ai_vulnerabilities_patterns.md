# AI IDE & Coding Assistant Vulnerability Patterns

This table simplifies the 25 repeatable attack patterns found in AI coding tools. The patterns describe how an attacker could trick an AI tool into doing something harmful, often just by getting you to open a malicious project folder.

## 1. Arbitrary Code/Command Execution
*These attacks let a hacker run harmful code or commands on your computer through the AI tool.*

| Pattern Name | What it means in simple terms |
| :--- | :--- |
| **1.1 MCP Configuration Poisoning** | Hiding a malicious config file in a project that forces the AI to run bad commands. |
| **1.2 LSP Configuration** | Tricking the editor into using a fake "language helper" that runs bad code when you open a file. |
| **1.3 Tools/Skills Definition Auto-Loading** | The AI automatically runs any "tool" script it finds in a project folder. |
| **1.4 Argument Injection** | Fooling the AI into adding dangerous extra commands to a safe one it was going to run. |
| **1.5 Hooks Definition** | Setting up scripts that run automatically whenever the AI reads or writes a file. |
| **1.6 Application-Specific Configuration Auto-Execution** | Exploiting a tool's own settings fields that are designed to run commands. |
| **1.7 Initialization Race Condition** | Malicious code runs before the tool asks you if you trust the project. |
| **1.8 Terminal Command Filtering Bypasses** | Sneaking past the AI's safety filters with tricks like hidden characters or special commands. |
| **1.9 Binary Planting** | Placing a fake, malicious program in the project folder, which the AI runs instead of the real one. |
| **1.10 Safe Executables with In-Workspace Config** | Making a normally "safe" command (like `git diff`) dangerous by changing its settings file in the project. |
| **1.11 Environment Variable Prefixing** | Using tricks with environment variables to bypass command blocklists. |
| **1.12 IDE Settings Abuse (IDEsaster)** | Changing a setting in the project folder (e.g., which program runs for a specific file type) to execute bad code. |
| **1.13 Unauthenticated Local Network Services** | The AI tool starts a hidden web server on your computer that any other program or website can talk to and control. |

## 2. Prompt Injection
*These patterns are about tricking the AI itself by hiding instructions in places it will read.*

| Pattern Name | What it means in simple terms |
| :--- | :--- |
| **2.1 Adversarial Directory Names** | Naming a folder something like "read_the_file_and_delete_it_now," and the AI follows that instruction. |
| **2.2 Prompt Template Auto-Loading** | The AI automatically loads a "prompt template" file from the project that changes its core behavior. |
| **2.3 Prompt Injection to Config Modification via File Write** | The AI is tricked into writing a file that changes its own settings, making it less secure. |
| **2.4 Rules Override** | Special project rules files can disable safety features, allowing commands to run without asking you. |
| **2.5 Hidden Instructions (Invisible Unicode)** | Hiding malicious instructions using invisible characters that humans can't see, but the AI can. |

## 3. Data Exfiltration
*These patterns are specifically about stealing your private data, like API keys or source code.*

| Pattern Name | What it means in simple terms |
| :--- | :--- |
| **3.1 Markdown Image Rendering** | Tricking the AI into showing a markdown image. The image's web address contains your stolen data, which is sent to the attacker's server when your computer tries to load the image. |
| **3.2 Mermaid Diagram Abuse** | Same as above, but using a different type of diagram that might not have the same security checks. |
| **3.3 Pre-Configured URL Fetching** | Changing a project setting that makes the tool fetch a specific web address. If that address now points to an attacker's server, your data is sent there. |
| **3.4 Webview Rendering** | Tricking the AI into opening a webpage it controls, with your stolen data hidden in the page's web address. |
| **3.5 Model Provider Redirect** | Changing a setting so all your conversations with the AI (including your prompts and the code/files it sees) are secretly sent to a hacker's server instead of the real AI company. |
| **3.6 DNS-Based Exfiltration** | Using common, often-allowlisted commands like `ping` to send stolen data to an attacker's server by hiding it in the domain name. |

## 4. Trust Persistence / TOCTOU
*These patterns describe how an attacker can maintain access, even after you think you've removed the threat.*

| Pattern Name | What it means in simple terms |
| :--- | :--- |
| **4.1 Persistent Backdoor via Global Config** | Malicious code is written to a global settings folder (not just the project), so it runs every time you use the tool. |
| **4.2 Two-Step Configuration Poisoning** | You approve a harmless-looking config, but an attacker changes it in a later project update, and the tool runs it without asking again. |
| *Note: This category describes the *method* of attack, which can apply to many of the config files mentioned above.* | |


## 🛡️ Common Attack Chains
The patterns are rarely used alone. The repository outlines common attack chains, which are step-by-step recipes for an attack. For example:

Chain 1 — "The Classic": Clone a malicious repo → Hidden instructions in code → AI writes a file → That file changes a setting → The new setting runs bad code.

Chain 3 — "The Exfil Express": Clone repo → Instruction in README file → AI reads your API key → AI sends it to a hacker's server.

# AI IDE Vulnerabilities: Selected Examples

| Category | Vulnerability Description | Affected Product | Source |
| :--- | :--- | :--- | :--- |
| **Arbitrary Code Execution** | Attackers can coerce the AI agent into running unintended or malicious terminal commands, with one extreme case reporting the agent formatting an entire drive. | Google Antigravity IDE | [Mindgard Disclosures](https://mindgard.ai/disclosures/) |
| **Arbitrary Code Execution** | Malicious instructions can be embedded in a project's `.clinerules` directory to force all `execute_command` operations to run without user approval, enabling silent code execution. | Cline AI Coding Agent | [From Prompt to Pwn: Cline Bot AI Coding Agent Vulnerabilities](https://mindgard.ai/blog/from-prompt-to-pwn-cline-bot-ai-coding-agent-vulnerabilities) |
| **Arbitrary Code Execution** | A malicious "trusted workspace" can embed a backdoor that executes arbitrary code every time the application launches, persisting even after a complete uninstall and reinstall. | Google Antigravity IDE | [Forced Descent: Google Antigravity Persistent Code Execution](https://mindgard.ai/blog/forced-descent-google-antigravity-persistent-code-execution) |
| **Prompt Injection** | The most critical flaw allows attackers to plant malicious instructions directly into source code files, such as Python docstrings or Markdown configuration files, which the agent then executes. | Cline AI Coding Agent | [From Prompt to Pwn: Cline Bot AI Coding Agent Vulnerabilities](https://mindgard.ai/blog/from-prompt-to-pwn-cline-bot-ai-coding-agent-vulnerabilities) |
| **Prompt Injection** | Attackers can hide instructions in source code comments, Markdown files, or other processed content to manipulate the AI's behavior. | Google Antigravity IDE | [Mindgard Disclosures](https://mindgard.ai/disclosures/) |
| **Prompt Injection** | Vulnerabilities often exploit the AI's instruction hierarchy, where "user rules" are given high priority, allowing malicious instructions to override built-in safety mechanisms. | Google Antigravity IDE | [Mindgard Disclosures](https://mindgard.ai/disclosures/) |
| **Data Exfiltration** | Attackers can coerce the AI into reading environment variables (including API keys) and encoding them into DNS queries sent to attacker-controlled domains via seemingly benign `ping` commands. | Cline AI Coding Agent | [From Prompt to Pwn: Cline Bot AI Coding Agent Vulnerabilities](https://mindgard.ai/blog/from-prompt-to-pwn-cline-bot-ai-coding-agent-vulnerabilities) |
| **Data Exfiltration** | Malicious instructions can trick the AI into leaking sensitive data, such as credentials or private project materials, to an external domain, bypassing security checks like `.gitignore` restrictions. | Google Antigravity IDE | [Mindgard Disclosures](https://mindgard.ai/disclosures/) |
| **Trust Persistence** | A flaw allows a malicious workspace to embed code in a global configuration directory that executes every time the application launches, creating a persistent backdoor that survives uninstallation and reinstallation. | Google Antigravity IDE | [Forced Descent: Google Antigravity Persistent Code Execution](https://mindgard.ai/blog/forced-descent-google-antigravity-persistent-code-execution) |
| **Trust Persistence** | The trust model in some IDEs is misleading, as core functionality requires marking a workspace as "trusted," effectively making trust an entry point to the product rather than a deliberate conferral of privileges. | Google Antigravity IDE | [Mindgard Disclosures](https://mindgard.ai/disclosures/) |


```
flowchart TB
    subgraph Legend[Legend]
        direction LR
        L1[🟦 Component] --- L2[⚠️ Vulnerability] --- L3[➡️ Data Flow] --- L4[🔴 Attack Surface]
    end

    subgraph External["🌐 External World"]
        direction TB
        E1[🌍 Malicious Repo<br/>GitHub/GitLab] 
        E2[👤 Attacker-Controlled<br/>Domain/Server]
        E3[🕸️ Malicious Website<br/>with CORS]
    end

    subgraph Workspace["📁 Workspace/Project (Untrusted)"]
        direction TB
        W1[📄 Source Code Files<br/>with Hidden Instructions]
        W2[⚙️ Config Files<br/>.vscode/settings.json]
        W3[📘 README.md<br/>with Prompt Injection]
        W4[📦 MCP Config Files<br/>.toml/.yaml]
        W5[🛠️ LSP Config Files<br/>.zed/settings.json]
        W6[🧰 Tool Definitions<br/>/tools/*.py]
        W7[🔧 Hooks Config<br/>pre_read_code]
        W8[📋 Prompt Templates<br/>.prompttemplate]
        W9[📂 Malicious Directory Names]
        W10[💣 Binary Payloads<br/>fake git/python]
        W11[⚙️ Git Configs<br/>.gitattributes]
        
        %% Vulnerabilities in Workspace
        W1 & W3 --- V_PI[⚠️ 2.x Prompt Injection]
        W2 & W4 & W5 & W6 & W7 & W8 & W11 --- V_CONFIG[⚠️ 1.x Configuration-Based<br/>Code Execution]
        W9 --- V_DIR[⚠️ 2.1 Adversarial<br/>Directory Names]
        W10 --- V_BIN[⚠️ 1.9 Binary Planting]
    end

    subgraph IDE["💻 AI IDE / Coding Assistant"]
        direction TB
        
        subgraph Trust_Boundary[🔒 Trust Boundary]
            TB1[🤖 AI Model/Agent<br/>with Prompt Context]
            TB2[📝 Prompt Processor<br/>& Template Loader]
            TB3[🔍 File Indexer<br/>& Context Builder]
        end
        
        subgraph Configuration["⚙️ Configuration System"]
            C1[📋 Workspace Config Loader<br/>- Auto-executes on load]
            C2[🛠️ Tool/Skill Manager<br/>- Auto-loads tools]
            C3[🔌 MCP Server Manager<br/>- Spawns processes]
            C4[📏 LSP Manager<br/>- Launches language servers]
            C5[🎣 Hook Manager<br/>- Executes on events]
            
            %% Vulnerabilities in Config
            C1 --- V1_6[⚠️ 1.6 App-Specific Config]
            C2 --- V1_3[⚠️ 1.3 Tools Auto-Loading]
            C3 --- V1_1[⚠️ 1.1 MCP Poisoning]
            C4 --- V1_2[⚠️ 1.2 LSP Config]
            C5 --- V1_5[⚠️ 1.5 Hooks Definition]
        end
        
        subgraph Execution["⚡ Execution Engine"]
            E1[💻 Terminal Command Executor<br/>with Filtering]
            E2[🔧 Safe Command Allowlist<br/>git diff, status, etc]
            E3[📂 File System Operations<br/>Read/Write]
            
            %% Vulnerabilities in Execution
            E1 --- V1_4[⚠️ 1.4 Argument Injection]
            E1 --- V1_8[⚠️ 1.8 Filtering Bypasses]
            E1 --- V1_11[⚠️ 1.11 Env Var Prefixing]
            E2 --- V1_10[⚠️ 1.10 Safe Executables Abuse]
        end
        
        subgraph Network["🌐 Local Network Services"]
            N1[🔌 Local HTTP Server<br/>Port dynamic]
            N2[🌍 Webview/Browser Preview]
            N3[📡 Model API Client]
            
            %% Vulnerability in Network Services
            N1 --- V1_13[⚠️ 1.13 Unauthenticated<br/>Local Network Services]
        end
        
        subgraph Persistence["💾 Persistence Layer"]
            P1[🌍 Global Config<br/>~/.config/]
            P2[📁 Workspace Cache]
            P3[🔐 Trust Database<br/>Approved Workspaces]
            
            %% Vulnerabilities in Persistence
            P1 --- V4_1[⚠️ 4.1 Persistent Backdoor]
            P2 & P3 --- V4_2[⚠️ 4.2 Two-Step Poisoning]
        end
        
        subgraph DataFlow["🔄 Data Flow Paths"]
            D1[📤 Exfiltration Channels]
            D2[📥 Injection Vectors]
        end
        
        %% Trust dialog
        TD[❓ Trust Dialog<br/>"Do you trust this workspace?"]
        
        %% Race condition
        V1_7[⚠️ 1.7 Initialization Race<br/>Executes BEFORE trust dialog] --> TD
    end

    subgraph Attack_Surfaces["🔴 Attack Surfaces"]
        A1[📥 Ingress - Project Import<br/>- Clone repo<br/>- Open folder]
        A2[📤 Egress - Network Exfiltration<br/>- DNS queries<br/>- HTTP requests<br/>- Ping traffic]
        A3[🔄 Lateral Movement<br/>- Config file writes<br/>- Global settings]
    end

    %% Connections from External to Workspace
    E1 -->|Clone/Download| A1
    A1 --> W1 & W2 & W3 & W4 & W5 & W6 & W7 & W8 & W9 & W10 & W11

    %% Workspace to IDE flows
    Workspace -->|Load on open| Configuration
    Workspace -->|Index for context| Trust_Boundary
    
    %% Trust Boundary flows
    Trust_Boundary -->|Uses| Execution
    Trust_Boundary -->|May modify| Configuration
    
    %% Configuration to Execution
    Configuration -->|Triggers| Execution
    
    %% Execution to DataFlow
    Execution -->|Read/Write| E3
    
    %% Execution to Network
    Execution -->|Can initiate| Network
    
    %% Execution to Persistence
    Execution -->|Can write| Persistence
    
    %% DataFlow connections
    TB1 -->|Context includes| Workspace
    
    %% Exfiltration paths
    Execution -->|DNS Queries| E2
    Execution -->|HTTP Requests| E2
    Execution -->|Ping Commands| E2
    
    Network -->|Ingress from malicious sites| E3
    Network -->|Egress data| E2
    
    Persistence -->|Persistence across sessions| P1
    
    %% Data Exfiltration vulnerabilities
    D1 --- V3_1[⚠️ 3.1 Exfil via DNS/Ping]
    D1 --- V3_2[⚠️ 3.2 Exfil via File Write]
    D1 --- V3_3[⚠️ 3.3 Exfil via Silent Terminal]
    
    %% Add remaining vulnerability numbers for completeness
    V2_3[⚠️ 2.3 PI → Config Modification] --- Configuration
    
    %% Styling
    classDef vuln fill:#ff9999,stroke:#ff0000,stroke-width:2px
    classDef component fill:#e1f5fe,stroke:#01579b
    classDef external fill:#fff3e0,stroke:#ff6f00
    classDef workspace fill:#f3e5f5,stroke:#4a148c
    classDef trust fill:#c8e6c9,stroke:#1b5e20
    classDef attack fill:#ffeb3b,stroke:#f57f17
    
    class V1_1,V1_2,V1_3,V1_4,V1_5,V1_6,V1_7,V1_8,V1_9,V1_10,V1_11,V1_12,V1_13,V2_1,V2_2,V2_3,V3_1,V3_2,V3_3,V4_1,V4_2,V4_3 vuln
    class E1,E2,E3 external
    class W1,W2,W3,W4,W5,W6,W7,W8,W9,W10,W11 workspace
    class TB1,TB2,TB3 trust
    class C1,C2,C3,C4,C5,E1,E2,E3,N1,N2,N3,P1,P2,P3 component
    class A1,A2,A3 attack
```

[!mermaid_20260312_7fcfcb.svg](mermaid_20260312_7fcfcb.svg)    


# AI IDE Attack Surfaces: Key Locations & Entry Points

This document maps the critical locations where AI-powered IDEs are vulnerable, from initial entry points to data exfiltration channels.

---

## 📥 Ingress Points (Where Attacks Enter)

| Ingress Point | Description | Related Attack Chains |
| :--- | :--- | :--- |
| **Malicious Repository Clone** | The primary attack vector. A user clones a repository containing poisoned files, unknowingly bringing the attack into their local environment. | Chain 1, Chain 3, Chain 5 |
| **Project Folder Open** | Simply opening a folder in the IDE can trigger the automatic loading of malicious configuration files located within it. | Chain 1, Chain 2 |
| **Git Pull/Update** | A previously "trusted" workspace receives a malicious update. When the user runs `git pull`, the new poisoned configuration is loaded, often without a new security prompt. | Chain 5 — "The Long Con" |

---

## 🔴 Critical Vulnerability Locations

### ⚙️ Configuration System (Auto-Executes on Load)
*These vulnerabilities exploit the IDE's habit of automatically processing settings files from the workspace.*

| Pattern ID | Vulnerability | How it Works |
| :--- | :--- | :--- |
| **1.1** | **MCP Configuration Poisoning** | Malicious MCP (Model Context Protocol) server config files in the workspace cause the IDE to spawn attacker-controlled processes. |
| **1.2** | **LSP Configuration** | Overriding Language Server Protocol (LSP) binary paths in workspace settings tricks the IDE into running malware when a file is opened. |
| **1.3** | **Tools/Skills Auto-Loading** | Tool definition files (e.g., Python scripts) placed in the workspace are automatically loaded and executed by the AI agent. |
| **1.5** | **Hooks Definition** | Scripts defined in workspace files run automatically on specific events, like when the AI reads or writes a file. |
| **1.6** | **App-Specific Config Auto-Execution** | Native configuration fields within the IDE that are designed to run commands (e.g., `notify`, `discoveryCommand`) can be exploited via workspace files. |

### 🚀 Execution Engine (Command Runner)
*These attacks manipulate how the AI builds and runs terminal commands.*

| Pattern ID | Vulnerability | How it Works |
| :--- | :--- | :--- |
| **1.4** | **Argument Injection** | Malicious arguments are injected into what the AI believes is a safe command, altering its behavior. |
| **1.8** | **Terminal Command Filtering Bypasses** | Using tricks like newline characters, shell expansion, or manipulating allowlisted commands (e.g., `find -exec`) to sneak past safety filters. |
| **1.10** | **Safe Executables with In-Workspace Config** | Making a normally "safe" command (like `git diff`) dangerous by changing its configuration file (e.g., `.gitattributes`) in the project to execute arbitrary code. |
| **1.11** | **Environment Variable Prefixing** | Using environment variables (`VAR=value command`) to bypass command blocklists or to inject malicious libraries via `LD_PRELOAD`. |

### 🌐 Local Network Services (The Hidden Server)
*Some AI tools start a local web server, creating a powerful but often unsecured attack surface.*

| Pattern ID | Vulnerability | How it Works |
| :--- | :--- | :--- |
| **1.13** | **Unauthenticated Local Network Services** | The IDE starts an HTTP server on `localhost` that listens for commands. |
| | **🔓 Ingress (Entry)** | Any local process, or even a website the user visits (via permissive CORS), can send commands to this server. |
| | **📤 Egress (Exit)** | The server can make outbound requests to the internet, sending stolen data to an attacker. |
| | **🔑 Key Issue** | No authentication is required—the server provides complete open access to anyone who can reach it. |

### 🔁 Persistence Layer (Survives Restarts)
*These attacks ensure the malware survives even after the project is closed or the IDE is restarted.*

| Pattern ID | Vulnerability | How it Works |
| :--- | :--- | :--- |
| **4.1** | **Persistent Backdoor via Global Config** | Malicious code is written to a global configuration directory (e.g., `~/.config/`), causing it to execute every time the IDE launches, even after a full uninstall/reinstall. |
| **4.2** | **Two-Step Configuration Poisoning (TOCTOU)** | A user approves a harmless-looking config file. The attacker later updates it via a `git commit`. When the user does a `git pull`, the now-malicious config loads without re-approval. |
| **4.3** | **Hidden Payload in Approved Commands** | A command that the user has previously approved contains hidden malicious code (e.g., using invisible characters) that executes later without a new approval prompt. |

### 🛡️ The Trust Boundary (The Critical Moment)
*The main point of user control, and how attackers bypass it.*

| Pattern ID | Vulnerability | How it Works |
| :--- | :--- | :--- |
| **1.7** | **Initialization Race Condition** | Malicious code executes **BEFORE** the "Do you trust this folder?" dialog is even shown to the user. |
| | **⚙️ Location** | This occurs in the startup sequence, specifically between "load workspace configurations" and "ask user for trust." It exploits a timing window during IDE initialization. |

---

## 📤 Egress Points (Where Data Leaves)

Once stolen, data is sent out through various channels. Attackers will try different paths if one is blocked.

| Egress Channel | Method | Description |
| :--- | :--- | :--- |
| **DNS Queries** | `ping`, `nslookup`, `dig` | Data is encoded into subdomains (e.g., `stolen-api-key.attacker.com`) and sent via seemingly benign DNS lookups, often bypassing HTTP firewalls. |
| **HTTP/HTTPS** | Direct web requests | Data is sent directly to an attacker-controlled server via standard HTTP requests, often hidden in image URLs or API calls. |
| **Model Provider Calls** | API Redirect | The AI tool's settings are changed so that all prompts and data are sent to the attacker's fake API server instead of the real one (e.g., OpenAI). |
| **Git Operations** | Remote URLs | Data is exfiltrated by including it in the URL of a `git push` command to a malicious remote repository. |
| **Package Manager Requests** | `pip`, `npm` installs | The AI is tricked into installing a malicious package, which then sends data back during its installation script. |

---

## 🔄 Attack Chains Mapped to Diagram

### Chain 1 — "The Classic"
*The most common path from repository clone to code execution.*
```
E1 (Clone Malicious Repo)
→ W1 (Project contains code with Prompt Injection)
→ TB1 (AI reads the poisoned file)
→ E3 (AI writes a new file)
→ C1 (The written file modifies a config, like settings.json)
→ E1 (Config change triggers command execution)
```

### Chain 3 — "The Exfil Express"
*The shortest path from repository clone to data theft.*
```
E1 (Clone Malicious Repo)
→ W3 (README.md file contains Prompt Injection)
→ TB1 (AI reads the README and follows the instruction)
→ E1 (AI runs a terminal command, like ping)
→ DNS Queries (Data is sent to attacker server)
→ E2 (Attacker collects the data)
```

### Chain 5 — "The Long Con"
*A time-delayed attack that abuses trust.*
```
P3 (User approves a BENIGN config in a trusted workspace)
→ (Time passes...)
→ E1 (Attacker updates the remote repository with malicious config)
→ git pull (User updates their local workspace)
→ W2 (The new, malicious config is loaded)
→ C1 (The config is processed WITHOUT re-approval, as the path is "trusted")
→ E1 (The malicious config executes commands)
```

---

## 🛡️ Trust Boundaries & The Illusion of Safety

The main user-facing security control is the **Trust Dialog** ("Do you trust the authors of the files in this folder?"). However, this boundary is porous and can be bypassed by:

1.  **Race Conditions (1.7):** Code can execute in the window *before* the dialog appears.
2.  **Auto-Execution (1.1, 1.3, 1.5):** Many configurations are processed automatically during the workspace load phase, *before* or *without* a trust decision being enforced.
3.  **Global Persistence (4.1):** Attacks that escape the local workspace and write to global configuration directories survive outside the workspace trust model entirely, affecting all future sessions.

This reveals that AI IDEs have multiple concentric trust zones. Vulnerabilities exist at every layer where untrusted workspace data interacts with trusted IDE functionality.



