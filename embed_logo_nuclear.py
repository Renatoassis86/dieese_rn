"""
The 'Nuclear Option' for the logo:
1. Converts the PNG logo to a Base64 string.
2. Injects the Base64 directly into index.html and dashboard.html.
3. This ensures the logo is EMBEDDED in the code and cannot fail due to pathing or server issues.
"""
import base64
import os

LOGO_PATH = 'src/app/logo.png'
TARGET_FILES = ['src/app/index.html', 'src/app/dashboard.html']

if not os.path.exists(LOGO_PATH):
    # Fallback to public if src/app missing
    LOGO_PATH = 'public/logo.png'

with open(LOGO_PATH, 'rb') as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

b64_src = f"data:image/png;base64,{encoded_string}"

for file_path in TARGET_FILES:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace all variants of the logo path with the Base64 string
        # We target both header and footer
        import re
        # This replaces any src that points to logo.png
        content = re.sub(r'src=["\'].*?logo\.png["\']', f'src="{b64_src}"', content)
        
        # Also handle any missed ones
        content = content.replace('"/logo.png"', f'"{b64_src}"')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

print(f"Logo embedded as Base64 in {len(TARGET_FILES)} files. Path dependency eliminated.")
