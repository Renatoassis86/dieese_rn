/**
 * API Integration: Supabase Connection for the Rural Observatory
 * Optimized with RPC for large datasets (343k+ rows).
 */

const SUPABASE_URL = "https://kyzcdpcmgiisllxmnhqn.supabase.co";
const SUPABASE_KEY = "sb_publishable_DRWOVTb1-KWvTd35C_E18A_-L9RQtUJ";

const headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": `Bearer ${SUPABASE_KEY}`,
    "Content-Type": "application/json"
};

(function() {
    /**
     * Generic Query
     */
    async function query(table, filters = {}) {
        let url = `${SUPABASE_URL}/rest/v1/${table}?select=*`;
        Object.entries(filters).forEach(([key, val]) => {
            if (val && val !== 'todos') url += `&${key}=eq.${encodeURIComponent(val)}`;
        });
        url += `&limit=10000`; // Safety limit
        
        try {
            const res = await fetch(url, { headers: { ...headers } });
            return await res.json();
        } catch (e) {
            console.error(`Error querying ${table}:`, e);
            return [];
        }
    }

    /**
     * Fetch PAA annual stats using RPC
     */
    async function fetchPaaAnnual() {
        const url = `${SUPABASE_URL}/rest/v1/rpc/get_paa_stats_annual`;
        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({ uf_filter: "RN" })
            });
            const data = await res.json();
            return data.map(d => ({
                ano: d.ano,
                valor: parseFloat(d.total_pago) / 1000000,
                pactuado: parseFloat(d.total_pactuado) / 1000000,
                agricultores: parseInt(d.total_agricultores),
                mulheres: parseInt(d.total_mulheres),
                perc_mulheres: d.total_agricultores > 0 ? (parseInt(d.total_mulheres) / parseInt(d.total_agricultores)) * 100 : 0,
                total_kg: parseFloat(d.total_kg || 0),
                total_litros: parseFloat(d.total_litros || 0)
            }));
        } catch (e) {
            console.error("RPC Annual error:", e);
            return [];
        }
    }

    /**
     * Fetch PAA stats by territory using RPC
     */
    async function fetchPaaByTerritory(year = 2024) {
        const url = `${SUPABASE_URL}/rest/v1/rpc/get_paa_stats_by_territory`;
        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({ uf_filter: "RN", year_filter: parseInt(year) })
            });
            const data = await res.json();
            return data.map(d => ({
                nome: d.territorio || "Não Informado",
                valor: parseInt(d.total_agricultores),
                pago: parseFloat(d.total_pago)
            }));
        } catch (e) {
            console.error("RPC Territory error:", e);
            return [];
        }
    }

    /**
     * Fetch Filtered PAA for BI
     */
    async function fetchFilteredPAA(filters = {}) {
        return await query("paa_master", filters);
    }

    /**
     * Fetch PNAD indicators
     */
    async function fetchPnadIndicadores() {
        const url = `${SUPABASE_URL}/rest/v1/pnad_indicators?order=ano.asc&local=eq.Rio Grande do Norte`;
        const urlNE = `${SUPABASE_URL}/rest/v1/pnad_indicators?order=ano.asc&local=eq.Nordeste`;
        // Wait, the table I created was pnad_indicadores (with e). Fix consistency.
        const url_real = `${SUPABASE_URL}/rest/v1/pnad_indicadores?order=ano.asc&local=eq.Rio Grande do Norte`;
        const urlNE_real = `${SUPABASE_URL}/rest/v1/pnad_indicadores?order=ano.asc&local=eq.Nordeste`;
        
        try {
            const [resRN, resNE] = await Promise.all([
                fetch(url_real, { headers: { ...headers } }),
                fetch(urlNE_real, { headers: { ...headers } })
            ]);
            return {
                rn: await resRN.json(),
                ne: await resNE.json()
            };
        } catch (e) {
            console.error("PNAD Fetch error:", e);
            return null;
        }
    }

    /**
     * Export PAA to CSV
     */
    async function exportPAA(filters = {}) {
        let data = await fetchFilteredPAA(filters);
        if (!data || data.length === 0) return;
        
        const headerRow = Object.keys(data[0]);
        const csvContent = "data:text/csv;charset=utf-8," 
            + headerRow.join(";") + "\n"
            + data.map(e => Object.values(e).join(";")).join("\n");

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `paa_export_${new Date().getTime()}.csv`);
        document.body.appendChild(link);
        link.click();
    }

    /**
     * Fetch Agro indicators
     */
    async function fetchAgroIndicadores() {
        const url = `${SUPABASE_URL}/rest/v1/agro_indicadores?order=municipio.asc`;
        try {
            const res = await fetch(url, { headers: { ...headers } });
            return await res.json();
        } catch (e) {
            console.error("Agro Fetch error:", e);
            return [];
        }
    }

    /**
     * Fetch EES (EcoSol) data - Placeholder until table is confirmed
     */
    async function fetchEesData() {
        // Mocking for now as table cadsol is not yet confirmed
        return [
            { tipo: 'Associações', valor: 72 },
            { tipo: 'Cooperativas', valor: 18 },
            { tipo: 'Grupos Informais', valor: 8 },
            { tipo: 'Sociedades', valor: 2 }
        ];
    }

    /**
     * Fetch All Indicators for a specific dimension/territory
     */
    async function fetchDimensionData(dimension, territory = 'todos', year = 'todos') {
        let table = "paa_master";
        if (dimension === 'agro' || dimension === 'producao') table = "agro_indicadores";
        if (dimension === 'social') table = "pnad_indicadores";
        
        let url = `${SUPABASE_URL}/rest/v1/${table}?select=*`;
        
        if (territory && territory !== 'todos') {
            const field = (table === 'paa_master') ? 'territorio' : 'municipio'; 
            url += `&${field}=ilike.*${encodeURIComponent(territory)}*`;
        }
        
        if (year && year !== 'todos') {
            url += `&ano=eq.${year}`;
        }

        try {
            const res = await fetch(url, { headers: { ...headers } });
            return await res.json();
        } catch (e) {
            console.error(`Error fetching dimension ${dimension}:`, e);
            return [];
        }
    }

    // ══════════════════════════════════════════════
// API & GLOBAL CONFIG - OBSERVATÓRIO RURAL RN
// ══════════════════════════════════════════════

// Global Chart.js Defaults for Mobile & Premium UX
if (typeof Chart !== 'undefined') {
    Chart.defaults.responsive = true;
    Chart.defaults.maintainAspectRatio = false;
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.plugins.legend.position = window.innerWidth < 768 ? 'bottom' : 'right';
    Chart.defaults.font.family = "'Open Sans', sans-serif";
}

window.API = {
        query,
        fetchPaaAnnual,
        fetchPaaByTerritory,
        fetchFilteredPAA,
        fetchPnadIndicadores,
        fetchAgroIndicadores,
        fetchEesData,
        fetchDimensionData,
        exportPAA
    };
})();
