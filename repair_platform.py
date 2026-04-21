"""Full platform structural fix based on software engineering principles and study objectives."""
import os

HTML_PATH = 'src/app/index.html'

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. NAVBAR FIX - COMPLETELY REPLACE THE NAV BLOCK
# Identify header start to hero start to be safe
header_start = content.index('<header')
hero_start = content.index('<!-- ══════════ HERO')

new_header = """<header class="navbar">
    <div class="navbar-inner">
        <a href="#inicio" class="logo">
            <span class="logo-icon">🌿</span>
            <div class="logo-text">
                <span class="logo-title">Observatório do Trabalho e de Políticas Sociais</span>
                <span class="logo-sub">RIO GRANDE DO NORTE · DIEESE</span>
            </div>
        </a>
        <nav>
            <ul class="nav-links">
                <li class="dropdown">
                    <a href="#" class="dropbtn">Institucional &#9662;</a>
                    <div class="dropdown-content">
                        <a href="#sobre">O Projeto</a>
                        <a href="#sobre">Objetivos</a>
                        <a href="#sobre">Metodologia</a>
                    </div>
                </li>
                <li class="dropdown">
                    <a href="#" class="dropbtn">Dimensões &#9662;</a>
                    <div class="dropdown-content">
                        <a href="#ecosol">Economia Solidária</a>
                        <a href="#mercado">Mercado Institucional</a>
                        <a href="#agro">Estrutura Agropecuária</a>
                        <a href="#producao">Produção e Dinâmica</a>
                        <a href="#trabalho">Trabalho e Renda</a>
                        <a href="#vulnerabilidades">Vulnerabilidades</a>
                    </div>
                </li>
                <li><a href="#territorios">Territórios</a></li>
                <li><a href="#indicadores">Indicadores</a></li>
                <li><a href="#estatisticas" class="nav-stat">📊 Estatísticas</a></li>
            </ul>
        </nav>
    </div>
</header>
"""

content = content[:header_start] + new_header + content[hero_start:]

# 2. ABOUT SECTION FIX
sobre_start = content.index('<section class="section-light" id="sobre">')
dimensoes_start = content.index('<!-- ══════════ DIMENSÕES ══════════ -->')

new_sobre = """<section class="section-light" id="sobre">
    <div class="container">
        <div class="text-center mb-5">
            <p class="kicker">— O PROJETO —</p>
            <h2>Diagnóstico Socioeconômico dos Empreendimentos de Economia Solidária</h2>
            <p class="subtitle text-darker">Um observatório técnico para subsidiar o percurso formativo e o planejamento de políticas rurais no Rio Grande do Norte.</p>
        </div>
        <div class="pillars-grid">
            <div class="pillar-card">
                <span class="pillar-icon">🗂️</span>
                <h4>OE1 — Base Integrada</h4>
                <p>Integração de bases secundárias (PAA, Censo Agro, CADSOL) em base temática única.</p>
            </div>
            <div class="pillar-card">
                <span class="pillar-icon">🗺️</span>
                <h4>OE2 — Recortes Territoriais</h4>
                <p>Análise espacial por município e territórios de identidade oficial do RN.</p>
            </div>
            <div class="pillar-card">
                <span class="pillar-icon">📊</span>
                <h4>OE3 — Indicadores</h4>
                <p>Construção de tipologias para priorização e orientação de decisões estaduais.</p>
            </div>
            <div class="pillar-card">
                <span class="pillar-icon">📄</span>
                <h4>OE4 — Produtos Visuais</h4>
                <p>Infográficos, mapas e fichas territoriais com interpretação técnica padronizada.</p>
            </div>
        </div>
    </div>
</section>
"""

content = content[:sobre_start] + new_sobre + content[dimensoes_start:]

# 3. SIX DIMENSIONS FIX
dimensoes_tag = content.index('<!-- ══════════ DIMENSÕES ══════════ -->')
territorios_tag = content.index('<!-- ══════════ TERRITÓRIOS ══════════ -->')

