import os

with open(os.path.join(os.path.dirname(__file__), '../../keys/private.pem'), "rb") as f:
    PRIVATE_KEY = f.read()
with open(os.path.join(os.path.dirname(__file__), '../../keys/public.pem'), "rb") as f:
    PUBLIC_KEY = f.read()