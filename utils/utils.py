import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import time
from functools import wraps
    
def derive_key(password: str, salt: bytes) -> bytes:
    """Derives a cryptographic key from the given password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return key

def encrypt_message(message: str, password: str) -> str:
    """Encrypts a message using the provided password."""
    salt = os.urandom(16)  # Generate a random salt
    key = derive_key(password, salt)
    
    iv = os.urandom(16)  # Generate a random initialization vector (IV)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_message = padder.update(message.encode()) + padder.finalize()

    encrypted_message = encryptor.update(padded_message) + encryptor.finalize()

    encrypted_data = salt + iv + encrypted_message
    return base64.b64encode(encrypted_data).decode('utf-8')

def decrypt_message(encrypted_message: str, password: str) -> str:
    """Decrypts a message using the provided password."""
    encrypted_data = base64.b64decode(encrypted_message)
    salt = encrypted_data[:16]
    iv = encrypted_data[16:32]
    encrypted_message = encrypted_data[32:]

    key = derive_key(password, salt)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    padded_message = decryptor.update(encrypted_message) + decryptor.finalize()

    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    message = unpadder.update(padded_message) + unpadder.finalize()

    return message.decode('utf-8')

def debounce(wait):
    """Debounce decorator to delay function invocation."""
    def decorator(func):
        last_invocation = None
        @wraps(func)
        def debounced(*args, **kwargs):
            nonlocal last_invocation
            current_time = time.time()
            if last_invocation is None or current_time - last_invocation >= wait:
                result = func(*args, **kwargs)
                last_invocation = current_time
                return result
        return debounced
    return decorator