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
        L5[🛡️ Security Gate G1-G9] --- L6[❌ Blocks Pattern]
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
        W9 --- V2_1[⚠️ 2.1 Adversarial<br/>Directory Names]
        W10 --- V1_9[⚠️ 1.9 Binary Planting]
    end

    subgraph IDE["💻 AI IDE / Coding Assistant"]
        direction TB
        
        subgraph Security_Gates["🛡️ Security Gates (G1-G9)"]
            G1[<b>G1 — Config Approval</b><br/>Nothing auto-executes without approval]
            G2[<b>G2 — Initialization Safety</b><br/>No execution before trust dialog]
            G3[<b>G3 — Trust Integrity</b><br/>Content hash binding, re-approval on change]
            G4[<b>G4 — File Write Restrictions</b><br/>Agent can't modify own config]
            G5[<b>G5 — Command Robustness</b><br/>Parsing handles shell tricks]
            G6[<b>G6 — Binary Security</b><br/>Workspace not in search path]
            G7[<b>G7 — Input Sanitization</b><br/>Strip invisible Unicode]
            G8[<b>G8 — Outbound Controls</b><br/>Block/gate all external requests]
            G9[<b>G9 — Network Security</b><br/>Auth required for local services]
        end
        
        subgraph Trust_Boundary[🔒 Trust Boundary]
            TB1[🤖 AI Model/Agent<br/>with Prompt Context]
            TB2[📝 Prompt Processor<br/>& Template Loader]
            TB3[🔍 File Indexer<br/>& Context Builder]
        end
        
        subgraph Configuration["⚙️ Configuration System"]
            direction TB
            C1[📋 Workspace Config Loader]
            C2[🛠️ Tool/Skill Manager]
            C3[🔌 MCP Server Manager]
            C4[📏 LSP Manager]
            C5[🎣 Hook Manager]
            
            %% Vulnerabilities with Gate Mapping
            C1 --- V1_6[⚠️ 1.6 App-Specific Config<br/><b>❌ Blocked by: G1</b>]
            C2 --- V1_3[⚠️ 1.3 Tools Auto-Loading<br/><b>❌ Blocked by: G1</b>]
            C3 --- V1_1[⚠️ 1.1 MCP Poisoning<br/><b>❌ Blocked by: G1, G3</b>]
            C4 --- V1_2[⚠️ 1.2 LSP Config<br/><b>❌ Blocked by: G1</b>]
            C5 --- V1_5[⚠️ 1.5 Hooks Definition<br/><b>❌ Blocked by: G1</b>]
        end
        
        subgraph Execution["⚡ Execution Engine"]
            E1[💻 Terminal Command Executor<br/>with Filtering]
            E2[🔧 Safe Command Allowlist<br/>git diff, status, etc]
            E3[📂 File System Operations<br/>Read/Write]
            
            %% Vulnerabilities with Gate Mapping
            E1 --- V1_4[⚠️ 1.4 Argument Injection<br/><b>❌ Blocked by: G5</b>]
            E1 --- V1_8[⚠️ 1.8 Filtering Bypasses<br/><b>❌ Blocked by: G5</b>]
            E1 --- V1_11[⚠️ 1.11 Env Var Prefixing<br/><b>❌ Blocked by: G5</b>]
            E2 --- V1_10[⚠️ 1.10 Safe Executables Abuse<br/><b>❌ Blocked by: G5</b>]
        end
        
        subgraph Network["🌐 Local Network Services"]
            N1[🔌 Local HTTP Server]
            N2[🌍 Webview/Browser Preview]
            N3[📡 Model API Client]
            
            %% Vulnerabilities with Gate Mapping
            N1 --- V1_13[⚠️ 1.13 Unauthenticated Local Services<br/><b>❌ Blocked by: G9</b>]
        end
        
        subgraph Persistence["💾 Persistence Layer"]
            P1[🌍 Global Config<br/>~/.config/]
            P2[📁 Workspace Cache]
            P3[🔐 Trust Database<br/>Approved Workspaces]
            
            %% Vulnerabilities with Gate Mapping
            P1 --- V4_1[⚠️ 4.1 Persistent Backdoor<br/><b>❌ Blocked by: G3</b>]
            P2 & P3 --- V4_2[⚠️ 4.2 Two-Step Poisoning<br/><b>❌ Blocked by: G3</b>]
        end
        
        %% Trust dialog with gate mapping
        TD[❓ Trust Dialog<br/>"Do you trust this workspace?"]
        V1_7[⚠️ 1.7 Initialization Race<br/><b>❌ Blocked by: G2</b>] --> TD
    end

    subgraph Data_Exfiltration["📤 Data Exfiltration Channels"]
        D1[DNS Queries<br/>ping/nslookup/dig]
        D2[HTTP Requests<br/>curl/wget/fetch]
        D3[Markdown Images<br/>![]()]
        D4[Mermaid Diagrams<br/>external image refs]
        D5[Model API Calls<br/>to attacker server]
        D6[Git Operations<br/>remote URLs]
        
        %% Exfiltration vulnerabilities with gate mapping
        D1 --- V3_1[⚠️ 3.1 Exfil via DNS/Ping<br/><b>❌ Blocked by: G8</b>]
        D2 --- V3_3[⚠️ 3.3 Exfil via Silent Terminal<br/><b>❌ Blocked by: G8</b>]
        D3 & D4 --- V3_4[⚠️ 3.4 Exfil via Rendered Content<br/><b>❌ Blocked by: G8</b>]
        D5 --- V3_5[⚠️ 3.5 Model Provider Redirect<br/><b>❌ Blocked by: G1, G8</b>]
        D6 --- V3_6[⚠️ 3.6 Exfil via Git<br/><b>❌ Blocked by: G8</b>]
    end

    subgraph Attack_Surfaces["🔴 Attack Surfaces with Gates"]
        A1[📥 Ingress - Project Import<br/>- Clone repo<br/>- Open folder<br/><b>🛡️ Gates: G1, G2, G6, G7</b>]
        A2[📤 Egress - Network Exfiltration<br/>- DNS/HTTP/Ping<br/><b>🛡️ Gates: G8, G9</b>]
        A3[🔄 Lateral Movement<br/>- Config writes<br/>- Global settings<br/><b>🛡️ Gates: G3, G4</b>]
    end

    %% Connections from External to Workspace
    E1 -->|Clone/Download| A1
    A1 --> W1 & W2 & W3 & W4 & W5 & W6 & W7 & W8 & W9 & W10 & W11

    %% Workspace to IDE flows with gates
    Workspace -->|Load on open| G1
    G1 --> Configuration
    
    Workspace -->|Index for context| G7
    G7 --> Trust_Boundary
    
    Workspace -->|Binary search| G6
    G6 --> Execution
    
    %% Trust Boundary flows
    Trust_Boundary -->|Uses| Execution
    Trust_Boundary -->|May modify| G4
    G4 --> Configuration
    
    %% Configuration to Execution
    Configuration -->|Triggers| G5
    G5 --> Execution
    
    %% Execution to DataFlow with gates
    Execution -->|Initiates outbound| G8
    G8 --> Data_Exfiltration
    
    %% Execution to Persistence with gates
    Execution -->|Writes to| G3
    G3 --> Persistence
    
    %% Network security gate
    Network -->|Local access| G9
    G9 --> Execution
    
    %% Add remaining vulnerability patterns with gate mapping
    V2_2[⚠️ 2.2 Prompt Template Auto-Loading<br/><b>❌ Blocked by: G1</b>] --- G1
    V2_3[⚠️ 2.3 PI → Config Modification<br/><b>❌ Blocked by: G4</b>] --- G4
    V2_4[⚠️ 2.4 Rules Override<br/><b>❌ Blocked by: G1</b>] --- G1
    V2_5[⚠️ 2.5 Hidden Instructions (invisible chars)<br/><b>❌ Blocked by: G7</b>] --- G7
    V3_2[⚠️ 3.2 Exfil via File Write<br/><b>❌ Blocked by: G4, G8</b>] --- G4
    V4_3[⚠️ 4.3 Hidden Payload in Approved Commands<br/><b>❌ Blocked by: G3</b>] --- G3
    V1_12[⚠️ 1.12 IDE Settings Abuse<br/><b>❌ Blocked by: G1</b>] --- G1

    %% Styling
    classDef vuln fill:#ff9999,stroke:#ff0000,stroke-width:2px
    classDef component fill:#e1f5fe,stroke:#01579b
    classDef external fill:#fff3e0,stroke:#ff6f00
    classDef workspace fill:#f3e5f5,stroke:#4a148c
    classDef trust fill:#c8e6c9,stroke:#1b5e20
    classDef attack fill:#ffeb3b,stroke:#f57f17
    classDef gate fill:#90EE90,stroke:#006400,stroke-width:2px
    classDef exfil fill:#FFB6C1,stroke:#8B0000
    
    class V1_1,V1_2,V1_3,V1_4,V1_5,V1_6,V1_7,V1_8,V1_9,V1_10,V1_11,V1_12,V1_13,V2_1,V2_2,V2_3,V2_4,V2_5,V3_1,V3_2,V3_3,V3_4,V3_5,V3_6,V4_1,V4_2,V4_3 vuln
    class E1,E2,E3 external
    class W1,W2,W3,W4,W5,W6,W7,W8,W9,W10,W11 workspace
    class TB1,TB2,TB3 trust
    class C1,C2,C3,C4,C5,E1,E2,E3,N1,N2,N3,P1,P2,P3 component
    class A1,A2,A3 attack
    class G1,G2,G3,G4,G5,G6,G7,G8,G9 gate
    class D1,D2,D3,D4,D5,D6 exfil
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


# Critical Security Gates Coverage Summary

Based on the checklist's mapping, this document shows how 9 key security gates block the 25 vulnerability patterns in AI IDEs.

---

## 🚪 Gate Coverage Matrix

| Gate | What It Blocks | Priority |
| :--- | :--- | :--- |
| **G1 — Config Approval** | **9 patterns**: 1.1 (MCP), 1.2 (LSP), 1.3 (Tools), 1.5 (Hooks), 1.6 (App Config), 1.12 (IDE Settings), 2.2 (Prompt Templates), 2.4 (Rules Override), 3.5 (Model Redirect) | **Highest** — stops most zero-click config attacks |
| **G8 — Outbound Controls** | **6 patterns**: 3.1 (DNS), 3.2 (File Write), 3.3 (Silent Terminal), 3.4 (Rendered Content), 3.5 (Model Redirect), 3.6 (Git) | **High** — blocks all exfiltration channels |
| **G5 — Command Robustness** | **4 patterns**: 1.4 (Arg Injection), 1.8 (Filter Bypass), 1.10 (Safe Exec Abuse), 1.11 (Env Var Prefix) | **High** — prevents terminal-based attacks |
| **G7 — Input Sanitization** | **2 patterns**: 2.1 (Adversarial Dirs), 2.5 (Hidden Instructions) — *but amplifies all prompt injection defenses* | **High** — reduces all prompt injection chains |
| **G4 — File Write Restrictions** | **2 patterns**: 2.3 (PI → Config Mod), 3.2 (Exfil via File) — *breaks the classic PI → code exec chain* | **High** — stops most common escalation path |
| **G3 — Trust Integrity** | **4 patterns**: 1.1 (two-step variant), 4.1 (Persistent), 4.2 (Two-Step), 4.3 (Hidden Payload) | **Medium** — prevents post-approval attacks |
| **G2 — Initialization Safety** | **1 pattern**: 1.7 (Race Condition) — *upgrades all config attacks to zero-click if missing* | **Medium** — prevents startup execution |
| **G6 — Binary Security** | **1 pattern**: 1.9 (Binary Planting) | **Medium** — stops planted executables |
| **G9 — Network Security** | **1 pattern**: 1.13 (Local Network Services) | **Medium** — secures local endpoints |

---

## 🎯 Priority Summary

| Priority Level | Gates | Patterns Blocked |
| :--- | :--- | :--- |
| **Highest** | G1 | 9 patterns |
| **High** | G8, G5, G7, G4 | 14 patterns (some overlap) |
| **Medium** | G3, G2, G6, G9 | 6 patterns |

---

## ✅ If You Can Only Do Five Things

*From the Checklist's top recommendations:*

| Priority | Gate | Why It Matters |
| :---: | :--- | :--- |
| **1** | **G1 — Config Approval** | Nothing auto-executes from workspace without approval. **Blocks 9 patterns** including all config-based code execution. |
| **2** | **G8 — Outbound Controls** | Block all outbound requests from rendering and tool features. **Blocks all 6 exfiltration patterns.** |
| **3** | **G5 — Command Robustness** | Harden command parsing against injection and bypasses. **Blocks 4 terminal-based attack patterns.** |
| **4** | **G4 — File Write Restrictions** | Agent cannot write to its own config files. **Breaks the classic PI → code execution chain.** |
| **5** | **G7 — Input Sanitization** | Strip invisible Unicode from LLM input. **Defeats covert prompt injection delivery across all chains.** |

---

## 🔗 Attack Chains Broken by These Gates

| Attack Chain | Critical Gates That Break It |
| :--- | :--- |
| **Chain 1 — "The Classic"** (Repo → PI → File Write → Config Mod → Code Exec) | **G4** (File Write Restrictions) breaks the chain at the critical "File Write" step. **G1** (Config Approval) blocks the final "Config Mod" from executing. |
| **Chain 3 — "The Exfil Express"** (Repo → PI in README → Terminal → DNS → Attacker) | **G8** (Outbound Controls) blocks the DNS/HTTP egress. **G5** (Command Robustness) can block the terminal command itself. |
| **Chain 5 — "The Long Con"** (Benign config approved → malicious git pull → loads without re-approval) | **G3** (Trust Integrity) prevents configs from loading without re-approval after a change. **G1** (Config Approval) ensures all configs, even updated ones, require approval. |

---

## 📊 Coverage Visualization

```
G1 ────────────────── Blocks 9 config-based patterns
╲
╲
G4 ───╲───────────── Breaks the PI → Code Exec chain
╲
G5 ─────╲─────────── Blocks 4 terminal attack patterns
╲
G7 ───────╲───────── Sanitizes input, amplifies all PI defenses
╲
G8 ──────────────── Blocks all 6 exfiltration channels
```


**Results in defense-in-depth across:**
- 📥 **Ingress** (G7, G1)
- ⚙️ **Execution** (G5, G4)
- 📤 **Egress** (G8)
- 🔁 **Persistence** (G3)
- 🚀 **Initialization** (G2)

---

This gate-based approach shows that a relatively small number of well-placed security controls can block the vast majority of attack patterns, with **just five gates covering 80%+ of the vulnerability surface**.

# Mapping Each Sandbox Layer to the 9 Security Gates

This document shows how different sandboxing technologies enforce specific security gates, creating a defense-in-depth strategy against the 25 vulnerability patterns.

---

## 🏗️ Sandbox Layer Matrix

| Layer | Technology | Gates Enforced | Attack Patterns Blocked |
| :--- | :--- | :--- | :--- |
| **L1: Git Worktree Fencing** | Content-addressed worktrees, read-only mounts | **G3** (Trust Integrity) | **1.1 (two-step), 4.2, 4.3** — prevents tampering after approval |
| **L2: Bubblewrap** | Linux namespaces, seccomp-bpf | **G1, G2, G6** | **1.1–1.12** (all config-based code exec), **1.9** (binary planting) |
| **L3: gVisor** | Userspace kernel, system call interception | **G5, G8** | **1.4, 1.8, 1.11** — blocks argument injection and filter bypasses |
| **L4: Extism WASM** | Capability-based permissions, manifest validation | **G1, G4, G5** | **2.3, 3.2** — prevents config modification and file exfiltration |
| **L5: Seatbelt** | macOS sandbox profiles | **G1, G2, G6** | Same as Bubblewrap but for macOS |
| **L6: Network Gates** | iptables/nftables/pf, DNS filtering | **G8** | **3.1, 3.3, 3.4, 3.5, 3.6** — blocks all exfiltration channels |
| **L7: MicroVM** | Firecracker, complete isolation | **ALL GATES** | **Everything** — ultimate blast radius containment |

---

## 🛡️ Defense-in-Depth Strategy

The key insight is **layered, overlapping controls**. No single layer is perfect, but together they create multiple hurdles for an attacker.

### How Layers Catch What Others Miss

| If an attacker bypasses... | ...this layer catches it |
| :--- | :--- |
| **G1** (Config Approval) by exploiting a race condition | **G2** (Initialization Safety) prevents startup execution |
| **G2** through social engineering | **G3** (Trust Integrity) detects tampering after approval |
| **G1–G3** by modifying configs via prompt injection | **G4** (File Write Restrictions) blocks writes to config directories |
| **G1–G4** and tries terminal commands | **G5** (Command Robustness) blocks injection and bypasses |
| **G1–G5** by planting binaries | **G6** (Binary Security) prevents execution of planted executables |
| **G1–G6** by hiding instructions | **G7** (Input Sanitization) strips invisible Unicode and adversarial content |
| **G1–G7** and tries to steal data | **G8** (Outbound Controls) blocks DNS, HTTP, and all exfiltration channels |
| **G1–G8** by attacking local services | **G9** (Network Security) requires authentication for local endpoints |
| **All of the above** | **L7: MicroVM** contains the blast radius to a disposable environment |

---

## 🔄 Visualizing the Layered Defense

```
ATTACK SURFACE
│
▼
┌─────────────────────────────────────┐
│ L1: Git Worktree Fencing (G3) │ ◄── Prevents post-approval tampering
│ └───────────────────────────────── │
│ L2: Bubblewrap / L5: Seatbelt │ ◄── Blocks config execution & binary planting
│ └──────────────────────────────── │
│ L3: gVisor (G5, G8) │ ◄── Stops command injection & filter bypass
│ └─────────────────────────────── │
│ L4: Extism WASM (G1, G4, G5) │ ◄── Prevents config writes & file exfil
│ └────────────────────────────── │
│ L6: Network Gates (G8) │ ◄── Blocks all data egress channels
│ └───────────────────────────── │
│ L7: MicroVM (ALL GATES) │ ◄── Ultimate containment
└─────────────────────────────────────┘
│
▼
BLAST RADIUS CONTAINED
```


---

## 📊 Complete Gate-to-Layer Mapping

| Gate | Primary Enforcers | Backup Enforcers |
| :--- | :--- | :--- |
| **G1 — Config Approval** | L2 (Bubblewrap), L4 (WASM), L5 (Seatbelt) | L7 (MicroVM) |
| **G2 — Initialization Safety** | L2, L5 | L7 |
| **G3 — Trust Integrity** | L1 (Git Worktree) | L7 |
| **G4 — File Write Restrictions** | L4 (WASM) | L7 |
| **G5 — Command Robustness** | L3 (gVisor), L4 (WASM) | L7 |
| **G6 — Binary Security** | L2, L5 | L7 |
| **G7 — Input Sanitization** | *Application Layer* | L7 |
| **G8 — Outbound Controls** | L3 (gVisor), L6 (Network Gates) | L7 |
| **G9 — Network Security** | L6 | L7 |

---

## 🎯 Why This Works

This layered approach solves the fundamental problem of AI agent security: **decoupling the agent from the developer's filesystem**.

| Challenge | Solution |
| :--- | :--- |
| Agents need to read code | Read-only mounts (L1) with content-addressed storage |
| Agents need to run tools | Sandboxed execution with seccomp (L2, L5) |
| Agents need network access | gVisor interception + network filters (L3, L6) |
| Agents need to write files | Capability-based WASM permissions (L4) |
| Agents might get compromised | MicroVM containment (L7) — throw away the environment |

---

## 🔑 The Key Insight

> **When an attack succeeds (and some will), the blast radius is contained to an environment you can throw away.**

This is the answer: decouple the agent from the developer's filesystem through multiple layers of sandboxing, each mapped to specific attack patterns and security gates. No single layer is perfect, but together they create a defense where:
- Each layer covers the gaps of the layers above
- Attackers must bypass multiple independent technologies
- The most sensitive assets (global configs, SSH keys, production code) are never exposed to the agent environment


# AI IDE Security Framework: Attack Classes & Defenses

This framework categorizes AI IDE attacks into four classes based on severity and impact, mapping each to the affected vulnerability patterns and defensive gates.

---

## 🎯 Attack Class Matrix

| ATTACK CLASS | EXPLANATION AND CONSEQUENCES | AFFECTED VULNERABILITY PATTERNS | DEFENSE GATES | DEFENSE STRENGTH |
| :--- | :--- | :--- | :--- | :--- |
| **System Modification** | The most severe class. Attackers gain arbitrary code execution on the host machine. Can lead to full system compromise, ransomware, persistent backdoors, and lateral movement across the developer's infrastructure. **Consequences: Severe** | **1.1-1.13** (All Arbitrary Code Execution): MCP Poisoning, LSP Config, Tools Auto-Loading, Argument Injection, Hooks, App-Specific Config, Race Conditions, Filter Bypasses, Binary Planting, Safe Executable Abuse, Env Var Prefixing, IDE Settings Abuse, Local Network Services<br><br>**2.3** (PI → Config Modification)<br><br>**4.1-4.3** (All Trust Persistence) | **G1** (Config Approval)<br>**G2** (Init Safety)<br>**G3** (Trust Integrity)<br>**G4** (File Write Restrictions)<br>**G5** (Command Robustness)<br>**G6** (Binary Security)<br>**G9** (Network Security) | **Strong**<br>(Multiple overlapping gates) |
| **Invasion of Privacy** | Data exfiltration attacks. If you value your IP, API keys, or customer data, this class is particularly odious. Attackers steal environment variables, source code, credentials, and proprietary algorithms. Can include forging requests to internal services. **Consequences: Moderate to Severe** | **3.1** (DNS/Ping Exfil)<br>**3.2** (File Write Exfil)<br>**3.3** (Silent Terminal Exfil)<br>**3.4** (Rendered Content Exfil)<br>**3.5** (Model Provider Redirect)<br>**3.6** (Git Exfil)<br><br>**2.1-2.2** (Adversarial Dirs, Prompt Templates — as delivery mechanisms) | **G7** (Input Sanitization)<br>**G8** (Outbound Controls)<br>**G4** (File Write Restrictions) | **Strong**<br>(Comprehensive outbound filtering) |
| **Denial of Service** | Resource exhaustion attacks. These can bring a developer's machine to a standstill, halt CI/CD pipelines, or consume excessive cloud credits. May require reboot or VM termination. Includes fork bombs, memory exhaustion, disk filling, and API rate limit exhaustion. **Consequences: Moderate** | *N/A in original 25 (But implied by argument injection allowing `:(){ :|:& };:`, disk writes, or cryptominers)*<br><br>**1.4** (Argument Injection — can launch fork bombs)<br>**1.8** (Filter Bypasses — can run resource hogs)<br>**1.3** (Tools Auto-Loading — can load infinite loops) | **G5** (Command Robustness — blocks fork bombs)<br>**G1** (Config Approval — blocks crypto miners)<br>Resource Limits in Bubblewrap/gVisor | **Weak**<br>(Java's assessment holds true — perfect prevention is difficult) |
| **Antagonism** | Merely annoying attacks. The most commonly encountered class. Includes `rm -rf /` jokes that fail due to permissions, infinite notification popups, changing editor themes, playing sounds, or deleting temporary files. May require restart of IDE. **Consequences: Light to Moderate** | **2.1** (Adversarial Directory Names — can trick AI into deleting files)<br>**2.5** (Hidden Instructions — can make AI behave erratically)<br>**1.10** (Safe Executable Abuse — can make `git status` delete files) | **G7** (Input Sanitization)<br>**G4** (File Write Restrictions)<br>**G5** (Command Robustness) | **Weak**<br>(Annoyance is hard to prevent without breaking functionality) |

