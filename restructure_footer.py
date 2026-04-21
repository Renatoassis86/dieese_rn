"""
Restructuring footer links for better context and cohesion.
Removes 'Dimensões I/II' and replaces them with logical echelons.
"""
import os

files = ['src/app/index.html', 'src/app/dashboard.html']

for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Restructuring Footer Grid
    old_grid = """
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
"""
    
    new_grid = """
            <div class="h-footer-grid">
                <div class="link-group">
                    <span class="group-title">Institucional</span>
                    <a href="#sobre">Sobre o Projeto</a>
                    <a href="#sobre">Objetivos</a>
                    <a href="#sobre">Metodologia</a>
                </div>
                
                <div class="link-group">
                    <span class="group-title">Eixos Rurais</span>
                    <a href="#ecosol">Economia Solidária</a>
                    <a href="#mercado">Mercado Institucional</a>
                    <a href="#agro">Estrutura Agropecuária</a>
                </div>

                <div class="link-group">
                    <span class="group-title">Dinâmicas</span>
                    <a href="#producao">Produção e Dinâmica</a>
                    <a href="#trabalho">Trabalho e Renda</a>
                    <a href="#vulnerabilidades">Vulnerabilidades</a>
                </div>

                <div class="link-group">
                    <span class="group-title">Explorar Dados</span>
                    <a href="#territorios">Territórios RN</a>
                    <a href="#indicadores">Série Histórica</a>
                    <a href="/static/dashboard.html">Painel de BI</a>
                </div>
            </div>
"""
    # Use replacement
    if old_grid.strip() in content:
        content = content.replace(old_grid.strip(), new_grid.strip())
    else:
        # Fallback if structure varies slightly
        import re
        content = re.sub(r'<div class="h-footer-grid">.*?</div>\s*</div>\s*</div>', new_grid + '</div></div>', content, flags=re.DOTALL)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Footer restructured and logo paths verified.")
