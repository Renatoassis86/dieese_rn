"""
Updating BI teaser styles: Premium button and circular video mask.
"""
import os

CSS_PATH = 'src/app/style.css'
with open(CSS_PATH, 'a', encoding='utf-8') as f:
    f.write("""

/* ── PREMIUM BI BUTTON ── */
.btn-bi-premium {
    display: inline-flex;
    align-items: center;
    gap: 1rem;
    padding: 1.2rem 2.5rem;
    background: var(--amber);
    color: #000 !important;
    text-decoration: none;
    font-weight: 900;
    font-size: 1.1rem;
    border-radius: 50px;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    box-shadow: 0 10px 20px rgba(244, 162, 97, 0.3);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border: 2px solid transparent;
}

.btn-bi-premium:hover {
    background: #fff;
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 15px 30px rgba(255, 255, 255, 0.2);
    border-color: var(--amber);
}

.btn-bi-premium i {
    font-size: 1.2rem;
    transition: transform 0.3s ease;
}

.btn-bi-premium:hover i {
    transform: translateX(5px) rotate(-10deg);
}

/* ── CIRCULAR VIDEO MASK ── */
.geometric-mask-v3 {
    width: 450px;
    height: 450px;
    border-radius: 50%;
    overflow: hidden;
    border: 8px solid rgba(255,255,255,0.05);
    box-shadow: 0 0 50px rgba(0,0,0,0.3);
    margin: 0 auto;
}

@media (max-width: 768px) {
    .geometric-mask-v3 {
        width: 300px;
        height: 300px;
    }
}
""")

print("Premium button and circular mask CSS added.")
