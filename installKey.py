import os
import secrets
import string

INSTALL_KEY_FILE = "install.key"

def generate_install_key(length=28):
    chars = string.ascii_uppercase + string.digits 
    return ''.join(secrets.choice(chars) for _ in range(length))

def main():
    if os.path.exists(INSTALL_KEY_FILE):
        with open(INSTALL_KEY_FILE, "r") as f:
            key = f.read().strip()
        print(f"Installation key already exists: {key}")
        return

    key = generate_install_key() 
    with open(INSTALL_KEY_FILE, "w") as f:
        f.write(key)
    print(f"Your Installation Key is: {key}\nSave this key securely and provide it to users for login.")

if __name__ == "__main__":
    main()