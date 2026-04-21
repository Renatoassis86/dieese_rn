"""
Bugfix in BI charting logic.
"""
import os

HTML_PATH = 'src/app/index.html'

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'munSum[d.nome_municipio] = (munSum[d.nome_municipio] || 0) + parseFloat(curr.val_executado);',
    'munSum[d.nome_municipio] = (munSum[d.nome_municipio] || 0) + parseFloat(d.val_executado);'
)

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(content)
