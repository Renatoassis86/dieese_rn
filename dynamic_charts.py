"""
Injecting API layer and making charts real-time (reactive to Supabase data).
Fixed substring matching.
"""
import os

HTML_PATH = 'src/app/index.html'

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. ADD SCRIPT TAG
if '<script src="/static/api.js"></script>' not in content:
    content = content.replace(
        '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>',
        '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>\n    <script src="/static/api.js"></script>'
    )

# 2. OVERWRITE SCRIPT SECTION FOR REACTIVITY
# Find from Paleta de cores to initCharts end
try:
    script_start = content.index('// ── Paleta de cores DIEESE')
    # Finding the end of initCharts (line 554 in previous view)
    # We find the intersection observer start as marker
    script_end = content.index('// ── KPI Counter animado', script_start)

    new_script = """// ── CONFIGS GERAIS — CORES ──────────────────
const GREEN = '#2D6A4F';
const AMBER = '#F4A261';
const NAVY  = '#0D1B2A';
const GREENS = ['#1B4332','#2D6A4F','#40916C','#52B788','#74C69D','#95D5B2','#B7E4C7','#D8F3DC'];

// ── INITIALIZATION ──────────────────────
let chartsInit = false;

async function initCharts() {
    if (chartsInit) return;
    chartsInit = true;
    
    console.log("📊 Carregando dados do Supabase...");
    
    // Global defaults
    Chart.defaults.font.family = "'Montserrat', sans-serif";
    Chart.defaults.color = '#4A5568';

    // Fetch real data from API
    const [paaAnual, paaTerrit] = await Promise.all([
        window.API.fetchPaaAnnual(),
        window.API.fetchPaaByTerritory()
    ]);

    // 1. LINHA — Evolução PAA
    if (paaAnual.length > 0) {
        new Chart(document.getElementById('chartLinha'), {
            type: 'line',
            data: {
                labels: paaAnual.map(d => d.ano),
                datasets: [{
                    label: 'Execução PAA (Milhões R$)',
                    data: paaAnual.map(d => d.valor),
                    borderColor: GREEN,
                    backgroundColor: 'rgba(45, 106, 79, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 3,
                    pointRadius: 4,
                    pointBackgroundColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                plugins: { 
                    legend: { display: false },
                    tooltip: { callbacks: { label: ctx => ` R$ ${ctx.parsed.y.toFixed(1)} Mi` } }
                },
                scales: {
                    y: { beginAtZero: true, ticks: { callback: v => `R$ ${v}Mi` } }
                }
            }
        });
        
        // Update KPIs based on data
        const total = paaAnual.reduce((acc, curr) => acc + curr.valor, 0);
        const kpiTotal = document.querySelector('[data-target="12.7"]');
        if (kpiTotal) {
            kpiTotal.dataset.target = total.toFixed(1);
            // Counter will trigger via intersection observer in index.html
        }
    }

    // 2. BARRAS — Territórios
    if (paaTerrit.length > 0) {
        const topTerrit = paaTerrit.slice(0, 8);
        new Chart(document.getElementById('chartTerrit'), {
            type: 'bar',
            data: {
                labels: topTerrit.map(d => d.nome),
                datasets: [{
                    label: 'Agricultores Beneficiários',
                    data: topTerrit.map(d => d.valor),
                    backgroundColor: GREENS,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                plugins: { 
                    legend: { display: false },
                    tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.y.toLocaleString('pt-BR')} agricultores` } }
                },
                scales: {
                    y: { beginAtZero: true },
                    x: { ticks: { font: { size: 10 } } }
                }
            }
        });
    }

    initStaticCharts();
}

function initStaticCharts() {
    // 3. RANKING NE (Manual reference)
    new Chart(document.getElementById('chartRanking'), {
        type: 'bar',
        data: {
            labels: ['BA', 'PE', 'CE', 'MA', 'PI', 'RN', 'PB', 'AL', 'SE'],
            datasets: [{
                label: 'Ticket Médio (R$)',
                data: [6850, 5920, 5240, 4810, 4200, 3980, 3650, 3420, 3100],
                backgroundColor: ['#2D6A4F','#2D6A4F','#2D6A4F','#2D6A4F','#2D6A4F','#F4A261','#2D6A4F','#2D6A4F','#2D6A4F'],
                borderRadius: 6
            }]
        },
        options: { indexAxis: 'y', plugins: { legend: { display: false } } }
    });

    // 4. DONUT (Modalidades)
    new Chart(document.getElementById('chartModalidade'), {
        type: 'doughnut',
        data: {
            labels: ['CDS (Alimentos)', 'PAA Leite', 'Sementes', 'Form. Estoque'],
            datasets: [{
                data: [62, 25, 8, 5],
                backgroundColor: ['#2D6A4F','#40916C','#F4A261','#0D1B2A']
            }]
        },
        options: { cutout: '65%', plugins: { legend: { position: 'bottom' } } }
    });
}
"""

    content = content[:script_start] + new_script + content[script_end:]

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print("UI updated successfully with real-time charts.")

except ValueError as e:
    print(f"Error: Substring not found. Details: {e}")
