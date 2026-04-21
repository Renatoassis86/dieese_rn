"""
Fixing logo once and for all by using absolute root paths and a dedicated route.
"""
import os

files = ['src/app/index.html', 'src/app/dashboard.html']

for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Standardize logo path to /logo.png
    content = content.replace('/static/logo.png', '/logo.png')
    content = content.replace('static/logo.png', '/logo.png')
    content = content.replace('/public/logo.png', '/logo.png')
    
    # Fix potential branding in header if exists
    content = content.replace('logo.png"', '/logo.png"')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("HTML files updated to use root /logo.png.")
