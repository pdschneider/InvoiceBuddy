# Managers/security.py
from tkinter import simpledialog, messagebox
import json, os, logging, hashlib
from Utils.load_settings import load_users_path

# Password Check
def load_users():
    """Load authorized users from users.json, return default if file doesn't exist."""
    users_path = load_users_path()
    default_users = {"authorized_users": [
        "056aefda718e5b3379e7e5e5c1e03810", #  Allen
        "94a648b01b1d806a38cf0e60cd79d235", #  Phillip
        "7e9d21dc407e7a42a259a0ac02da784c"]} #  Cassie
    try:
        if os.path.exists(users_path):
            with open(users_path, 'r') as f:
                return json.load(f)
        return default_users
    except Exception as e:
        logging.error(f"Error loading users from {users_path}: {e}")
        messagebox.showwarning("Warning", f"Failed to load users: {e}. Using default users.")
        return default_users

def save_users(users):
    """Save authorized users to users.json."""
    users_path = load_users_path()
    try:
        settings_dir = os.path.dirname(users_path)
        if not os.path.exists(settings_dir):
            os.makedirs(settings_dir, exist_ok=True)
        with open(users_path, 'w') as f:
            json.dump(users, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        logging.error(f"Error saving users to {users_path}: {e}")
        messagebox.showerror("Error", f"Failed to save users: {e}")
        raise

def restrict_access(globals):
    """Allows access only to specific users or those with the password."""
    user = globals.hashed_user
    users_data = load_users()
    authorized_users = users_data.get("authorized_users", [])
    if user in authorized_users:
        return
    password = simpledialog.askstring("Password", "Enter Password:", show="*")
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    if hashed_password == "ba01a63d489254db430f37b184b6abd7":
        authorized_users.append(user)
        users_data["authorized_users"] = authorized_users
        save_users(users_data)
        messagebox.showinfo("Success", f"User added to authorized users.")
    else:
        messagebox.showerror("Access Denied", "You are not authorized to use this program.")
        exit()
