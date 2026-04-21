"""
Restoring original horizontal footer and implementing BI-style statistics section.
"""
import os

HTML_PATH = 'src/app/index.html'

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. RESTORE FOOTER (Horizontal Format)
footer_start = content.index('<footer')
footer_end = content.index('</footer>') + 9

new_footer = """<footer class="footer">
    <div class="container h-footer-container">
        <div class="h-footer-top">
            <div class="h-footer-brand">
                <img src="/static/logo.png" alt="DIEESE" class="footer-logo-img-h">
                <p>Departamento Intersindical de Estatística e Estudos Socioeconômicos</p>
            </div>
            <div class="h-footer-links">
                <div class="link-group">
                    <span class="group-title">Institucional</span>
                    <a href="#sobre">Projeto</a>
                    <a href="#sobre">Objetivos</a>
                </div>
                <div class="link-group">
                    <span class="group-title">Dimensões</span>
                    <a href="#ecosol">Economia Solidária</a>
                    <a href="#mercado">M. Institucional</a>
                </div>
            </div>
            <div class="h-footer-contact">
                <span class="group-title">Contatos</span>
                <p>📞 (11) 3874-5366</p>
                <p>📧 en@dieese.org.br</p>
            </div>
        </div>
        <div class="h-footer-bottom">
            <p>&copy; 2024-2026 Observatório do Trabalho e de Políticas Sociais do RN. Todos os direitos reservados.</p>
        </div>
    </div>
</footer>"""

content = content[:footer_start] + new_footer + content[footer_end:]

# 2. REDESIGN STATISTICS SECTION (BI MODULE)
estat_start = content.index('<section class="section-dark" id="estatisticas">')
# The section often goes until the script or next tag. I'll replace the block.
# Let's find the indicators section to be safe
try:
    indic_start = content.index('<!-- ══════════ INDICADORES')
    estat_end = indic_start
except:
    estat_end = content.index('<script')

new_estat = """<!-- ══════════ PAINEL DE INFORMAÇÕES (BI) ══════════ -->
<section class="bi-section" id="estatisticas">
    <div class="container">
        <div class="bi-header text-center">
            <p class="kicker">— ACESSO À INFORMAÇÃO —</p>
            <h1 class="bi-title">PAINEL DE INFORMAÇÕES DO OBSERVATÓRIO</h1>
            <p class="bi-date">ATUALIZADO EM ABRIL DE 2026</p>
            
            <div class="bi-nav-icons">
                <div class="bi-nav-item active" onclick="switchBIMode('paa')">
                    <div class="bi-icon">📈</div>
                    <span>Principais Resultados</span>
                </div>
                <div class="bi-nav-item" onclick="switchBIMode('setorial')">
                    <div class="bi-icon">⚙️</div>
                    <span>Dados Setoriais</span>
                </div>
                <div class="bi-nav-item" onclick="switchBIMode('sobre')">
                    <div class="bi-icon">📋</div>
                    <span>Sobre o Painel</span>
                </div>
            </div>
        </div>

        <div class="bi-module">
            <!-- Sidebar de Filtros -->
            <div class="bi-sidebar">
                <h3>🔍 Filtros Global</h3>
                <div class="filter-group">
                    <label>Dimensão do Estudo</label>
                    <select id="filter-dim">
                        <option value="mercado">Mercado Institucional (PAA/PNAE)</option>
                        <option value="ecosol">Economia Solidária</option>
                        <option value="agro">Estrutura Agropecuária</option>
                        <option value="trabalho">Trabalho e Renda</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Território de Identidade</label>
                    <select id="filter-territory">
                        <option value="todos">Todos os Territórios</option>
                        <option value="Seridó">Seridó</option>
                        <option value="Alto Oeste">Alto Oeste</option>
                        <option value="Mato Grande">Mato Grande</option>
                        <option value="Potengi">Potengi</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Período (Ano)</label>
                    <select id="filter-year">
                        <option value="todos">Série Histórica</option>
                        <option value="2024">2024</option>
                        <option value="2023">2023</option>
                        <option value="2022">2022</option>
                    </select>
                </div>
                <button class="btn-apply" onclick="applyFilters()">Gerar Diagnóstico ✓</button>
            </div>

            <!-- Área de Conteúdo Pro Max -->
            <div class="bi-content">
                <div class="bi-status-bar">
                    <span>📍 Visualizando: <strong>Rio Grande do Norte</strong></span>
                    <span id="bi-sync-status">🟢 Conectado ao Supabase</span>
                </div>
                
                <div id="bi-placeholder" class="bi-canvas">
                    <div class="canvas-empty">
                        <div class="loader-spinner"></div>
                        <p>Selecione as dimensões e clique em <strong>Gerar Diagnóstico</strong> para processar os quadros estatísticos.</p>
                    </div>
                </div>
                
                <div id="bi-charts" class="bi-canvas" style="display:none;">
                    <div class="bi-grid">
                        <div class="bi-card">
                            <h5>Execução Financeira por Ano</h5>
                            <canvas id="chartBI-Line"></canvas>
                        </div>
                        <div class="bi-card">
                            <h5>Distribuição Territorial</h5>
                            <canvas id="chartBI-Bar"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
"""

