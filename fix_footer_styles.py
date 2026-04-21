"""
Fixing Footer styles and Logo visibility.
- Fixes blue link color in footer.
- Ensures logo.png path is correct and accessible.
- Updates main.py to mount the public folder correctly.
"""
import os

# 1. Update main.py to mount public folder as /public
MAIN_PATH = 'main.py'
with open(MAIN_PATH, 'r', encoding='utf-8') as f:
    main_py = f.read()

if 'app.mount("/public"' not in main_py:
    mount_code = """
public_dir = os.path.join(os.path.dirname(__file__), "public")
if os.path.exists(public_dir):
    app.mount("/public", StaticFiles(directory=public_dir), name="public")
"""
    main_py = main_py.replace('app = FastAPI(title="Observatório Rural RN")', 'app = FastAPI(title="Observatório Rural RN")' + mount_code)

with open(MAIN_PATH, 'w', encoding='utf-8') as f:
    f.write(main_py)

# 2. Update index.html for correct logo path and classes
INDEX_PATH = 'src/app/index.html'
with open(INDEX_PATH, 'r', encoding='utf-8') as f:
    index_html = f.read()

index_html = index_html.replace('src="/static/logo.png"', 'src="/public/logo.png"')

with open(INDEX_PATH, 'w', encoding='utf-8') as f:
    f.write(index_html)

# 3. Update style.css to fix blue links and white font in footer
CSS_PATH = 'src/app/style.css'
with open(CSS_PATH, 'r', encoding='utf-8') as f:
    css_content = f.read()

# Fix footer link selectors and colors
css_content = css_content.replace('.h-footer-links a { color: #fff;', '.link-group a { color: #ffffff !important; opacity: 0.7; border-bottom: none; ')
css_content = css_content.replace('.h-footer-links a:hover', '.link-group a:hover')

# Ensure entire footer text is clear
if '.footer p {' not in css_content:
    css_content += "\n.footer p, .footer span { color: #ffffff !important; opacity: 0.8; }\n"

with open(CSS_PATH, 'w', encoding='utf-8') as f:
    f.write(css_content)

print("Footer styles fixed, Logo path updated, and main.py mounting corrected.")
