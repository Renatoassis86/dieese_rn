"""
CSS for the new BI Stats Module on the landing page.
"""
import os

CSS_PATH = 'src/app/style.css'
with open(CSS_PATH, 'a', encoding='utf-8') as f:
    f.write("""

/* ── BI STATS MODULE (Landing Page) ── */
.bi-stats-module { padding: 10rem 0; background: linear-gradient(135deg, #0d1b2a 0%, #07101a 100%); }
.bi-stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6rem; align-items: center; }
.bi-stats-info { animation: fadeInLeft 0.8s ease; }
.stats-description { font-size: 1.1rem; line-height: 1.8; color: rgba(255,255,255,0.8); margin: 2rem 0; }
.stats-features { display: flex; flex-direction: column; gap: 1rem; margin-bottom: 2rem; }
.feature-item { font-size: 0.9rem; font-weight: 700; color: var(--amber); background: rgba(244,162,97,0.1); padding: 0.8rem 1.2rem; border-radius: 12px; border: 1px solid rgba(244,162,97,0.2); width: fit-content; }

.bi-stats-preview { position: relative; animation: fadeInRight 0.8s ease; }
.preview-card-glass { background: var(--glass); padding: 1rem; border-radius: 30px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 50px 100px rgba(0,0,0,0.5); }
.geometric-mask-v3 { width: 100%; height: 450px; border-radius: 20px; overflow: hidden; }
.video-contain-full { width: 100%; height: 100%; object-fit: cover; filter: contrast(1.1) brightness(0.9); }

@keyframes fadeInLeft { from { opacity: 0; transform: translateX(-30px); } to { opacity: 1; transform: translateX(0); } }
@keyframes fadeInRight { from { opacity: 0; transform: translateX(30px); } to { opacity: 1; transform: translateX(0); } }

@media (max-width: 992px) {
    .bi-stats-grid { grid-template-columns: 1fr; gap: 4rem; text-align: center; }
    .bi-stats-info { order: 2; }
    .bi-stats-preview { order: 1; }
    .feature-item { margin: 0 auto; }
}
""")

print("CSS for BI Stats Module added.")
