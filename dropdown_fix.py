"""
Fixing dropdown persistence and creating exports directory.
"""
import os

# Create exports directory
os.makedirs('exports', exist_ok=True)

HTML_PATH = 'src/app/index.html'
with open(HTML_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix JS for dropdown persistence
dropdown_fix = """
// ── DROPDOWN PERSISTENCE ────────────────
document.querySelectorAll('.dropdown').forEach(dd => {
    const btn = dd.querySelector('.dropbtn');
    btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        // Close others
        document.querySelectorAll('.dropdown').forEach(other => {
            if (other !== dd) other.classList.remove('open');
        });
        
        dd.classList.toggle('open');
    });
});

window.addEventListener('click', () => {
    document.querySelectorAll('.dropdown').forEach(dd => dd.classList.remove('open'));
});
"""

# Inject before IntersectionObserver
if '// ── DROPDOWN PERSISTENCE' not in content:
    content = content.replace('// ── IntersectionObserver', dropdown_fix + '\n// ── IntersectionObserver')

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

# Update CSS for .open class
CSS_PATH = 'src/app/style.css'
with open(CSS_PATH, 'a', encoding='utf-8') as f:
    f.write("""
/* Dropdown fix */
.dropdown.open .dropdown-content {
    display: block !important;
    opacity: 1 !important;
    visibility: visible !important;
    transform: translateY(0) !important;
}
""")

print("Dropdown fix applied and 'exports' folder created.")
