"""Fix CSS for better contrast, centralized captions, and rounded image formats."""
CSS_PATH = 'src/app/style.css'

with open(CSS_PATH, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Fix contrast for .subtitle
    if "color: rgba(0,0,0,0.7);" in line:
        new_lines.append(line.replace("rgba(0,0,0,0.7)", "rgba(0,0,0,0.85)"))
    # Fix contrast for .text-muted
    elif ".text-muted  { color: rgba(255,255,255,0.65); }" in line:
        new_lines.append(".text-muted  { color: rgba(255,255,255,0.85); }\n")
    # Fix .hero-sub contrast
    elif "color: rgba(255,255,255,0.80);" in line:
        new_lines.append(line.replace("0.80", "0.95"))
    else:
        new_lines.append(line)

# Add missing/improved styles at the end
extra_styles = """
/* Improvements for contrast and diagramming */
.text-muted-bright { color: rgba(255,255,255,0.9) !important; }
.subtitle.text-darker { color: #2D3748; }

/* Centered Captions with rounded bottom */
.illust-caption {
    position: absolute; bottom: 0; left: 0; right: 0;
    background: linear-gradient(transparent, rgba(0,0,0,0.9));
    color: #fff; padding: 2.5rem 1rem 1rem;
    font-size: 0.9rem; font-weight: 700;
    text-align: center;
    border-bottom-left-radius: 80px; /* Matching var(--r-img) bottom */
    border-bottom-right-radius: 80px;
    letter-spacing: 0.02em;
}

.illust-wrap img {
    border-radius: var(--r-img);
    width: 100%; object-fit: cover;
    box-shadow: 0 20px 40px rgba(0,0,0,0.15);
}

.base-tag {
    display: inline-block;
    background: rgba(45,106,79,0.08);
    color: var(--green);
    padding: 0.4rem 0.8rem;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 700;
    margin-right: 0.5rem;
    margin-bottom: 0.5rem;
    border: 1px solid rgba(45,106,79,0.15);
}

.badge-dev {
    display: inline-block;
    padding: 0.3rem 0.7rem;
    background: #EDF2F7;
    color: #4A5568;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    margin-top: 1rem;
}

.footer-social-inline { display: flex; gap: 1rem; margin-top: 0.5rem; }
.footer-social-inline a { color: #fff; font-weight: 800; font-size: 0.8rem; }
.contact-item { font-size: 0.85rem; color: #fff; margin-bottom: 0.4rem; }
"""

with open(CSS_PATH, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
    f.write(extra_styles)

print("CSS contrast and layout improved.")
