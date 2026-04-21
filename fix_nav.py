"""Fix the corrupted nav section in index.html"""
with open('src/app/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the entire nav block
start = content.index('<nav>')
end = content.index('</nav>') + 6

new_nav = """<nav>
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
        </nav>"""

content = content[:start] + new_nav + content[end:]

with open('src/app/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('NAV fixed successfully!')
