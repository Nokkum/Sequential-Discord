import tkinter as tk
from tkinter import messagebox
import subprocess
import os
from cryptography.fernet import Fernet

TOKEN_FILE = ".token"
KEY_FILE = ".token.key"
BOT_FILE = "bot.py"


def generate_key():
    """Generate and save a new AES key if it doesn't exist."""
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    with open(KEY_FILE, "rb") as f:
        return f.read()


def get_cipher():
    """Return a Fernet cipher object."""
    key = generate_key()
    return Fernet(key)


def save_token(token: str):
    """Encrypt and save token."""
    cipher = get_cipher()
    encrypted = cipher.encrypt(token.strip().encode("utf-8"))
    with open(TOKEN_FILE, "wb") as f:
        f.write(encrypted)


def load_token():
    """Load and decrypt token if available."""
    if not os.path.exists(TOKEN_FILE):
        return ""
    try:
        cipher = get_cipher()
        with open(TOKEN_FILE, "rb") as f:
            encrypted = f.read()
        return cipher.decrypt(encrypted).decode("utf-8")
    except Exception:
        return ""


def launch_bot(token: str):
    """Launch bot.py as subprocess with env var."""
    if not os.path.exists(BOT_FILE):
        messagebox.showerror("Error", f"Cannot find {BOT_FILE}")
        return

    save_token(token)
    try:
        env = os.environ.copy()
        env["DISCORD_TOKEN"] = token
        subprocess.Popen(["python", BOT_FILE], env=env)
        messagebox.showinfo("Bot Launched", "Discord bot started successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch bot: {e}")


def main():
    root = tk.Tk()
    root.title("Discord Bot Token Sidebar")
    root.geometry("320x220")
    root.resizable(False, False)

    tk.Label(root, text="Discord Token:", font=("Segoe UI", 10, "bold")).pack(pady=(10, 2))

    token_var = tk.StringVar(value=load_token())
    token_entry = tk.Entry(root, textvariable=token_var, show="*", width=40)
    token_entry.pack(pady=5)

    show_token = tk.BooleanVar(value=False)

    def toggle_token_visibility():
        if show_token.get():
            token_entry.config(show="*")
            toggle_btn.config(text="Show Token")
            show_token.set(False)
        else:
            token_entry.config(show="")
            toggle_btn.config(text="Hide Token")
            show_token.set(True)

    def on_save():
        token = token_var.get().strip()
        if not token:
            messagebox.showwarning("Missing Token", "Please enter your Discord bot token.")
            return
        save_token(token)
        messagebox.showinfo("Saved", "Token encrypted and saved successfully.")

    def on_launch():
        token = token_var.get().strip()
        if not token:
            messagebox.showwarning("Missing Token", "Please enter your Discord bot token.")
            return
        launch_bot(token)

    toggle_btn = tk.Button(root, text="Show Token", command=toggle_token_visibility, width=20)
    toggle_btn.pack(pady=3)
    tk.Button(root, text="Save Token", command=on_save, width=20).pack(pady=3)
    tk.Button(root, text="Launch Bot", command=on_launch, width=20).pack(pady=3)

    root.mainloop()


if __name__ == "__main__":
    main()
