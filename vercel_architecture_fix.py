"""
Final Architecture Overhaul for Vercel:
1. Moves all frontend assets to the REPOSITORY ROOT.
2. Simplifies all paths to flat relative paths (style.css, api.js, logo.png).
3. Removes redundant 'DIEESE' text from the header as requested.
4. Ensures logo visibility by eliminating subfolder nesting that Vercel might be ignoring.
"""
import os
import re

INDEX_PATH = 'index.html'

if os.path.exists(INDEX_PATH):
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Simplify paths (remove /static/ or folder prefixes)
    content = content.replace('/static/style.css', 'style.css')
    content = content.replace('static/style.css', 'style.css')
    content = content.replace('/static/api.js', 'api.js')
    content = content.replace('static/api.js', 'api.js')
    content = content.replace('/static/assets/', 'assets/')
    content = content.replace('static/assets/', 'assets/')
    
    # logo.png is now at the root too
    content = re.sub(r'src=["\'].*?logo\.png["\']', 'src="logo.png"', content)
    content = re.sub(r'href=["\'].*?logo\.png["\']', 'href="logo.png"', content)

    # 2. Remove redundant ' - DIEESE' from header text
    # Looking for: <span class="logo-sub">RIO GRANDE DO NORTE · DIEESE</span>
    # Or similar
    content = content.replace('RIO GRANDE DO NORTE · DIEESE', 'RIO GRANDE DO NORTE')
    content = content.replace('RIO GRANDE DO NORTE - DIEESE', 'RIO GRANDE DO NORTE')

    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

# Repeat for dashboard if it was moved (I didn't move it yet, let's move it)
if os.path.exists('src/app/dashboard.html'):
    import shutil
    shutil.copy('src/app/dashboard.html', './dashboard.html')
    
    with open('dashboard.html', 'r', encoding='utf-8') as f:
        dash_content = f.read()
    dash_content = dash_content.replace('/static/style.css', 'style.css')
    dash_content = dash_content.replace('/static/api.js', 'api.js')
    dash_content = re.sub(r'src=["\'].*?logo\.png["\']', 'src="logo.png"', dash_content)
    with open('dashboard.html', 'w', encoding='utf-8') as f:
        f.write(dash_content)

print("Vercel-ready architecture deployed at root level.")
