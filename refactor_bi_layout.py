"""
Finalizing BI module layout (landing page):
- Uses standard dim-grid for visual consistency.
- Adopts Cidade Viva illustration shape for the video.
- Reduces padding to fit 100% zoom.
- Removes redundant frames.
"""
import os

INDEX_PATH = 'src/app/index.html'
with open(INDEX_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the bi-stats-module with a more integrated version
old_bi = """
<!-- ══════════ PAINEL DE ESTATÍSTICAS (BI) ══════════ -->
<section id="estatisticas" class="section-dark bi-stats-module">
    <div class="container">
        <div class="bi-stats-grid">
            <div class="bi-stats-info text-left">
                <p class="kicker kicker-light">— INTELIGÊNCIA DE DADOS —</p>
                <h2 class="text-white">Diagnóstico Territorial & BI</h2>
                <p class="stats-description">
                    Utilize nossa inteligência de dados para gerar tabelas e indicadores dinâmicos. 
                    O objetivo deste painel é subsidiar o planejamento institucional através de 
                    diagnósticos personalizados por território de identidade, período e dimensão do estudo.
                </p>
                <div class="stats-features">
                    <div class="feature-item">✓ Geração de Quadros Estatísticos</div>
                    <div class="feature-item">✓ Filtros por 10 Territórios de RN</div>
                    <div class="feature-item">✓ Exportação para Excel e CSV</div>
                </div>
                <a href="/static/dashboard.html" class="btn-bi-premium mt-4">
                    <span>Entrar no Painel de BI</span>
                    <i class="fas fa-rocket"></i>
                </a>
            </div>
            <div class="bi-stats-preview">
                <div class="preview-card-glass">
                    <img src="/static/assets/video2.mp4" alt="Visualização BI" style="display:none;"> <!-- Placeholder if video removed -->
                    <div class="geometric-mask-v3">
                         <video autoplay muted loop playsinline class="video-contain-full">
                            <source src="/static/assets/video2.mp4" type="video/mp4">
                        </video>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
"""

new_bi = """
<!-- ══════════ PAINEL DE INTELIGÊNCIA DE DADOS (BI) ══════════ -->
<section id="estatisticas" class="dim-section section-dark" style="padding: 4rem 0; overflow: hidden;">
    <div class="container dim-grid">
        <div class="dim-content text-left">
            <p class="kicker kicker-light">— INTELIGÊNCIA DE DADOS —</p>
            <h2 class="text-white">Diagnóstico Territorial & BI</h2>
            <p class="text-muted" style="font-size: 1.05rem; opacity: 0.85; line-height: 1.6; margin-bottom: 2rem;">
                Utilize nossa inteligência de dados para gerar tabelas e indicadores dinâmicos. 
                Subsidie o planejamento institucional com diagnósticos personalizados por território, período e dimensão do estudo.
            </p>
            <div class="dim-bases" style="margin-top: 0;">
                <div class="base-tag">📊 Gerador de Quadros</div>
                <div class="base-tag">🗺️ 10 Territórios</div>
                <div class="base-tag">📥 Exportação XLSX</div>
            </div>
            <div style="margin-top: 2.5rem;">
                <a href="/static/dashboard.html" class="btn-bi-premium">
                    <span>Entrar no Painel de BI</span>
                    <i class="fas fa-rocket"></i>
                </a>
            </div>
        </div>
        <div class="dim-illust">
            <div class="illust-wrap" style="box-shadow: 0 20px 60px rgba(0,0,0,0.4); border-color: rgba(255,255,255,0.1);">
                <video autoplay muted loop playsinline style="width: 100%; height: 100%; object-fit: cover;">
                    <source src="/static/assets/video2.mp4" type="video/mp4">
                </video>
                <div class="illust-caption">Painel de Monitoramento e BI</div>
            </div>
        </div>
    </div>
</section>
"""

if old_bi.strip() in content:
    content = content.replace(old_bi.strip(), new_bi.strip())
else:
    # Fallback using regex if slightly changed
    import re
    content = re.sub(r'<!-- ══════════ PAINEL DE ESTATÍSTICAS \(BI\) ══════════ -->.*?<section id="estatisticas".*?</section>', new_bi.strip(), content, flags=re.DOTALL)

with open(INDEX_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("BI module refactored to match site standards.")
