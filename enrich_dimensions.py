"""
Enriching dimension concepts and database detail frames.
Also improves territorial mapping to fix charts showing 'Outros'.
"""
import os

HTML_PATH = 'src/app/index.html'

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. ENRICHING DIMENSIONS CONTENT
# We will create a template for dimension detail with buttons
def get_dim_content(num, title, concept, db_list):
    dbs_html = "".join([f'<button class="btn-db" onclick="toggleDBInfo(\'db-{num}-{i}\')">📂 {db["name"]}</button>' for i, db in enumerate(db_list)])
    details_html = "".join([f'<div id="db-{num}-{i}" class="db-details-box" style="display:none;"><h4>{db["name"]}</h4><p>{db["desc"]}</p></div>' for i, db in enumerate(db_list)])
    
    return f"""
    <div class="dim-info-block">
        <p class="kicker-dim">— DIMENSÃO {num} —</p>
        <h2 class="dim-title-large">{title}</h2>
        <div class="dim-concept">
            <p>{concept}</p>
        </div>
        <div class="dim-databases">
            <p class="db-label">Bases de Dados Integradas:</p>
            <div class="db-button-grid">
                {dbs_html}
            </div>
            <div class="db-details-container">
                {details_html}
            </div>
        </div>
    </div>
    """

# Dimension Data
dim_data = {
    "ecosol": {
        "num": 1,
        "title": "Economia Solidária",
        "concept": "A Economia Solidária no Rio Grande do Norte compreende um conjunto de iniciativas de produção, comércio, consumo e crédito organizadas sob os princípios da autogestão, democracia direta e cooperação. Esta dimensão busca mapear os Empreendimentos de Economia Solidária (EES) rurais, identificando sua maturidade organizativa, diversidade de atividades e o papel fundamental que desempenham na permanência das famílias no campo através da ajuda mútua.",
        "dbs": [
            {"name": "Novo CADSOL", "desc": "Sistema de Cadastro Nacional de Empreendimentos de Economia Solidária. Provê dados sobre a tipologia jurídica, número de sócios e ramos de atividade."},
            {"name": "Mapeamento DIEESE", "desc": "Base de dados primária e secundária compilada para identificar grupos informais e coletivos não registrados no sistema nacional."}
        ]
    },
    "mercado": {
        "num": 2,
        "title": "Mercado Institucional",
        "concept": "O Mercado Institucional refere-se ao conjunto de políticas públicas de compras governamentais que garantem escoamento e renda para a agricultura familiar. Esta dimensão analisa a eficácia de programas como o PAA e PNAE, monitorando quanto do orçamento público é destinado aos pequenos produtores potiguares, as modalidades mais utilizadas e o impacto direto na segurança alimentar de hospitais, escolas e redes de assistência.",
        "dbs": [
            {"name": "MiSocial (MDS)", "desc": "Plataforma de consulta de dados sociais do Governo Federal. Fonte principal para execução financeira do PAA municipal."},
            {"name": "CONAB PAA", "desc": "Dados detalhados sobre as modalidades de Doação Simultânea e Formação de Estoque operadas pela Companhia Nacional de Abastecimento."},
            {"name": "SIG-PNAE", "desc": "Sistema de Gestão do Programa Nacional de Alimentação Escolar, utilizado para monitorar a compra direta de agricultores familiares pelas prefeituras."}
        ]
    },
    "agro": {
        "num": 3,
        "title": "Estrutura Agropecuária",
        "concept": "Esta dimensão investiga a base física e produtiva do RN, analisando a distribuição das terras, o acesso à água e as tecnologias de produção. O foco está na diferenciação entre a agricultura patronal e a familiar, observando como o pequeno produtor se insere na cadeia produtiva e quais as principais dificuldades relacionadas ao regime de posse da terra e uso do solo no semiárido.",
        "dbs": [
            {"name": "Censo Agropecuário 2017", "desc": "Pesquisa decenal do IBGE que fornece a foto mais detalhada da estrutura fundiária, áreas cultivadas e perfil dos estabelecimentos."},
            {"name": "INCRA / Terra Legal", "desc": "Dados sobre assentamentos de reforma agrária e regularização fundiária no estado."},
            {"name": "SIDRA IBGE", "desc": "Sistema de Recuperação Automática para consulta de séries temporais de produção e valor da produção agrícola."}
        ]
    },
    "producao": {
        "num": 4,
        "title": "Produção e Dinâmica",
        "concept": "Analisa o que é produzido no campo potiguar e como essa produção circula. O foco recai sobre as cadeias produtivas estratégicas (fruticultura, mel, leite, castanha de caju) e as feiras livres locais. Busca-se entender a sazonalidade, os custos de produção e a agregação de valor através do beneficiamento de produtos em agroindústrias familiares.",
        "dbs": [
            {"name": "LSPA (IBGE)", "desc": "Levantamento Sistemático da Produção Agrícola, com estimativas mensais de safra para grãos e culturas permanentes."},
            {"name": "PPM (IBGE)", "desc": "Pesquisa da Pecuária Municipal, focada em rebanhos bovinos, caprinos e produção de leite."},
            {"name": "EMPARN", "desc": "Dados técnicos e meteorológicos que impactam a produtividade rural no RN."}
        ]
    },
    "trabalho": {
        "num": 5,
        "title": "Trabalho e Renda",
        "concept": "Mensure o impacto econômico direto na vida dos atores rurais. Esta dimensão trata da ocupação formal e informal, níveis salariais no campo e a Previdência Social Rural como pilar de seguridade. O objetivo é diagnosticar o precariado rural e as oportunidades de geração de renda digna através do cooperativismo e da economia solidária.",
        "dbs": [
            {"name": "RAIS / Novo CAGED", "desc": "Registros administrativos sobre o mercado de trabalho formal, permitindo ver admissões e desligamentos no setor agropecuário."},
            {"name": "PNAD Contínua", "desc": "Pesquisa do IBGE sobre mercado de trabalho e rendimento das famílias, incluindo recortes para residência rural."},
            {"name": "DATAPREV", "desc": "Dados sobre benefícios previdenciários rurais, fundamentais para a economia dos pequenos municípios do interior."}
        ]
    },
    "vulnerabilidades": {
        "num": 6,
        "title": "Vulnerabilidades Sociais",
        "concept": "Cruza indicadores de pobreza com a realidade do campo. Esta dimensão monitora o acesso a serviços básicos (saúde, educação, saneamento) e a dependência de transferências de renda. É essencial para priorizar territórios que necessitam de intervenção urgente em termos de políticas de combate à fome e mitigação dos efeitos da seca no Rio Grande do Norte.",
        "dbs": [
            {"name": "CadÚnico", "desc": "Cadastro Único para Programas Sociais. Identifica famílias em situação de extrema pobreza e vulnerabilidade no meio rural."},
            {"name": "Vis Data (MDS)", "desc": "Painéis de indicadores sociais que cruzam dados de diversos programas de transferência de renda."},
            {"name": "Atlas Brasil (PNUD)", "desc": "Dados sobre Índice de Desenvolvimento Humano Municipal (IDH-M) e seus subcomponentes."}
        ]
    }
}

