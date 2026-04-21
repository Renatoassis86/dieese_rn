"""
Wrapping dropdown content in index.html for stability fix (FIXED REGEX).
"""
import os
import re

HTML_PATH = 'src/app/index.html'
with open(HTML_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

def wrap_dropdown(match):
    inner = match.group(1)
    return f'<div class="dropdown-content"><div class="dropdown-inner">{inner}</div></div>'

# Regex to catch the dropdown content and wrap it
content = re.sub(r'<div class="dropdown-content">(.*?)</div>', wrap_dropdown, content, flags=re.DOTALL)

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Dropdown HTML wrapped with .dropdown-inner (successfully).")
