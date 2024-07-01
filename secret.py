import os
import base64

# Generate a secure random key
secure_key = os.urandom(32)
# Convert it to a readable string
secret_key = base64.b64encode(secure_key).decode('utf-8')

print(f"Your new SECRET_KEY is: {secret_key}")
# Add this to your .env file or environment variables