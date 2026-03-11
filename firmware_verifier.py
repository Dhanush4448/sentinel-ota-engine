"""
Firmware Verification Module for Sentinel OTA Engine
Implements cryptographic signature verification and chunk integrity checks
to detect tampered firmware BEFORE installation.
"""

import hashlib
import hmac
import json
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from typing import Dict, List, Tuple, Optional


class FirmwareVerifier:
    """
    Verifies firmware integrity using cryptographic signatures and chunk checksums.
    Implements defense-in-depth: manifest signature + per-chunk verification.
    """
    
    def __init__(self, public_key_path: Optional[str] = None, trusted_ca_path: Optional[str] = None):
        """
        Initialize verifier with public key or CA certificate.
        
        Args:
            public_key_path: Path to RSA public key for signature verification
            trusted_ca_path: Path to trusted CA certificate for chain validation
        """
        self.public_key = None
        self.trusted_ca = None
        
        if public_key_path and os.path.exists(public_key_path):
            with open(public_key_path, 'rb') as f:
                self.public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
        
        if trusted_ca_path and os.path.exists(trusted_ca_path):
            with open(trusted_ca_path, 'rb') as f:
                self.trusted_ca = f.read()
    
    def verify_chunk_integrity(self, chunk_data: bytes, expected_hash: str, chunk_index: int) -> Tuple[bool, str]:
        """
        Verify a single chunk's integrity using SHA-256 hash.
        
        Args:
            chunk_data: Raw firmware chunk bytes
            expected_hash: Expected SHA-256 hash from manifest
            chunk_index: Chunk sequence number
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Calculate actual hash
            actual_hash = hashlib.sha256(chunk_data).hexdigest()
            
            # Constant-time comparison to prevent timing attacks
            if not hmac.compare_digest(actual_hash, expected_hash):
                return False, f"Chunk {chunk_index}: Hash mismatch. Expected {expected_hash[:16]}..., got {actual_hash[:16]}..."
            
            return True, "Chunk integrity verified"
            
        except Exception as e:
            return False, f"Chunk {chunk_index} verification error: {str(e)}"
    
    def verify_manifest_signature(self, manifest: Dict, signature: bytes) -> Tuple[bool, str]:
        """
        Verify the firmware manifest signature using RSA public key.
        
        Args:
            manifest: Firmware manifest dictionary
            signature: RSA signature bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.public_key:
            return False, "No public key configured for signature verification"
        
        try:
            # Serialize manifest deterministically
            manifest_json = json.dumps(manifest, sort_keys=True, separators=(',', ':'))
            manifest_bytes = manifest_json.encode('utf-8')
            
            # Verify RSA signature
            self.public_key.verify(
                signature,
                manifest_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True, "Manifest signature verified"
            
        except Exception as e:
            return False, f"Signature verification failed: {str(e)}"
    
    def verify_firmware_chunks(self, chunks: List[bytes], manifest: Dict) -> Tuple[bool, List[str]]:
        """
        Verify all firmware chunks before installation.
        
        Args:
            chunks: List of firmware chunk bytes
            manifest: Firmware manifest with chunk hashes
            
        Returns:
            Tuple of (all_valid, list_of_errors)
        """
        errors = []
        
        # Verify manifest structure
        if 'chunks' not in manifest:
            return False, ["Manifest missing 'chunks' field"]
        
        if 'total_chunks' not in manifest:
            return False, ["Manifest missing 'total_chunks' field"]
        
        expected_chunk_count = manifest['total_chunks']
        if len(chunks) != expected_chunk_count:
            errors.append(f"Chunk count mismatch: expected {expected_chunk_count}, got {len(chunks)}")
            return False, errors
        
        # Verify each chunk
        for i, chunk_data in enumerate(chunks):
            if str(i) not in manifest['chunks']:
                errors.append(f"Chunk {i}: Missing in manifest")
                continue
            
            expected_hash = manifest['chunks'][str(i)]['hash']
            is_valid, error_msg = self.verify_chunk_integrity(chunk_data, expected_hash, i)
            
            if not is_valid:
                errors.append(error_msg)
        
        return len(errors) == 0, errors
    
    def verify_complete_firmware(self, chunks: List[bytes], manifest: Dict, signature: bytes) -> Tuple[bool, List[str]]:
        """
        Complete firmware verification pipeline:
        1. Verify manifest signature
        2. Verify all chunk hashes
        3. Verify chunk sequence integrity
        
        Args:
            chunks: List of firmware chunk bytes
            manifest: Firmware manifest
            signature: RSA signature of manifest
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Step 1: Verify manifest signature
        sig_valid, sig_error = self.verify_manifest_signature(manifest, signature)
        if not sig_valid:
            errors.append(f"SIGNATURE VERIFICATION FAILED: {sig_error}")
            return False, errors  # Fail fast on signature failure
        
        # Step 2: Verify chunk integrity
        chunks_valid, chunk_errors = self.verify_firmware_chunks(chunks, manifest)
        if not chunks_valid:
            errors.extend(chunk_errors)
            return False, errors
        
        # Step 3: Verify chunk sequence (check for gaps or duplicates)
        chunk_indices = sorted([int(k) for k in manifest['chunks'].keys()])
        expected_sequence = list(range(len(chunks)))
        
        if chunk_indices != expected_sequence:
            errors.append(f"Chunk sequence error: expected {expected_sequence}, got {chunk_indices}")
            return False, errors
        
        return True, []


class FirmwareManifest:
    """
    Creates and manages firmware manifests with cryptographic signatures.
    """
    
    @staticmethod
    def create_manifest(chunks: List[bytes], firmware_version: str, device_model: str) -> Dict:
        """
        Create a firmware manifest with chunk hashes.
        
        Args:
            chunks: List of firmware chunk bytes
            firmware_version: Version string (e.g., "v2.4.1")
            device_model: Target device model
            
        Returns:
            Manifest dictionary
        """
        chunk_hashes = {}
        
        for i, chunk in enumerate(chunks):
            chunk_hash = hashlib.sha256(chunk).hexdigest()
            chunk_hashes[str(i)] = {
                'hash': chunk_hash,
                'size': len(chunk),
                'index': i
            }
        
        manifest = {
            'firmware_version': firmware_version,
            'device_model': device_model,
            'total_chunks': len(chunks),
            'total_size': sum(len(c) for c in chunks),
            'chunks': chunk_hashes,
            'algorithm': 'SHA-256'
        }
        
        return manifest
    
    @staticmethod
    def sign_manifest(manifest: Dict, private_key_path: str) -> bytes:
        """
        Sign a manifest with RSA private key.
        
        Args:
            manifest: Manifest dictionary
            private_key_path: Path to RSA private key
            
        Returns:
            Signature bytes
        """
        with open(private_key_path, 'rb') as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
        
        manifest_json = json.dumps(manifest, sort_keys=True, separators=(',', ':'))
        manifest_bytes = manifest_json.encode('utf-8')
        
        signature = private_key.sign(
            manifest_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return signature


def generate_key_pair(key_size: int = 2048) -> Tuple[bytes, bytes]:
    """
    Generate RSA key pair for firmware signing.
    
    Args:
        key_size: RSA key size in bits (2048 or 4096)
        
    Returns:
        Tuple of (private_key_pem, public_key_pem)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem, public_pem


# Example usage and testing
if __name__ == "__main__":
    print("Firmware Verification Module - Security Test")
    print("=" * 50)
    
    # Generate test keys
    print("\n1. Generating RSA key pair...")
    private_key, public_key = generate_key_pair()
    
    # Save keys temporarily
    with open('test_private_key.pem', 'wb') as f:
        f.write(private_key)
    with open('test_public_key.pem', 'wb') as f:
        f.write(public_key)
    
    # Create test firmware chunks (simulating 500-byte chunks)
    print("\n2. Creating test firmware chunks...")
    chunk_size = 500
    num_chunks = 20
    original_chunks = [os.urandom(chunk_size) for _ in range(num_chunks)]
    
    # Create manifest
    print("\n3. Creating firmware manifest...")
    manifest = FirmwareManifest.create_manifest(
        original_chunks,
        firmware_version="v2.4.1",
        device_model="SENTINEL-OTA-DEVICE"
    )
    
    # Sign manifest
    print("\n4. Signing manifest...")
    signature = FirmwareManifest.sign_manifest(manifest, 'test_private_key.pem')
    
    # Initialize verifier
    print("\n5. Initializing verifier...")
    verifier = FirmwareVerifier(public_key_path='test_public_key.pem')
    
    # Test 1: Verify legitimate firmware
    print("\n6. Testing legitimate firmware verification...")
    is_valid, errors = verifier.verify_complete_firmware(original_chunks, manifest, signature)
    if is_valid:
        print("✓ Legitimate firmware verified successfully!")
    else:
        print(f"✗ Verification failed: {errors}")
    
    # Test 2: Tampered chunk detection
    print("\n7. Testing tampered chunk detection...")
    tampered_chunks = original_chunks.copy()
    tampered_chunks[5] = b'MALICIOUS_CODE' + os.urandom(chunk_size - 14)  # Tamper chunk 5
    
    is_valid, errors = verifier.verify_complete_firmware(tampered_chunks, manifest, signature)
    if not is_valid:
        print("✓ Tampered chunk detected!")
        print(f"  Errors: {errors[:2]}...")  # Show first 2 errors
    else:
        print("✗ SECURITY FAILURE: Tampered chunk not detected!")
    
    # Test 3: Invalid signature detection
    print("\n8. Testing invalid signature detection...")
    fake_signature = os.urandom(256)  # Random bytes
    is_valid, errors = verifier.verify_complete_firmware(original_chunks, manifest, fake_signature)
    if not is_valid:
        print("✓ Invalid signature detected!")
        print(f"  Error: {errors[0]}")
    else:
        print("✗ SECURITY FAILURE: Invalid signature not detected!")
    
    # Cleanup
    print("\n9. Cleaning up test files...")
    for f in ['test_private_key.pem', 'test_public_key.pem']:
        if os.path.exists(f):
            os.remove(f)
    
    print("\n" + "=" * 50)
    print("Security verification tests complete!")