---

## 📊 Attack Class Summary

| Attack Class | Severity | Number of Affected Patterns | Primary Defense Gates | Defense Strength |
| :--- | :---: | :---: | :--- | :---: |
| **System Modification** | 🔴 Severe | ~20 patterns | G1, G2, G3, G4, G5, G6, G9 | ✅ Strong |
| **Invasion of Privacy** | 🟠 Moderate to Severe | ~8 patterns | G7, G8, G4 | ✅ Strong |
| **Denial of Service** | 🟡 Moderate | ~3 patterns (implied) | G5, G1, Resource Limits | ⚠️ Weak |
| **Antagonism** | 🟢 Light to Moderate | ~3 patterns | G7, G4, G5 | ⚠️ Weak |

---

## 🔄 Attack Class Breakdown by Vulnerability Category

```
SYSTEM MODIFICATION (Severe)
├── 1.1-1.13 All Code Execution patterns
├── 2.3 PI → Config Modification
└── 4.1-4.3 All Trust Persistence
│
▼
Protected by: G1, G2, G3, G4, G5, G6, G9

INVASION OF PRIVACY (Moderate-Severe)
├── 3.1 DNS/Ping Exfil
├── 3.2 File Write Exfil
├── 3.3 Silent Terminal Exfil
├── 3.4 Rendered Content Exfil
├── 3.5 Model Provider Redirect
├── 3.6 Git Exfil
└── 2.1-2.2 Delivery Mechanisms
│
▼
Protected by: G7, G8, G4

DENIAL OF SERVICE (Moderate)
├── 1.4 Argument Injection (fork bombs)
├── 1.8 Filter Bypasses (resource hogs)
└── 1.3 Tools Auto-Loading (infinite loops)
│
▼
Protected by: G5, G1, Resource Limits
⚠️ Perfect prevention difficult

ANTAGONISM (Light-Moderate)
├── 2.1 Adversarial Directory Names
├── 2.5 Hidden Instructions
└── 1.10 Safe Executable Abuse
│
▼
Protected by: G7, G4, G5
⚠️ Annoyance hard to prevent

```


