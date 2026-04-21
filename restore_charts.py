"""
Restoring missing initCharts function and fixing duplicate IDs.
"""
import os

HTML_PATH = 'src/app/index.html'
with open(HTML_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. FIX DUPLICATE IDs and RESTORE FUNCTION
# The teaser has id="estatisticas"
# The section-dark below it ALSO has id="estatisticas"
content = content.replace('<section class="section-dark" id="estatisticas">', '<section class="section-dark" id="estatisticas-placeholder">')

# 2. RESTORE initCharts() definition
# It should start before line 601 (which was the start of fetchPaaAnual logic in the view_file earlier)
if 'async function initCharts() {' not in content:
    # Find where the script starts
    script_pattern = 'let chartsInit = false;'
    restore_code = """let chartsInit = false;

async function initCharts() {
    if (chartsInit) return;
    chartsInit = true;
    
    console.log("📊 Carregando dados do Supabase...");
    
    Chart.defaults.font.family = "'Montserrat', sans-serif";
    Chart.defaults.color = '#4A5568';

    const [paaAnual, paaTerrit] = await Promise.all([
        window.API.fetchPaaAnnual(),
        window.API.fetchPaaByTerritory()
    ]);
"""
    content = content.replace(script_pattern, restore_code)

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("initCharts definition restored and duplicate IDs fixed.")