new_dims_content = """<!-- ══════════ DIMENSÕES ══════════ -->
<section class="section-dark" id="dimensoes">
    <div class="container text-center">
        <p class="kicker kicker-light">— MATRIZ DE BASES —</p>
        <h2 class="text-white">Seis Eixos de Análise do Estudo</h2>
        <p class="subtitle text-muted-bright">Cada dimensão mobiliza bases de dados específicas para construir o retrato dos empreendimentos rurais.</p>
    </div>
</section>

<!-- ══════════ DIM 1: ECONOMIA SOLIDÁRIA ══════════ -->
<section class="dim-section" id="ecosol">
    <div class="container dim-grid">
        <div class="dim-illust">
            <div class="illust-wrap">
                <img src="/static/assets/dim_coop.png" alt="Economia Solidária">
                <div class="illust-caption">Economia Solidária · Panorama do RN</div>
            </div>
        </div>
        <div class="dim-content">
            <p class="kicker">— DIMENSÃO 1 —</p>
            <h2>Economia Solidária</h2>
            <p>Mapeamento de EES: formas organizativas, atividade econômica e localização territorial no estado.</p>
            <div class="dim-bases">
                <div class="base-tag">📡 Novo CADSOL / Cadastros EES</div>
            </div>
            <span class="badge-dev">🚧 Em desenvolvimento</span>
        </div>
    </div>
</section>

<!-- ══════════ DIM 2: MERCADO INSTITUCIONAL ══════════ -->
<section class="dim-section dim-alt" id="mercado">
    <div class="container dim-grid reversed">
        <div class="dim-content">
            <p class="kicker">— DIMENSÃO 2 —</p>
            <h2>Mercado Institucional</h2>
            <p>Inserção em compras públicas via PAA e PNAE: execução financeira e logística de fornecimento.</p>
            <div class="dim-bases">
                <div class="base-tag">📡 MiSocial (MDS) · PNAE (FNDE)</div>
            </div>
            <a href="#indicadores" class="btn-primary-sm">Ver Indicadores ✓</a>
        </div>
        <div class="dim-illust">
            <div class="illust-wrap">
                <img src="/static/assets/dim_paa.png" alt="Mercado Institucional">
                <div class="illust-caption">PAA · Compras Governamentais</div>
            </div>
        </div>
    </div>
</section>

<!-- ══════════ DIM 3: ESTRUTURA AGRO ══════════ -->
<section class="dim-section" id="agro">
    <div class="container dim-grid">
        <div class="dim-illust">
            <div class="illust-wrap">
                <img src="/static/assets/dim_agro.png" alt="Estrutura Agro">
                <div class="illust-caption">Estrutura Agropecuária · IBGE 2017</div>
            </div>
        </div>
        <div class="dim-content">
            <p class="kicker">— DIMENSÃO 3 —</p>
            <h2>Estrutura Agropecuária</h2>
            <p>Perfil rural, agricultura familiar e vocações produtivas por território.</p>
            <div class="dim-bases">
                <div class="base-tag">📡 Censo Agropecuário (IBGE)</div>
            </div>
            <span class="badge-dev">🚧 Em desenvolvimento</span>
        </div>
    </div>
</section>

<!-- ══════════ DIM 4: PRODUÇÃO E DINÂMICA ══════════ -->
<section class="dim-section dim-alt" id="producao">
    <div class="container dim-grid reversed">
        <div class="dim-content">
            <p class="kicker">— DIMENSÃO 4 —</p>
            <h2>Produção e Dinâmica</h2>
            <p>Análise da produção por cultura/rebanho e dinâmica territorial das cadeias produtivas.</p>
            <div class="dim-bases">
                <div class="base-tag">📡 PAM / PPM (IBGE)</div>
            </div>
            <span class="badge-dev">🚧 Em desenvolvimento</span>
        </div>
        <div class="dim-illust">
            <div class="illust-wrap">
                <img src="/static/assets/dim_cadeias.png" alt="Produção">
                <div class="illust-caption">Dinâmica Territorial e Cadeias</div>
            </div>
        </div>
    </div>
</section>

<!-- ══════════ DIM 5: TRABALHO E RENDA ══════════ -->
<section class="dim-section" id="trabalho">
    <div class="container dim-grid">
        <div class="dim-illust">
            <div class="illust-wrap">
                <img src="/static/assets/dim_trabalho.png" alt="Trabalho">
                <div class="illust-caption">Ocupação e Renda Rural</div>
            </div>
        </div>
        <div class="dim-content">
            <p class="kicker">— DIMENSÃO 5 —</p>
            <h2>Trabalho e Renda</h2>
            <p>Contexto de ocupação rura, remuneração e recortes de gênero no território.</p>
            <div class="dim-bases">
                <div class="base-tag">📡 PNADC / RAIS / CAGED</div>
            </div>
            <span class="badge-dev">🚧 Em desenvolvimento</span>
        </div>
    </div>
</section>

<!-- ══════════ DIM 6: VULNERABILIDADES ══════════ -->
<section class="dim-section dim-alt" id="vulnerabilidades">
    <div class="container dim-grid reversed">
        <div class="dim-content">
            <p class="kicker">— DIMENSÃO 6 —</p>
            <h2>Vulnerabilidades Sociais</h2>
            <p>Indicadores sociais que afetam a organização e produção rural.</p>
            <div class="dim-bases">
                <div class="base-tag">📡 CadÚnico / Índices Sociais</div>
            </div>
            <span class="badge-dev">🚧 Em desenvolvimento</span>
        </div>
        <div class="dim-illust">
            <div class="illust-wrap">
                <img src="/static/assets/dim_vulnerabilidades.png" alt="Vulnerabilidades">
                <div class="illust-caption">Condicionantes Sociais e Vulnerabilidade</div>
            </div>
        </div>
    </div>
</section>
"""

