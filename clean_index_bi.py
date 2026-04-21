"""
Refining index.html: removing duplicates and creating a professional BI teaser module.
"""
import os

HTML_PATH = 'src/app/index.html'
with open(HTML_PATH, 'r', encoding='utf-8') as f:
    full_content = f.read()

# 1. REMOVE DUPLICATE MODULE
# Found near line 365
duplicate_start = '<!-- ══════════ INDICADORES DINÂMICOS ══════════ -->'
duplicate_end = '<!-- ══════════ ESTATÍSTICAS (placeholder) ══════════ -->'
try:
    start_idx = full_content.index(duplicate_start)
    end_idx = full_content.index(duplicate_end)
    full_content = full_content[:start_idx] + full_content[end_idx:]
except ValueError:
    print("Warning: Could not find exact duplicate markers. Proceeding with manual block replacement.")

# 2. TRANSFORM TEASER INTO "BLUE MODULO" STATS SECTION
old_teaser = """
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

new_stats_module = """
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
                <a href="/static/dashboard.html" class="btn-primary-amber mt-4">🚀 Entrar no Painel de BI</a>
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

# Replace the messy sections
full_content = full_content.replace(old_teaser, new_stats_module)

# Remove the placeholder section if it still exists
full_content = full_content.replace('<section class="section-dark" id="estatisticas-placeholder">', '<!-- REMOVED -->')

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(full_content)

print("Index.html cleaned: Duplicates removed and BI teaser upgraded to Blue Module.")
