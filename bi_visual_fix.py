"""
Fixing font visibility and adding video 2 in a geometric frame in the BI section.
"""
import os

HTML_PATH = 'src/app/index.html'

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. FIX FONT COLOR (Dark section descriptions) - Handled in CSS mainly, 
# but I'll ensure the inline text has a class or style
content = content.replace(
    'Utilize filtros para gerar quadros, tabelas e gráficos personalizados por território, período e dimensão do estudo. Dados integrados via Supabase para consultas em tempo real.',
    '<span class="light-desc">Utilize filtros para gerar quadros, tabelas e gráficos personalizados por território, período e dimensão do estudo. Dados integrados via Supabase para consultas em tempo real.</span>'
)

# 2. ADD VIDEO TO BI SECTION
video_html = """
        <div class="bi-video-container">
            <div class="geometric-video-frame">
                <video autoplay muted loop playsinline class="video-geometric">
                    <source src="/static/assets/video2.mp4" type="video/mp4">
                </video>
            </div>
        </div>
"""

# Insert video after bi-date
if '<div class="bi-video-container">' not in content:
    content = content.replace(
        '<p class="bi-date">ATUALIZADO EM ABRIL DE 2026</p>',
        '<p class="bi-date">ATUALIZADO EM ABRIL DE 2026</p>\n' + video_html
    )

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

# 3. CSS UPDATE
CSS_PATH = 'src/app/style.css'
with open(CSS_PATH, 'a', encoding='utf-8') as f:
    f.write("""
/* ── BI VIDEO & FONT FIX ──────────────── */
.light-desc { color: rgba(255,255,255,0.7) !important; display: inline-block; margin-top: 1rem; }

.bi-video-container { display: flex; justify-content: center; margin: 3rem 0; }
.geometric-video-frame { 
    width: 320px; 
    height: 380px; 
    border-radius: 40px; 
    overflow: hidden; 
    box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    border: 5px solid rgba(255,255,255,0.1);
}
.video-geometric { width: 100%; height: 100%; object-fit: cover; }

/* Font visibility in dark sections */
#estatisticas .bi-header p { color: rgba(255,255,255,0.8); }
""")

print("Font visibility fixed and Video 2 integrated into BI section.")
