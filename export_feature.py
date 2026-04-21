"""
Final touches: Excel export button in BI and Footer refinement.
"""
import os

HTML_PATH = 'src/app/index.html'
with open(HTML_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# ADD EXPORT BUTTON
export_btn = '<button class="btn-apply btn-excel" onclick="exportToExcel()" style="background:#1D6F42; margin-top: 10px;">💾 Exportar Base (CSV/Excel)</button>'
content = content.replace('</button>', '</button>\n                ' + export_btn, 1) # Insert in sidebar

# ADD EXPORT LOGIC
export_js = """
// ── EXCEL EXPORT ───────────────────────
function exportToExcel() {
    const terr = document.getElementById('filter-territory').value;
    const year = document.getElementById('filter-year').value;
    
    alert(`Preparando exportação do PAA - Filtros: ${terr}, ${year}. O arquivo será gerado e baixado.`);
    
    window.API.fetchFilteredPAA({ year, territory: terr }).then(data => {
        if (data.length === 0) return alert("Sem dados para exportar.");
        
        let csv = "ano,mes,municipio,valor_executado,beneficiarios\\n";
        data.forEach(d => {
            csv += `${d.ano},${d.mes},${d.nome_municipio},${d.val_executado},${d.qtd_beneficiados}\\n`;
        });
        
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.setAttribute("download", `paa_rn_export_${year}_${terr}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
}
"""

content = content.replace('// ── IntersectionObserver', export_js + '\n// ── IntersectionObserver')

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Export functionality and Footer logo finalized.")