content = content[:dimensoes_tag] + new_dims_content + content[territorios_tag:]

# 4. FOOTER FIX
footer_start = content.index('<footer')
footer_end = content.index('</footer>') + 9

new_footer = """<footer class="footer">
    <div class="container">
        <div class="footer-grid">
            <div class="footer-brand">
                <div class="footer-logo-mark">
                    <svg viewBox="0 0 280 60" class="dieese-logo-svg" aria-label="DIEESE">
                        <text x="0" y="50" fill="#FFFFFF" font-family="'Montserrat', Arial, sans-serif" font-weight="900" font-size="54" letter-spacing="2">D</text>
                        <text x="42" y="50" fill="#FFFFFF" font-family="'Montserrat', Arial, sans-serif" font-weight="900" font-size="54" letter-spacing="2">I</text>
                        <circle cx="53" cy="8" r="7" fill="#E30613"/>
                        <text x="66" y="50" fill="#FFFFFF" font-family="'Montserrat', Arial, sans-serif" font-weight="900" font-size="54" letter-spacing="2">EESE</text>
                    </svg>
                </div>
                <p class="footer-desc">Departamento Intersindical de Estatística e Estudos Socioeconômicos</p>
                <p class="footer-address">Rua Aurora, 957 — 1º andar · Santa Ifigênia<br>CEP 01209-001 · São Paulo — SP</p>
            </div>
            <div class="footer-nav-col">
                <h5>Institucional</h5>
                <a href="#sobre">O Projeto</a>
                <a href="#sobre">Objetivos</a>
                <a href="#sobre">Metodologia</a>
            </div>
            <div class="footer-nav-col">
                <h5>Dimensões</h5>
                <a href="#ecosol">Eco. Solidária</a>
                <a href="#mercado">M. Institucional</a>
                <a href="#agro">Estrutura Agro</a>
                <a href="#producao">Produção</a>
                <a href="#trabalho">Trabalho/Renda</a>
                <a href="#vulnerabilidades">Vulnerabilidade</a>
            </div>
            <div class="footer-nav-col">
                <h5>Contatos</h5>
                <p class="contact-item">📞 (11) 3874-5366</p>
                <p class="contact-item">📧 en@dieese.org.br</p>
                <div class="footer-social-inline">
                    <a href="https://www.instagram.com/daboradieese/" target="_blank">IG</a>
                    <a href="https://www.facebook.com/Daboradieese" target="_blank">FB</a>
                </div>
            </div>
        </div>
    </div>
</footer>"""

content = content[:footer_start] + new_footer + content[footer_end:]

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(content)
print("HTML Structure completely repaired and updated to 6 dimensions.")