---

## 🛡️ Defense Coverage by Attack Class

| Defense Gate | System Modification | Invasion of Privacy | Denial of Service | Antagonism |
| :--- | :---: | :---: | :---: | :---: |
| **G1 — Config Approval** | ✅ | ⬜ | ✅ | ⬜ |
| **G2 — Init Safety** | ✅ | ⬜ | ⬜ | ⬜ |
| **G3 — Trust Integrity** | ✅ | ⬜ | ⬜ | ⬜ |
| **G4 — File Write Restrictions** | ✅ | ✅ | ⬜ | ✅ |
| **G5 — Command Robustness** | ✅ | ⬜ | ✅ | ✅ |
| **G6 — Binary Security** | ✅ | ⬜ | ⬜ | ⬜ |
| **G7 — Input Sanitization** | ⬜ | ✅ | ⬜ | ✅ |
| **G8 — Outbound Controls** | ⬜ | ✅ | ⬜ | ⬜ |
| **G9 — Network Security** | ✅ | ⬜ | ⬜ | ⬜ |
| **Resource Limits** | ⬜ | ⬜ | ✅ | ⬜ |

---

## 🔑 Key Insights

| Insight | Explanation |
| :--- | :--- |
| **Most severe class is best defended** | System Modification attacks have **7 overlapping gates**, making them the hardest to successfully execute. |
| **Privacy invasions have strong defenses** | G8 (Outbound Controls) combined with G4 and G7 creates comprehensive exfiltration prevention. |
| **Denial of Service is the weak spot** | As noted in the original assessment, perfect prevention of resource exhaustion is "difficult" — attackers can always try to consume more resources than you can limit. |
| **Antagonism is the hardest to eliminate** | Preventing annoyance without breaking legitimate functionality is nearly impossible. Some level of "rm -rf /" jokes that fail safely may be acceptable. |
| **G4 is the multi-class MVP** | File Write Restrictions appear in **3 out of 4 attack classes**, making it one of the most valuable single defenses. |

