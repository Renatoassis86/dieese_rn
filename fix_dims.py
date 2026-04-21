"""Replace old 5 dimensions with official 6 dimensions in index.html"""
with open('src/app/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the old dimensions (from DIM 1: PAA to end of DIM 5: CADEIAS)
start_marker = '<!-- ══════════ DIM 1: PAA ══════════ -->'
end_marker = '<!-- ══════════ TERRITÓRIOS ══════════ -->'

start = content.index(start_marker)
end = content.index(end_marker)

new_dims = """<!-- ══════════ DIM 1: ECONOMIA SOLIDÁRIA ══════════ -->
<section class="dim-section" id="ecosol">
    <div class="container dim-grid">
        <div class="dim-illust">
            <div class="illust-wrap">
                <img src="/static/assets/dim_coop.png" alt="Economia Solidária">
                <div class="illust-caption">Economia Solidária · Empreendimentos do RN</div>
            </div>
        </div>
        <div class="dim-content">
            <p class="kicker">— DIMENSÃO 1 —</p>
            <h2>Economia Solidária</h2>
            <p>Universo dos Empreendimentos Econômicos Solidários (EES) no RN: forma organizativa, atividade econômica, localização territorial e vínculos com políticas públicas de economia solidária.</p>
            <div class="dim-bases">
                <h5>Bases de dados utilizadas</h5>
                <div class="base-tag">📡 Novo CADSOL · Cadastro Nacional Eco. Solidária</div>
                <div class="base-tag">📡 Cadastros EES · Registros estaduais</div>
            </div>
            <div class="dim-metrics">
                <div class="metric-item"><span class="metric-val">167</span><span class="metric-label">Municípios</span></div>
                <div class="metric-item"><span class="metric-val">10</span><span class="metric-label">Territórios</span></div>
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
            <p>Inserção dos empreendimentos em compras públicas via PAA e PNAE: execução financeira, agricultores beneficiários, modalidades (CDS, Leite, Sementes) e potencial de mercado e logística de fornecimento no RN de <strong>2003 a 2024</strong>.</p>
            <div class="dim-bases">
                <h5>Bases de dados utilizadas</h5>
                <div class="base-tag">📡 MDS/SAGI · API MiSocial (PAA)</div>
                <div class="base-tag">📡 FNDE · PNAE (quando disponível)</div>
                <div class="base-tag">📡 CONAB · Compêndio de Execução</div>
            </div>
            <div class="dim-metrics">
                <div class="metric-item"><span class="metric-val">2003–2024</span><span class="metric-label">Série histórica</span></div>
                <div class="metric-item"><span class="metric-val">167</span><span class="metric-label">Municípios</span></div>
                <div class="metric-item"><span class="metric-val">5</span><span class="metric-label">Modalidades</span></div>
            </div>
            <a href="#indicadores" class="btn-primary-sm">Acessar dados ✓</a>
        </div>
        <div class="dim-illust">
            <div class="illust-wrap">
                <img src="/static/assets/dim_paa.png" alt="Mercado Institucional - PAA">
                <div class="illust-caption">PAA · Compras institucionais da agricultura familiar</div>
            </div>
        </div>
    </div>
</section>

<!-- ══════════ DIM 3: ESTRUTURA AGROPECUÁRIA ══════════ -->
<section class="dim-section" id="agro">
    <div class="container dim-grid">
        <div class="dim-illust">
            <div class="illust-wrap">
                <img src="/static/assets/dim_agro.png" alt="Estrutura Agropecuária">
                <div class="illust-caption">Censo Agropecuário · Perfil rural do RN</div>
            </div>
        </div>
        <div class="dim-content">
            <p class="kicker">— DIMENSÃO 3 —</p>
            <h2>Estrutura Agropecuária</h2>
            <p>Perfil rural do RN a partir do Censo Agropecuário do IBGE: número de estabelecimentos, agricultura familiar, área, uso da terra, vocações produtivas e base para recorte de cadeias por território.</p>
            <div class="dim-bases">
                <h5>Bases de dados utilizadas</h5>
                <div class="base-tag">📡 IBGE · Censo Agropecuário 2017</div>
                <div class="base-tag">📡 IBGE · SIDRA (tabelas especiais)</div>
            </div>
            <div class="dim-metrics">
                <div class="metric-item"><span class="metric-val">2017</span><span class="metric-label">Último Censo</span></div>
                <div class="metric-item"><span class="metric-val">Decenal</span><span class="metric-label">Periodicidade</span></div>
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
            <h2>Produção e<br>Dinâmica Territorial</h2>
            <p>Produção por cultura e rebanho, dinâmica territorial e apoio ao recorte de cadeias produtivas: cajucultura, fruticultura, caprinocultura, pesca artesanal, apicultura e beneficiamento de alimentos no RN.</p>
            <div class="dim-bases">
                <h5>Bases de dados utilizadas</h5>
                <div class="base-tag">📡 IBGE · PAM (Produção Agrícola Municipal)</div>
                <div class="base-tag">📡 IBGE · PPM (Pecuária Municipal)</div>
                <div class="base-tag">📡 IBGE · PEVS (Extração Vegetal e Silvicultura)</div>
            </div>
            <div class="dim-metrics">
                <div class="metric-item"><span class="metric-val">Anual</span><span class="metric-label">Periodicidade</span></div>
                <div class="metric-item"><span class="metric-val">12+</span><span class="metric-label">Cadeias mapeadas</span></div>
            </div>
            <span class="badge-dev">🚧 Em desenvolvimento</span>
        </div>
        <div class="dim-illust">
            <div class="illust-wrap">
                <img src="/static/assets/dim_cadeias.png" alt="Produção e Dinâmica">
                <div class="illust-caption">Cadeias produtivas · Produtos da AF no RN</div>
            </div>
        </div>
    </div>
</section>

<!-- ══════════ DIM 5: TRABALHO E RENDA ══════════ -->
<section class="dim-section" id="trabalho">
    <div class="container dim-grid">
        <div class="dim-illust">
            <div class="illust-wrap">
                <img src="/static/assets/dim_trabalho.png" alt="Trabalho e Renda">
                <div class="illust-caption">Trabalho formal · Ocupação e renda no campo</div>
            </div>
        </div>
        <div class="dim-content">
            <p class="kicker">— DIMENSÃO 5 —</p>
            <h2>Trabalho e Renda</h2>
            <p>Contexto de ocupação e renda no meio rural do RN: vínculos formais no setor agropecuário e agroindústria, remuneração média, sazonalidade, recortes por sexo/idade e território.</p>
            <div class="dim-bases">
                <h5>Bases de dados utilizadas</h5>
                <div class="base-tag">📡 IBGE · PNAD Contínua (trimestral)</div>
                <div class="base-tag">📡 MTE · RAIS (quando necessário)</div>
            </div>
            <div class="dim-metrics">
                <div class="metric-item"><span class="metric-val">Anual/trim.</span><span class="metric-label">Periodicidade</span></div>
                <div class="metric-item"><span class="metric-val">CNAE</span><span class="metric-label">Setor agropecuário</span></div>
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
            <h2>Vulnerabilidades<br>e Contexto Social</h2>
            <p>Condicionantes sociais que afetam a capacidade de organização e produção dos empreendimentos rurais: indicadores de pobreza, acesso a água, saneamento, educação e saúde, índices de desenvolvimento territorial.</p>
            <div class="dim-bases">
                <h5>Bases de dados utilizadas</h5>
                <div class="base-tag">📡 Indicadores e índices sociais (variável)</div>
                <div class="base-tag">📡 CadÚnico / Bolsa Família</div>
                <div class="base-tag">📡 IBGE · Censo Demográfico</div>
            </div>
            <div class="dim-metrics">
                <div class="metric-item"><span class="metric-val">Variável</span><span class="metric-label">Periodicidade</span></div>
                <div class="metric-item"><span class="metric-val">167</span><span class="metric-label">Municípios</span></div>
            </div>
            <span class="badge-dev">🚧 Em desenvolvimento</span>
        </div>
        <div class="dim-illust">
            <div class="illust-wrap">
                <img src="/static/assets/dim_vulnerabilidades.png" alt="Vulnerabilidades sociais">
                <div class="illust-caption">Contexto social · Indicadores de vulnerabilidade</div>
            </div>
        </div>
    </div>
</section>

"""

content = content[:start] + new_dims + content[end:]

with open('src/app/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('6 dimensions applied successfully!')
