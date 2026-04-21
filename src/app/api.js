/**
 * API Integration: Supabase Connection for the Rural Observatory
 * Fetches real-time data for the dashboards.
 */

const SUPABASE_URL = "https://kyzcdpcmgiisllxmnhqn.supabase.co";
const SUPABASE_KEY = "sb_publishable_DRWOVTb1-KWvTd35C_E18A_-L9RQtUJ"; // Anon/Publishable Key

const headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": `Bearer ${SUPABASE_KEY}`
};

/**
 * Fetch Aggregated PAA Data for the Line Chart
 */
async function fetchPaaAnnual() {
    // We group by year in the query or fetch and group in JS
    // For performance, we fetch sum grouped by ano from a view or just the raw data if small
    // Since it's only 10k rows, we can fetch an aggregate
    const url = `${SUPABASE_URL}/rest/v1/rpc/get_paa_annual_summary`;
    
    // Fallback: If RPC doesn't exist, we use a complex select
    const selectUrl = `${SUPABASE_URL}/rest/v1/paa_dados?select=ano,val_executado,qtd_beneficiados&sigla_uf=eq.RN`;
    
    try {
        const response = await fetch(selectUrl, { headers });
        const data = await response.json();
        
        // Group by year in JS
        const grouped = data.reduce((acc, curr) => {
            acc[curr.ano] = (acc[curr.ano] || 0) + parseFloat(curr.val_executado);
            return acc;
        }, {});
        
        return Object.entries(grouped)
            .sort((a,b) => a[0] - b[0])
            .map(([ano, val]) => ({ ano, valor: val / 1000000 })); // Convert to Millions
    } catch (e) {
        console.error("Error fetching annual PAA:", e);
        return [];
    }
}

/**
 * Fetch PAA by Territory for the Bar Chart
 */
async function fetchPaaByTerritory() {
    // Join paa_dados with territorios_rn
    // SELECT t.nome_territorio, SUM(p.qtd_beneficiados) ...
    // Since Supabase REST doesn't support complex joins well without views,
    // we fetch both and join in JS or create a view.
    
    try {
        const [paaRes, terrRes] = await Promise.all([
            fetch(`${SUPABASE_URL}/rest/v1/paa_dados?select=cod_municipio_ibge,qtd_beneficiados`, { headers }),
            fetch(`${SUPABASE_URL}/rest/v1/territorios_rn?select=cod_municipio_ibge,nome_territorio`, { headers })
        ]);
        
        const paa = await paaRes.json();
        const territories = await terrRes.json();
        
        const terrMap = territories.reduce((acc, curr) => {
            acc[curr.cod_municipio_ibge] = curr.nome_territorio;
            return acc;
        }, {});
        
        const summary = paa.reduce((acc, curr) => {
            const terr = terrMap[curr.cod_municipio_ibge] || "Outros";
            acc[terr] = (acc[terr] || 0) + parseInt(curr.qtd_beneficiados);
            return acc;
        }, {});
        
        return Object.entries(summary)
            .sort((a,b) => b[1] - a[1])
            .map(([nome, valor]) => ({ nome, valor }));
    } catch (e) {
        console.error("Error fetching territory PAA:", e);
        return [];
    }
}

window.API = { fetchPaaAnnual, fetchPaaByTerritory };