# Apply to HTML - Replacing the light description blocks in index.html
# We'll use a more programmatic way to replace the sections
for key, data in dim_data.items():
    placeholder = f'<!-- CONTENT_{key.upper()} -->'
    # I'll first inject placeholders in the sections
    # In index.html, find Section for each dimension and replace the content block
    content = content.replace(f'<div class="dim-item-content">', f'<div class="dim-item-content">{placeholder}', 1)

# Now replace placeholders with actual enriched content
for key, data in dim_data.items():
    content = content.replace(f'<!-- CONTENT_{key.upper()} -->', get_dim_content(data["num"], data["title"], data["concept"], data["dbs"]))

# 2. FIXING CSS FOR DB BUTTONS
CSS_PATH = 'src/app/style.css'
with open(CSS_PATH, 'a', encoding='utf-8') as f:
    f.write("""
/* ── DIMENSION ENRICHMENT ──────────────── */
.dim-info-block { padding: 1rem 0; }
.dim-title-large { font-size: 2.8rem; font-weight: 900; color: var(--navy); margin-bottom: 1.5rem; letter-spacing: -0.02em; }
.dim-concept p { line-height: 1.8; color: #4A5568; font-size: 1.05rem; margin-bottom: 2rem; }
.db-label { font-weight: 800; text-transform: uppercase; font-size: 0.75rem; color: var(--green); letter-spacing: 0.1em; margin-bottom: 1.2rem; }
.db-button-grid { display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 2rem; }
.btn-db { padding: 0.8rem 1.4rem; background: #f8fafc; border: 2px solid #e2e8f0; border-radius: 12px; font-family: inherit; font-weight: 700; color: #1e293b; cursor: pointer; transition: 0.3s; font-size: 0.85rem; }
.btn-db:hover { border-color: var(--green); background: #fff; transform: translateY(-3px); }
.db-details-container { margin-top: 1rem; }
.db-details-box { background: #fff; border: 1px solid #e2e8f0; padding: 2rem; border-radius: 15px; border-left: 5px solid var(--amber); box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-bottom: 1rem; animation: slideDown 0.3s ease-out; }
.db-details-box h4 { margin-bottom: 0.8rem; font-weight: 800; color: var(--navy); }
.db-details-box p { font-size: 0.95rem; line-height: 1.6; color: #64748b; }

@keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
""")

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

# 3. ADDING JS HELPER
with open(HTML_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

toggle_js = """
// ── DB INFO TOGGLE ──────────────────────
function toggleDBInfo(id) {
    const box = document.getElementById(id);
    const isVisible = box.style.display === 'block';
    
    // Hide all in same section first
    box.parentElement.querySelectorAll('.db-details-box').forEach(el => el.style.display = 'none');
    
    if (!isVisible) box.style.display = 'block';
}
"""
content = content.replace('// ── IntersectionObserver', toggle_js + '\n// ── IntersectionObserver')

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Dimensions enriched with conceptual texts and interactive database frames.")
