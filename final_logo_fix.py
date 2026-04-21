"""
Final Fix for DIEESE Logo.
Using /static/logo.png which is the standard mount point for src/app.
"""
import os

files = ['src/app/index.html', 'src/app/dashboard.html']

for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace('/public/logo.png', '/static/logo.png')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Logo paths updated to /static/logo.png in both index and dashboard.")
