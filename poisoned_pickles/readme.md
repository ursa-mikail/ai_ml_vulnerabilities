# PyTorch Model Serialization Security Demonstration

This repository contains a comprehensive set of Python scripts demonstrating security vulnerabilities in PyTorch model serialization, particularly focusing on pickle-based attacks and their mitigations. The demonstrations range from basic pickle vulnerabilities to advanced persistent attacks and secure alternatives.

## ⚠️ WARNING

**These scripts are for educational and security research purposes only.** They demonstrate real vulnerabilities that can lead to arbitrary code execution. Never load PyTorch models from untrusted sources without proper safeguards, and never use these techniques against systems you don't own or have explicit permission to test.

## Prerequisites

```bash
pip install torch torchvision safetensors tabulate
```

```
File Descriptions
00.py - Comprehensive Security Demo
Purpose: Compares different serialization formats and their security implications.

This script demonstrates:

Basic pickle security issues with malicious payloads

PyTorch 2.6+ security features (weights_only=True)

Safetensors as a safe alternative

Code injection techniques into .pth files

Best practices for secure model loading

Format comparison with security ratings

Key Takeaways:

PyTorch 2.6+ defaults to weights_only=True for security

Safetensors provides format-level protection against code execution

State dict + safetensors is the recommended workflow

01.py - Payload Obfuscation Techniques
Purpose: Demonstrates how malicious payloads can be obfuscated to evade detection.

This script shows:

Original human-readable payload creation

Marshal obfuscation (compiling to bytecode)

XOR encoding with random keys

Final pickle payload generation

Size comparison across obfuscation layers

Execution demonstration of obfuscated code

Key Takeaways:

Payloads can be transformed multiple times to avoid detection

Obfuscation increases payload size but maintains functionality

Even heavily obfuscated code executes normally

02.py - Sticky Pickle: Self-Replicating Attack
Purpose: Demonstrates a persistent attack that survives model fine-tuning and redistribution.

This advanced attack shows:

Self-location (finds its own source file on disk)

Bytecode extraction (reads its own payload)

Attribute hiding (stores payload in unpickled object)

Function hooking (hooks pickle.dump() for reinfection)

Proper pickling using __reduce__

Payload persistence through fine-tuning and redistribution

Key Takeaways:

Models remain infected even after fine-tuning

Payload survives redistribution through HuggingFace, etc.

Traditional "load and resave" doesn't clean the infection

Extremely difficult to detect without specialized tools

03.py - Data Exfiltration Attack
Purpose: Demonstrates compromising a model to steal private user data.

This script shows:

Creating both ZIP and legacy pickle format models

Injecting exfiltration payloads

Simulating directory listing and file enumeration

Comparing safety checks between formats

Demonstrating payload execution during model loading

Key Takeaways:

Both modern (ZIP) and legacy formats are vulnerable

Payloads can exfiltrate sensitive data silently

Simple safety checks can be bypassed

04.py - Improved Payload Injection
Purpose: Enhanced version of data exfiltration with better payload execution.

Improvements include:

Proper namespace management for payload execution

Better error handling

More reliable payload injection into both formats

Detailed output showing payload execution

Mitigation recommendations

Key Takeaways:

Payloads execute reliably when models are loaded

The model may fail to load but payload still executes

weights_only=True is the only reliable protection

05.py - Functional Model with Payload
Purpose: Demonstrates payload execution while maintaining model functionality.

This script shows:

Payload execution that returns a working model

Proper handling of PyTorch's persistent IDs

Model remains fully functional after attack

eval() can be called on the compromised model

Key Takeaways:

The most dangerous attacks keep the model functional

Users have no indication anything is wrong

Backdoors can be hidden in seemingly normal models

06.py - Clean Vulnerability Demonstration
Purpose: Streamlined demonstration of the core vulnerability.

Features:

Clean, focused code showing the attack vector

Both ZIP and pickle format demonstrations

Clear safe vs. unsafe loading comparison

Educational output explaining each step

Security recommendations

Key Takeaways:

The vulnerability is real and affects all PyTorch versions

weights_only=True completely prevents code execution

The payload executes before any error occurs

07.py - Educational Security Demo
Purpose: Highly educational demonstration with detailed explanations.

This script provides:

Step-by-step walkthrough of the attack lifecycle

Clear separation of benign vs. malicious components

Explanation of the pickle vulnerability mechanism

Demonstration of safe loading with weights_only=True

Comprehensive summary and references

Key Takeaways:

Pickle's __reduce__ method is the attack vector

Any pickle file can potentially execute malicious code

Always verify model sources and use weights_only=True

08.py - Complete Secure vs. Insecure Demo
Purpose: Comprehensive demonstration with secure alternatives.

This extensive script includes:

Part 1: Creating benign models and displaying weights
Part 2: Creating malicious pickle files (educational)
Part 3: Secure Model Handler class with multiple protection layers
Part 4: Demonstrating secure saving/loading
Part 5: Comparing secure vs. malicious files
Part 6: Demonstrating the attack (educational)
Part 7: What would happen with unsafe loading
Part 8: Cleanup functionality

Secure features demonstrated:

SafeTensors format (most secure)

Weights-only pickle loading

Checksum verification

Model architecture separation

Metadata and integrity tracking

File inspection for suspicious patterns

Key Takeaways:

SafeTensors provides the best protection (no code execution possible)

Multiple protection layers are better than one

Always verify checksums and use trusted sources

Separate model architecture from weights when possible

Security Best Practices
Based on these demonstrations, follow these practices:

✅ DO:
Use weights_only=True with torch.load() (default in PyTorch 2.6+)

Prefer SafeTensors format for model weights

Save only state dicts, not full models

Verify checksums and digital signatures

Load models only from trusted sources

Use the safe_globals context manager when custom classes are needed

❌ DON'T:
Never set weights_only=False with untrusted files

Don't load full models from untrusted sources

Avoid pickle-based formats when possible

Don't ignore security warnings

🛡️ Additional Defenses:
Use cryptographic signing of models

Implement restricted unpicklers

Scan with tools like Fickling

Monitor for hooked functions

Consider ONNX for model interchange between frameworks
```