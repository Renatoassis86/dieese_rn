"""
Expanding footer to include all sections and social media icons.
"""
import os

HTML_PATH = 'src/app/index.html'

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. ADD FONT AWESOME CDN
if 'font-awesome' not in content:
    content = content.replace(
        '</head>',
        '    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">\n</head>'
    )

# 2. REDESIGN FOOTER
footer_start = content.index('<footer class="footer">')
footer_end = content.index('</footer>') + 9

new_footer = """<footer class="footer">
    <div class="container h-footer-container">
        <div class="h-footer-top">
            <div class="h-footer-brand">
                <img src="/static/logo.png" alt="DIEESE" class="footer-logo-img-h">
                <p>Departamento Intersindical de Estatística e Estudos Socioeconômicos</p>
                <div class="footer-social-icons">
                    <a href="https://www.instagram.com/dieese_online/" target="_blank" title="Instagram"><i class="fab fa-instagram"></i></a>
                    <a href="https://www.facebook.com/dieeseonline" target="_blank" title="Facebook"><i class="fab fa-facebook"></i></a>
                    <a href="mailto:en@dieese.org.br" title="E-mail"><i class="fas fa-envelope"></i></a>
                </div>
            </div>
            
            <div class="h-footer-grid">
                <div class="link-group">
                    <span class="group-title">Institucional</span>
                    <a href="#sobre">O Projeto</a>
                    <a href="#sobre">Objetivos</a>
                    <a href="#sobre">Metodologia</a>
                </div>
                
                <div class="link-group">
                    <span class="group-title">Dimensões I</span>
                    <a href="#ecosol">Economia Solidária</a>
                    <a href="#mercado">Mercado Institucional</a>
                    <a href="#agro">Estrutura Agropecuária</a>
                </div>

                <div class="link-group">
                    <span class="group-title">Dimensões II</span>
                    <a href="#producao">Produção e Dinâmica</a>
                    <a href="#trabalho">Trabalho e Renda</a>
                    <a href="#vulnerabilidades">Vulnerabilidades</a>
                </div>

                <div class="link-group">
                    <span class="group-title">Explorar</span>
                    <a href="#territorios">Territórios</a>
                    <a href="#indicadores">Indicadores</a>
                    <a href="#estatisticas">Estatísticas (BI)</a>
                </div>
            </div>
        </div>
        <div class="h-footer-bottom">
            <p>&copy; 2024-2026 Observatório do Trabalho e de Políticas Sociais — DIEESE. Sistema Integrado de Dados Socioeconômicos.</p>
        </div>
    </div>
</footer>"""

content = content[:footer_start] + new_footer + content[footer_end:]

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

# 3. CSS UPDATE FOR THE NEW GRID
CSS_PATH = 'src/app/style.css'
with open(CSS_PATH, 'a', encoding='utf-8') as f:
    f.write("""
/* ── FOOTER EXPANSION ────────────────── */
.h-footer-top { display: grid; grid-template-columns: 1fr 2.5fr; gap: 4rem; }
.h-footer-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 2rem; }
.footer-social-icons { display: flex; gap: 1.5rem; margin-top: 1.5rem; }
.footer-social-icons a { color: #fff; font-size: 1.4rem; opacity: 0.7; transition: 0.3s; }
.footer-social-icons a:hover { opacity: 1; color: var(--amber); transform: translateY(-3px); }
.link-group a { display: block; margin-bottom: 0.5rem; font-size: 0.85rem; }
""")

print("Footer expanded with all sections and social media icons.")
