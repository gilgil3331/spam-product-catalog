#!/usr/bin/env python3
"""
Local utility — generate a bcrypt hash for the guest user.
Run: python3 create_user.py
Copy the INSERT statement and run it in Supabase SQL Editor.
This script never connects to the database.
"""
import getpass
import bcrypt

password = getpass.getpass("Enter password for 'guest': ").encode("utf-8")
hashed = bcrypt.hashpw(password, bcrypt.gensalt(12)).decode()

print("\nRun this in Supabase SQL Editor:")
print(f"INSERT INTO users (username, password_hash) VALUES ('guest', '{hashed}');")
