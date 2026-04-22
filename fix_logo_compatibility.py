"""
Fixing logo paths once and for all for BOTH local file access and FastAPI server access.
Using relative path 'logo.png' which works because index.html and logo.png are in the same folder (src/app).
And FastAPI has a /logo.png route to catch root requests.
"""
import os

files = ['src/app/index.html', 'src/app/dashboard.html']

for file_path in files:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace absolute root paths with simple relative paths
        content = content.replace('src="/logo.png"', 'src="logo.png"')
        content = content.replace('href="/logo.png"', 'href="logo.png"') # Favicon
        
        # Ensure any /static/ variants are also fixed to just logo.png
        content = content.replace('src="/static/logo.png"', 'src="logo.png"')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

print("Logo paths converted to relative 'logo.png' for maximum compatibility.")
