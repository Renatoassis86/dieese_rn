"""
Refactoring BI into a separate page and updating index.html with a teaser section.
Fixes the substring error by using the correct section class.
"""
import os

HTML_PATH = 'src/app/index.html'
with open(HTML_PATH, 'r', encoding='utf-8') as f:
    full_index = f.read()

# 1. EXTRACT BI SECTION
# Using class and ID to be precise
bi_tag = '<section class="bi-section" id="estatisticas">'
bi_start = full_index.index(bi_tag)
bi_end = full_index.index('</section>', bi_start) + 10

bi_section_html = full_index[bi_start:bi_end]

# Extract Header/Head parts for dashboard
head_start = full_index.index('<head>')
head_end = full_index.index('</head>') + 7
head_content = full_index[head_start:head_end]

# Dashboard Template
dashboard_html = f"""<!DOCTYPE html>
<html lang="pt-br">
{head_content}
<style>
    .dashboard-page {{ background: #0b141e; }}
    .standalone-nav {{ background: #0d1b2a; padding: 1.5rem 0; border-bottom: 1px solid rgba(255,255,255,0.1); }}
    .btn-back {{ color: #F4A261; text-decoration: none; font-weight: 900; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; }}
    .nav-logo-small {{ height: 35px; }}
    .footer-mini {{ padding: 4rem 2rem; text-align: center; color: #718096; font-size: 0.8rem; border-top: 1px solid rgba(255,255,255,0.05); }}
</style>
<body class="dashboard-page">
    <nav class="navbar standalone-nav">
        <div class="container" style="display:flex; justify-content: space-between; align-items: center;">
            <a href="/" class="btn-back">⬅ Voltar ao Observatório</a>
            <img src="/static/logo.png" alt="DIEESE" class="nav-logo-small">
        </div>
    </nav>

    {bi_section_html}

    <footer class="footer-mini">
        <p>&copy; 2024-2026 Observatório do Trabalho e de Políticas Sociais — DIEESE. Todos os recursos integrados via Supabase.</p>
    </footer>

    <script src="/static/api.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</body>
</html>"""

with open('src/app/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dashboard_html)

# 2. UPDATE index.html with Teaser (Side-by-Side Video)
# Using a clean layout as requested by the user
teaser_html = """
<section id="estatisticas" class="dark-section bi-teaser">
    <div class="container teaser-flex">
        <div class="teaser-content">
            <p class="kicker-light">— PAINEL DE INFORMAÇÕES —</p>
            <h2 class="teaser-title">Diagnóstico em Tempo Real</h2>
            <p class="teaser-text">
                Explore indicadores dinâmicos sobre a agricultura familiar e economia solidária no RN. 
                Nossa plataforma permite a geração de quadros personalizados através de filtros territoriais, 
                temporais e setoriais baseados diretamente nos dados do Supabase.
            </p>
            <a href="/static/dashboard.html" class="btn-primary-amber">🚀 Acessar Painel Completo</a>
        </div>
        <div class="teaser-visual">
            <div class="geometric-video-frame-v2">
                <video autoplay muted loop playsinline class="video-contain-full">
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

print("Success: Dashboard.html created and Index.html updated with Side-by-Side Video Teaser.")
