"""
Refactoring BI into a separate page and updating index.html with a teaser section.
"""
import os

# 1. CREATE dashboard.html
with open('src/app/index.html', 'r', encoding='utf-8') as f:
    full_index = f.read()

# Extract BI Section and Logic
# Assuming bi-section is inside #estatisticas
bi_start = full_index.index('<section id="estatisticas"')
bi_end = full_index.index('</section>', bi_start) + 10

# Extract Header/Head parts for dashboard
head_start = full_index.index('<head>')
head_end = full_index.index('</head>') + 7
head_content = full_index[head_start:head_end]

# Dashboard Template
dashboard_html = f"""<!DOCTYPE html>
<html lang="pt-br">
{head_content}
<body class="dashboard-page">
    <nav class="navbar standalone-nav">
        <div class="container nav-container">
            <a href="/" class="btn-back">⬅ Voltar ao Observatório</a>
            <img src="/static/logo.png" alt="DIEESE" class="nav-logo-small">
        </div>
    </nav>

    {full_index[bi_start:bi_end]}

    <footer class="footer-mini">
        <p>&copy; 2024-2026 Observatório do Trabalho e de Políticas Sociais — DIEESE.</p>
    </footer>

    <script src="/static/api.js"></script>
    <script>
        // Copy relevant parts of BI logic from index if needed, 
        // but it's likely already in the section via injected script.
    </script>
</body>
</html>"""

with open('src/app/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dashboard_html)

# 2. UPDATE index.html with Teaser
teaser_html = """
<section id="estatisticas" class="dark-section bi-teaser">
    <div class="container teaser-flex">
        <div class="teaser-content">
            <p class="kicker-light">— PAINEL DE INFORMAÇÕES —</p>
            <h2 class="teaser-title">Diagnóstico em Tempo Real</h2>
            <p class="teaser-text">
                Explore indicadores dinâmicos sobre a agricultura familiar e economia solidária no RN. 
                Nossa plataforma permite a geração de quadros personalizados atravé de filtros territoriais, 
                temporais e setoriais baseados no Supabase.
            </p>
            <a href="/dashboard.html" class="btn-primary-amber">🚀 Acessar Painel de Estatísticas</a>
        </div>
        <div class="teaser-visual">
            <div class="geometric-video-frame-v2">
                <video autoplay muted loop playsinline class="video-contain">
                    <source src="/static/assets/video2.mp4" type="video/mp4">
                </video>
            </div>
        </div>
    </div>
</section>
"""

content = full_index[:bi_start] + teaser_html + full_index[bi_end:]

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

# 3. CSS UPDATES
CSS_PATH = 'src/app/style.css'
with open(CSS_PATH, 'a', encoding='utf-8') as f:
    f.write("""
/* ── BI TEASER & DASHBOARD PAGE ───────── */
.bi-teaser { padding: 8rem 0; overflow: hidden; }
.teaser-flex { display: flex; align-items: center; justify-content: space-between; gap: 5rem; }
.teaser-content { flex: 1; text-align: left; }
.teaser-title { font-size: 3.5rem; font-weight: 900; color: #fff; margin-bottom: 2rem; }
.teaser-text { font-size: 1.2rem; color: rgba(255,255,255,0.7); line-height: 1.8; margin-bottom: 2.5rem; }

.teaser-visual { flex: 1; display: flex; justify-content: flex-end; }
.geometric-video-frame-v2 { 
    width: 100%; 
    max-width: 500px; 
    border-radius: 40px; 
    overflow: hidden; 
    background: #000;
    border: 8px solid rgba(255,255,255,0.1);
    box-shadow: 0 30px 60px rgba(0,0,0,0.5);
}
.video-contain { width: 100%; height: auto; display: block; }

.btn-primary-amber { 
    display: inline-block; 
    padding: 1.2rem 2.5rem; 
    background: var(--amber); 
    color: var(--navy); 
    font-weight: 900; 
    text-transform: uppercase; 
    border-radius: 15px; 
    text-decoration: none;
    transition: 0.3s;
    box-shadow: 0 10px 20px rgba(246, 173, 85, 0.3);
}
.btn-primary-amber:hover { transform: translateY(-5px); background: #fff; }

/* Dashboard Standalone Styles */
.dashboard-page .bi-section { margin-top: 2rem; }
.standalone-nav { background: var(--navy); padding: 1rem 0; }
.btn-back { color: #fff; text-decoration: none; font-weight: 700; font-size: 0.9rem; }
.footer-mini { padding: 2rem; text-align: center; color: #718096; font-size: 0.8rem; }
""")

print("Teaser created on index.html and BI moved to dashboard.html.")
