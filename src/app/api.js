/**
 * API Integration: Supabase Connection for the Rural Observatory
 * Optimized to use server-side views for performance and accuracy.
 */

const SUPABASE_URL = "https://kyzcdpcmgiisllxmnhqn.supabase.co";
const SUPABASE_KEY = "sb_publishable_DRWOVTb1-KWvTd35C_E18A_-L9RQtUJ";

const headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": `Bearer ${SUPABASE_KEY}`
};

/**
 * Fetch Aggregated PAA Data for the Line Chart (Historical Series)
 * Uses view_paa_anual to avoid API limits and guarantee accurate totals.
 */
async function fetchPaaAnnual() {
    const url = `${SUPABASE_URL}/rest/v1/view_paa_anual?select=ano,total_valor`;
    
    try {
        const response = await fetch(url, { headers });
        const data = await response.json();
        
        return data.map(d => ({
            ano: d.ano,
            valor: parseFloat(d.total_valor) / 1000000 // Convert to Mi R$
        }));
    } catch (e) {
        console.error("Error fetching annual PAA:", e);
        return [];
    }
}

/**
 * Fetch PAA by Territory for the Bar Chart
 * Uses view_paa_territorios filtered by current year.
 */
async function fetchPaaByTerritory() {
    const url = `${SUPABASE_URL}/rest/v1/view_paa_territorios?ano=eq.2024&select=nome_territorio,total_beneficiados&order=total_beneficiados.desc`;
    
    try {
        const response = await fetch(url, { headers });
        const data = await response.json();
        
        return data.map(d => ({
            nome: d.nome_territorio,
            valor: parseInt(d.total_beneficiados)
        }));
    } catch (e) {
        console.error("Error fetching territory PAA:", e);
        return [];
    }
}

/**
 * Fetch Filtered PAA Data for BI Canvas
 * Handles complex joins in the client or uses territorial views.
 */
async function fetchFilteredPAA(filters = {}) {
    let url = `${SUPABASE_URL}/rest/v1/paa_dados?sigla_uf=eq.RN`;
    
    if (filters.year && filters.year !== 'todos') {
        url += `&ano=eq.${filters.year}`;
    }
    
    if (filters.limit) {
        url += `&limit=${filters.limit}`;
    } else {
        url += `&limit=2000`; // Increase default limit for analysis
    }

    try {
        const response = await fetch(url, { headers });
        let data = await response.json();
        
        // Filter by territory if specified
        if (filters.territory && filters.territory !== 'todos') {
            const terrRes = await fetch(`${SUPABASE_URL}/rest/v1/territorios_rn?nome_territorio=eq.${filters.territory}`, { headers });
            const terrMapData = await terrRes.json();
            const allowedIds = terrMapData.map(t => t.cod_municipio_ibge.toString());
            data = data.filter(d => allowedIds.includes(d.cod_municipio_ibge.toString()));
        }
        
        return data;
    } catch (e) {
        console.error("BI Filter error:", e);
        return [];
    }
}

/**
 * Global API Object
 */
window.API = {
    fetchPaaAnnual,
    fetchPaaByTerritory,
    fetchFilteredPAA,
    
    async exportPAA() {
        console.log("📥 Preparando exportação de dados...");
        const data = await this.fetchFilteredPAA({ limit: 10000 });
        const csv = "Ano;Municipio;Valor;Beneficiarios\n" + 
            data.map(d => `${d.ano};${d.nome_municipio};${d.val_executado};${d.qtd_beneficiados}`).join("\n");
        
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `paa_dados_rn_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
    }
};
