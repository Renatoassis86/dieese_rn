"""
Wrapping dropdown content in index.html for stability fix.
"""
import os

HTML_PATH = 'src/app/index.html'
with open(HTML_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Wrap all dropdown-content inner children
content = content.replace('<div class="dropdown-content">', '<div class="dropdown-content"><div class="dropdown-inner">')
content = content.replace('<!-- End Dropdown -->\n                    </div>\n                </li>', '</div></div>\n                </li>')
# Actually, a simpler replace:
content = content.replace('</ul>\n            </div>', '</div></div>') # This is too risky.

# Better: use the structure
import re
def wrap_dropdown(match):
    inner = match.group(2)
    return f'<div class="dropdown-content"><div class="dropdown-inner">{inner}</div></div>'

content = re.sub(r'<div class="dropdown-content">(.*?)</div>', wrap_dropdown, content, flags=re.DOTALL)

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Dropdown HTML wrapped with .dropdown-inner.")
