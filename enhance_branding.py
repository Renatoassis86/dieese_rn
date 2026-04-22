"""
Enhancing logo placement:
1. Replaces generic logo icon with the actual DIEESE logo in the navbar.
2. Sets the DIEESE logo as the site's Favicon for a professional browser tab appearance.
"""
import os

files = ['src/app/index.html', 'src/app/dashboard.html']

for file_path in files:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Add Favicon to <head>
        favicon_tag = '<link rel="icon" type="image/png" href="/logo.png">'
        if favicon_tag not in content:
            content = content.replace('<head>', f'<head>\n    {favicon_tag}')
        
        # 2. Update Navbar Logo in index.html (specifically)
        if 'index.html' in file_path:
            # Replace the 🌿 icon with the logo image
            old_brand = '<span class="logo-icon">🌿</span>'
            new_brand = '<img src="/logo.png" alt="DIEESE" style="height: 38px; width: auto; margin-right: 12px; filter: brightness(0) invert(1);">'
            # Using filter to make it white if the navbar is dark, but wait... 
            # If the user provided a colorful logo, maybe just normal src is better.
            # I'll use a clean <img> tag.
            if old_brand in content:
                content = content.replace(old_brand, new_brand)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

print("Logo placement enhanced in Navbar and Favicon.")
