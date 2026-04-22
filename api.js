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
 * Points to the new paa_master table.
 */
async function fetchPaaAnnual() {
    // Aggregated fetching: Must filter by UF and ensure year is valid
    const url = `${SUPABASE_URL}/rest/v1/paa_master?uf=eq.RN&ano=not.is.null&select=ano,valor_pago,agricultores,mulheres&limit=40000`;
    
    try {
        const response = await fetch(url, { headers });
        const rawData = await response.json();
        
        // Aggregate by year locally
        const aggregated = {};
        rawData.forEach(d => {
            if (!aggregated[d.ano]) aggregated[d.ano] = { valor: 0, agricultores: 0, mulheres: 0 };
            aggregated[d.ano].valor += parseFloat(d.valor_pago) || 0;
            aggregated[d.ano].agricultores += parseInt(d.agricultores) || 0;
            aggregated[d.ano].mulheres += parseInt(d.mulheres) || 0;
        });

        return Object.keys(aggregated)
            .filter(ano => parseInt(ano) >= 2011 && parseInt(ano) <= 2026)
            .map(ano => ({
            ano: parseInt(ano),
            valor: aggregated[ano].valor / 1000000, // Mi
            agricultores: aggregated[ano].agricultores,
            mulheres: aggregated[ano].mulheres,
            perc_mulheres: (aggregated[ano].mulheres / aggregated[ano].agricultores) * 100 || 0
        }));
    } catch (e) {
        console.error("Error fetching annual PAA:", e);
        return [];
    }
}

/**
 * Fetch PAA by Territory
 */
async function fetchPaaByTerritory(year = 2024) {
    const url = `${SUPABASE_URL}/rest/v1/paa_master?ano=eq.${year}&select=territorio,valor_pago,agricultores`;
    
    try {
        const response = await fetch(url, { headers });
        const data = await response.json();
        
        const aggregated = {};
        data.forEach(d => {
            if (!aggregated[d.territorio]) aggregated[d.territorio] = { valor: 0, agricultores: 0 };
            aggregated[d.territorio].valor += parseFloat(d.valor_pago) || 0;
            aggregated[d.territorio].agricultores += parseInt(d.agricultores) || 0;
        });

        return Object.keys(aggregated).map(t => ({
            nome: t,
            valor: aggregated[t].agricultores,
            investimento: aggregated[t].valor / 1000000
        })).sort((a, b) => b.valor - a.valor);
    } catch (e) {
        console.error("Error fetching territory PAA:", e);
        return [];
    }
}

/**
 * Fetch Filtered PAA Data for BI Canvas
 */
async function fetchFilteredPAA(filters = {}) {
    let url = `${SUPABASE_URL}/rest/v1/paa_master?select=*`;
    
    if (filters.year && filters.year !== 'todos') {
        url += `&ano=eq.${filters.year}`;
    }
    if (filters.territory && filters.territory !== 'todos') {
        url += `&territorio=eq.${encodeURIComponent(filters.territory)}`;
    }
    
    url += `&limit=40000`;

    try {
        const response = await fetch(url, { headers });
        return await response.json();
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
    
    async exportPAA(filters = {}) {
        const data = await this.fetchFilteredPAA(filters);
        const csv = "Ano;Municipio;Territorio;Valor_Pago;Agricultores;Mulheres\n" + 
            data.map(d => `${d.ano};${d.municipio};${d.territorio};${d.valor_pago};${d.agricultores};${d.mulheres}`).join("\n");
        
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `paa_master_rn_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
    }
};

