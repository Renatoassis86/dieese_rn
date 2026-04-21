"""Final UI polish based on latest user requests: logo replacement and official project description."""
import os

HTML_PATH = 'src/app/index.html'

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. LOGO REPLACEMENT IN FOOTER
# Find the footer logo SVG and replace with official public/logo.png
import re
# The SVG block is in repair_platform.py script too, so we find it in the current content
old_logo_mark = """<div class="footer-logo-mark">
                    <svg viewBox="0 0 280 60" class="dieese-logo-svg" aria-label="DIEESE">
                        <text x="0" y="50" fill="#FFFFFF" font-family="'Montserrat', Arial, sans-serif" font-weight="900" font-size="54" letter-spacing="2">D</text>
                        <text x="42" y="50" fill="#FFFFFF" font-family="'Montserrat', Arial, sans-serif" font-weight="900" font-size="54" letter-spacing="2">I</text>
                        <circle cx="53" cy="8" r="7" fill="#E30613"/>
                        <text x="66" y="50" fill="#FFFFFF" font-family="'Montserrat', Arial, sans-serif" font-weight="900" font-size="54" letter-spacing="2">EESE</text>
                    </svg>
                </div>"""

new_logo_mark = """<div class="footer-logo-mark">
                    <img src="/static/logo.png" alt="DIEESE" class="footer-logo-img">
                </div>"""

content = content.replace(old_logo_mark, new_logo_mark)

# 2. PROJECT DESCRIPTION REPLACEMENT
# Target the section-light id="sobre" h2 and p.subtitle
old_title_p = """<h2>Diagnóstico Socioeconômico dos Empreendimentos de Economia Solidária</h2>
            <p class="subtitle text-darker">Um observatório técnico para subsidiar o percurso formativo e o planejamento de políticas rurais no Rio Grande do Norte.</p>"""

new_title_p = """<h2>Diagnóstico Socioeconômico dos Empreendimentos Rurais de Economia Solidária</h2>
            <p class="subtitle text-darker">Elaborar o diagnóstico socioeconômico dos empreendimentos rurais de economia solidária do Rio Grande do Norte (RN) com base em dados secundários, estruturando uma base integrada e produtos visuais para subsidiar planejamento e execução do percurso formativo previsto no plano.</p>"""

content = content.replace(old_title_p, new_title_p)

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

# 3. CSS UPDATE FOR FOOTER LOGO
CSS_PATH = 'src/app/style.css'
with open(CSS_PATH, 'a', encoding='utf-8') as f:
    f.write("\n.footer-logo-img { height: 60px; width: auto; filter: brightness(0) invert(1); margin-bottom: 1rem; }\n")

print("UI Polish: Logo replaced and Project Description updated.")
