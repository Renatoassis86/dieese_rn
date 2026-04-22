"""
Reverting Base64 embedding and using the file provided by the user in public/logo.png.
"""
import os
import re

TARGET_FILES = ['src/app/index.html', 'src/app/dashboard.html']

for file_path in TARGET_FILES:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the massive base64 string back to /logo.png
        # We look for src="data:image/png;base64,... "
        content = re.sub(r'src=["\']data:image/png;base64,.*?["\']', 'src="/logo.png"', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

print("Base64 embedding removed. Reverted to /logo.png file path.")