content = content[:estat_start] + new_estat + content[estat_end:]

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

# 3. CSS UPDATES FOR HORIZONTAL FOOTER AND BI
CSS_PATH = 'src/app/style.css'
with open(CSS_PATH, 'a', encoding='utf-8') as f:
    f.write("""
/* ── HORIZONTAL FOOTER ────────────────── */
.footer { border-top: 1px solid rgba(255,255,255,0.1); padding: 4rem 0 2rem; background: #07101a; }
.h-footer-container { display: flex; flex-direction: column; gap: 3rem; }
.h-footer-top { display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 4rem; }
.h-footer-brand p { font-size: 0.9rem; color: rgba(255,255,255,0.7); margin-top: 1rem; max-width: 400px; }
.footer-logo-img-h { height: 45px; width: auto; filter: brightness(0) invert(1); }
.link-group { display: flex; flex-direction: column; gap: 0.8rem; margin-bottom: 1.5rem; }
.group-title { color: var(--amber); font-weight: 800; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; display: block; margin-bottom: 0.5rem; }
.h-footer-links a { color: #fff; font-size: 0.9rem; opacity: 0.8; transition: 0.3s; }
.h-footer-links a:hover { opacity: 1; color: var(--amber); }
.h-footer-contact p { font-size: 0.85rem; margin-bottom: 0.5rem; }
.h-footer-bottom { border-top: 1px solid rgba(255,255,255,0.05); padding-top: 2rem; text-align: center; }
.h-footer-bottom p { font-size: 0.8rem; color: rgba(255,255,255,0.5); }

/* ── BI MODULE STYLES ────────────────── */
.bi-section { padding: 8rem 0; background: #0D1B2A; color: #fff; }
.bi-title { font-size: 2.8rem; font-weight: 900; letter-spacing: -0.02em; margin: 1rem 0; }
.bi-date { font-weight: 600; color: var(--amber); font-size: 0.9rem; opacity: 0.9; }

.bi-nav-icons { display: flex; justify-content: center; gap: 4rem; margin-top: 3rem; margin-bottom: 4rem; }
.bi-nav-item { cursor: pointer; text-align: center; opacity: 0.5; transition: 0.3s; }
.bi-nav-item.active { opacity: 1; transform: translateY(-5px); }
.bi-nav-item .bi-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.bi-nav-item span { font-weight: 800; font-size: 0.9rem; text-transform: uppercase; }

.bi-module { display: grid; grid-template-columns: 320px 1fr; background: #fff; border-radius: 20px; overflow: hidden; box-shadow: 0 30px 60px rgba(0,0,0,0.4); min-height: 650px; }
.bi-sidebar { background: #f8fafc; padding: 2.5rem; border-right: 1px solid #e2e8f0; color: #1e293b; }
.bi-sidebar h3 { font-size: 1.1rem; font-weight: 900; margin-bottom: 2rem; color: var(--navy); }
.filter-group { margin-bottom: 1.5rem; }
.filter-group label { display: block; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; margin-bottom: 0.5rem; color: #64748b; }
.filter-group select { width: 100%; padding: 0.8rem; border-radius: 10px; border: 2px solid #e2e8f0; font-family: inherit; font-weight: 600; outline: none; transition: 0.3s; }
.filter-group select:focus { border-color: var(--green); }
.btn-apply { width: 100%; padding: 1.2rem; background: var(--navy); color: #fff; border: none; border-radius: 12px; font-weight: 800; cursor: pointer; margin-top: 1rem; transition: 0.3s; }
.btn-apply:hover { background: var(--green); transform: translateY(-2px); }

.bi-content { background: #fff; padding: 0; display: flex; flex-direction: column; }
.bi-status-bar { border-bottom: 1px solid #f1f5f9; padding: 1rem 2.5rem; display: flex; justify-content: space-between; align-items: center; background: #fdfdfd; font-size: 0.8rem; color: #64748b; }
.bi-canvas { padding: 3rem; flex: 1; display: flex; flex-direction: column; }
.canvas-empty { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; color: #94a3b8; }
.canvas-empty p { max-width: 400px; margin-top: 1.5rem; font-weight: 600; }
.loader-spinner { width: 40px; height: 40px; border: 4px solid #f1f5f9; border-top-color: var(--amber); border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.bi-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
.bi-card { background: #f8fafc; padding: 2rem; border-radius: 15px; border: 1px solid #f1f5f9; }
.bi-card h5 { margin-bottom: 1.5rem; font-weight: 800; color: var(--navy); }
""")

print("UI Re-orchestrated: BI Panel implemented and Footer restored to horizontal format.")
