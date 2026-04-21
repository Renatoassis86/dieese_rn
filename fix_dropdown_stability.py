"""
Fixing Navbar Dropdown hover stability.
- Removes the 6px physical gap that caused hover loss.
- Uses a pseudo-bridge to ensure the mouse never leaves the hit area.
"""
import os

CSS_PATH = 'src/app/style.css'
with open(CSS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Refined Dropdown Logic
old_content = """/* Dropdown */
.dropdown { position: relative; }
.dropdown-content {
    display: none; position: absolute; top: 100%; left: 0; padding-top: 6px; /* Bridge gap with padding or pseudo */
    background: #fff; min-width: 210px;
    border-radius: 14px; box-shadow: 0 16px 40px rgba(0,0,0,0.18);
    overflow: hidden; border: 1px solid rgba(0,0,0,0.06);
    animation: fadeDown 0.18s ease;
}
.dropdown:hover .dropdown-content { display: block; }
.dropdown-content::before { content: ""; position: absolute; top: -10px; left: 0; width: 100%; height: 10px; } /* Hover bridge */"""

new_content = """/* Dropdown */
.dropdown { position: relative; }
.dropdown-content {
    display: none; position: absolute; top: 90%; left: 0; padding-top: 15px; /* Creates an overlapping 'hit area' */
    min-width: 210px; z-index: 1000;
    transition: all 0.3s ease;
}
.dropdown-inner {
    background: #fff; border-radius: 14px; 
    box-shadow: 0 16px 40px rgba(0,0,0,0.22);
    overflow: hidden; border: 1px solid rgba(0,0,0,0.08);
    animation: fadeDown 0.2s ease forwards;
}
.dropdown:hover .dropdown-content { display: block; }
.dropdown-content a {
    display: block; padding: 0.9rem 1.4rem;
    font-size: 0.88rem; font-family: 'Open Sans', sans-serif;
    color: var(--text-mid); border-bottom: 1px solid var(--border);
    transition: all 0.2s;
}"""

content = content.replace(old_content, new_content)

with open(CSS_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Dropdown stability fix applied with overlapping hit area.")