---

## 🎯 Prioritization by Attack Class

| Priority | Attack Class | Rationale |
| :---: | :--- | :--- |
| **1** | **System Modification** | Highest severity, but also best defended — maintain strong gates |
| **2** | **Invasion of Privacy** | High severity, excellent defenses available — implement G8 strictly |
| **3** | **Denial of Service** | Moderate severity, weak defenses — accept residual risk |
| **4** | **Antagonism** | Low severity, hard to prevent — focus on detection, not prevention |

---

This framework shows that **the most severe attacks are also the best defended**, while the most common annoyances are the hardest to prevent completely — a pragmatic trade-off in AI IDE security.







## Architecture Diagram: Defense-in-Depth for AI IDEs

```
flowchart TB
    subgraph Legend[Legend]
        direction LR
        L1[🛡️ Security Layer] --- L2[⚠️ Attack Class] --- L3[🔴 Vulnerability Pattern] --- L4[🚪 Security Gate]
    end

    subgraph External_World["🌐 Untrusted External World"]
        direction TB
        E1[📦 Malicious Repository<br/>GitHub/GitLab/NPM]
        E2[👤 Attacker Server<br/>C2 & Exfiltration]
        E3[🕸️ Malicious Website<br/>CORS Attacks]
    end

    subgraph Attack_Classes["⚠️ Attack Classes (Inspired by Java Security Model)"]
        direction TB
        
        subgraph AC1[<b>System Modification</b><br/>Severity: 🔴🔴🔴 SEVERE]
            direction TB
            AC1_P1[1.1 MCP Poisoning]
            AC1_P2[1.2 LSP Config]
            AC1_P3[1.3 Tools Auto-Loading]
            AC1_P4[1.4 Argument Injection]
            AC1_P5[1.5 Hooks Definition]
            AC1_P6[1.6 App-Specific Config]
            AC1_P7[1.7 Race Condition]
            AC1_P8[1.8 Filter Bypasses]
            AC1_P9[1.9 Binary Planting]
            AC1_P10[1.10 Safe Exec Abuse]
            AC1_P11[1.11 Env Var Prefixing]
            AC1_P12[1.12 IDE Settings Abuse]
            AC1_P13[1.13 Local Network Services]
            AC1_P14[2.3 PI → Config Mod]
            AC1_P15[4.1 Persistent Backdoor]
            AC1_P16[4.2 Two-Step Poisoning]
            AC1_P17[4.3 Hidden Payload]
        end
        
        subgraph AC2[<b>Invasion of Privacy</b><br/>Severity: 🟠🟠 MODERATE-SEVERE]
            direction TB
            AC2_P1[3.1 DNS/Ping Exfil]
            AC2_P2[3.2 File Write Exfil]
            AC2_P3[3.3 Silent Terminal Exfil]
            AC2_P4[3.4 Rendered Content Exfil]
            AC2_P5[3.5 Model Provider Redirect]
            AC2_P6[3.6 Git Exfil]
            AC2_P7[2.1 Adversarial Dirs]
            AC2_P8[2.2 Prompt Templates]
        end
        
        subgraph AC3[<b>Denial of Service</b><br/>Severity: 🟡 MODERATE]
            direction TB
            AC3_P1[Fork Bombs via 1.4]
            AC3_P2[Crypto Miners via 1.3]
            AC3_P3[Disk Fill via 1.8]
            AC3_P4[API Exhaustion via 3.5]
        end
        
        subgraph AC4[<b>Antagonism</b><br/>Severity: 🟢 LIGHT]
            direction TB
            AC4_P1[File Deletion via 2.1]
            AC4_P2[UI Annoyances via 2.5]
            AC4_P3[Theme Changes via 1.12]
            AC4_P4[Sound via 1.8]
        end
    end

    subgraph Defense_Layers["🛡️ Defense-in-Depth Layers (Mapped to Java Security Model)"]
        direction TB
        
        subgraph L1_Pre_Execution["<b>L1: Pre-Execution Validation</b><br/>Gate: G7 - Input Sanitization"]
            direction TB
            L1_C1[🧹 Strip Invisible Unicode<br/>Remove zero-width chars]
            L1_C2[📁 Sanitize Directory Names<br/>Block adversarial names]
            L1_C3[🔍 Validate File Contents<br/>Scan for hidden instructions]
            L1_C4[✓ Content Hash Verification<br/>Detect tampering]
        end
        
        subgraph L2_Configuration_Gate["<b>L2: Configuration Approval Gate</b><br/>Gate: G1, G2, G3"]
            direction TB
            L2_C1[❓ Trust Dialog<br/>"Do you trust this workspace?"]
            L2_C2[🔒 No Auto-Execution<br/>All configs require approval]
            L2_C3[🔐 Content-Bound Trust<br/>Hash-based, not path-based]
            L2_C4[🔄 Re-approval on Change<br/>git pull triggers new approval]
        end
        
        subgraph L3_Execution_Sandbox["<b>L3: Execution Sandbox</b><br/>Gate: G4, G5, G6"]
            direction TB
            L3_C1[📦 Bubblewrap/gVisor<br/>System call interception]
            L3_C2[🔧 Command Filtering<br/>Argument sanitization]
            L3_C3[🚫 No Config Writes<br/>Agent can't modify own config]
            L3_C4[💾 Read-Only Filesystem<br/>Workspace mounted ro by default]
        end
        
        subgraph L4_Network_Isolation["<b>L4: Network Isolation</b><br/>Gate: G8, G9"]
            direction TB
            L4_C1[🚪 Network Gate<br/>iptables/pf filtering]
            L4_C2[🔌 Local Service Auth<br/>Tokens for localhost endpoints]
            L4_C3[🌐 DNS Filtering<br/>Block encoded exfiltration]
            L4_C4[🖼️ Content Security<br/>No external images in preview]
        end
        
        subgraph L5_Blast_Radius["<b>L5: Blast Radius Containment</b><br/>Gate: G3, G4, G6"]
            direction TB
            L5_C1[🧵 Git Worktree Fencing<br/>Immutable snapshots]
            L5_C2[🗑️ Disposable Environments<br/>MicroVMs throw away after use]
            L5_C3[🔐 No Persistence<br/>Global configs can't be modified]
            L5_C4[📊 Audit Logging<br/>All actions recorded]
        end
    end

    subgraph Security_Gates["🚪 Security Gates (G1-G9)"]
        direction TB
        G1[<b>G1 - Config Approval</b><br/>Blocks: 1.1,1.2,1.3,1.5,1.6,1.12,2.2,2.4,3.5]
        G2[<b>G2 - Init Safety</b><br/>Blocks: 1.7]
        G3[<b>G3 - Trust Integrity</b><br/>Blocks: 1.1(2-step),4.1,4.2,4.3]
        G4[<b>G4 - File Write Restrict</b><br/>Blocks: 2.3,3.2]
        G5[<b>G5 - Command Robustness</b><br/>Blocks: 1.4,1.8,1.10,1.11]
        G6[<b>G6 - Binary Security</b><br/>Blocks: 1.9]
        G7[<b>G7 - Input Sanitization</b><br/>Blocks: 2.1,2.5]
        G8[<b>G8 - Outbound Controls</b><br/>Blocks: 3.1,3.2,3.3,3.4,3.5,3.6]
        G9[<b>G9 - Network Security</b><br/>Blocks: 1.13]
    end

    subgraph Java_Style_Assessment["📊 Defense Strength Assessment (Java Security Model Style)"]
        direction TB
        JS1[<b>System Modification Defense: STRONG</b><br/>9 gates, 5 layers, multiple overlapping controls]
        JS2[<b>Invasion of Privacy Defense: STRONG</b><br/>Comprehensive outbound filtering at all egress points]
        JS3[<b>Denial of Service Defense: WEAK</b><br/>Resource limits help but perfect prevention difficult]
        JS4[<b>Antagonism Defense: WEAK</b><br/>Annoyance is subjective, hard to block without breaking UX]
    end

    %% Attack Flow
    E1 -->|Clone Repo| Attack_Classes
    E2 -->|Command & Control| Attack_Classes
    E3 -->|CORS Attack| Attack_Classes

    %% Attack Classes trigger defenses
    AC1 -->|Attempts System Modification| L1_Pre_Execution
    AC2 -->|Attempts Data Exfiltration| L1_Pre_Execution
    AC3 -->|Attempts DoS| L1_Pre_Execution
    AC4 -->|Attempts Antagonism| L1_Pre_Execution

    %% Defense Layer Flow
    L1_Pre_Execution -->|Passed| L2_Configuration_Gate
    L2_Configuration_Gate -->|Approved| L3_Execution_Sandbox
    L3_Execution_Sandbox -->|Monitored| L4_Network_Isolation
    L4_Network_Isolation -->|Contained| L5_Blast_Radius

    %% Gates mapped to defenses
    G7 --> L1_Pre_Execution
    G1 & G2 & G3 --> L2_Configuration_Gate
    G4 & G5 & G6 --> L3_Execution_Sandbox
    G8 & G9 --> L4_Network_Isolation
    G3 & G4 & G6 --> L5_Blast_Radius

    %% Java-style assessment
    L5_Blast_Radius --> JS1 & JS2
    L3_Execution_Sandbox --> JS3 & JS4

    %% Styling
    classDef attack_system fill:#ff9999,stroke:#ff0000,stroke-width:3px
    classDef attack_privacy fill:#ffb366,stroke:#ff6600,stroke-width:2px
    classDef attack_dos fill:#ffff99,stroke:#cccc00,stroke-width:2px
    classDef attack_antagonism fill:#ccff99,stroke:#339900,stroke-width:1px
    classDef defense fill:#99ccff,stroke:#0066cc,stroke-width:2px
    classDef gate fill:#90EE90,stroke:#006400,stroke-width:2px
    classDef assessment fill:#f0f0f0,stroke:#333333,stroke-width:2px
    
    class AC1,AC1_P1,AC1_P2,AC1_P3,AC1_P4,AC1_P5,AC1_P6,AC1_P7,AC1_P8,AC1_P9,AC1_P10,AC1_P11,AC1_P12,AC1_P13,AC1_P14,AC1_P15,AC1_P16,AC1_P17 attack_system
    class AC2,AC2_P1,AC2_P2,AC2_P3,AC2_P4,AC2_P5,AC2_P6,AC2_P7,AC2_P8 attack_privacy
    class AC3,AC3_P1,AC3_P2,AC3_P3,AC3_P4 attack_dos
    class AC4,AC4_P1,AC4_P2,AC4_P3,AC4_P4 attack_antagonism
    class L1_Pre_Execution,L2_Configuration_Gate,L3_Execution_Sandbox,L4_Network_Isolation,L5_Blast_Radius defense
    class G1,G2,G3,G4,G5,G6,G7,G8,G9 gate
    class JS1,JS2,JS3,JS4 assessment
```

[!mermaid_20260312_2c9de6.svg](mermaid_20260312_2c9de6.svg)    

