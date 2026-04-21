"""
Updating API.js to handle filtering logic for the new BI module.
"""
import os

API_PATH = 'src/app/api.js'

with open(API_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

new_logic = """
/**
 * Fetch Filtered PAA Data for BI Canvas
 */
async function fetchFilteredPAA(filters = {}) {
    let url = `${SUPABASE_URL}/rest/v1/paa_dados?sigla_uf=eq.RN`;
    
    if (filters.year && filters.year !== 'todos') {
        url += `&ano=eq.${filters.year}`;
    }
    
    // For territory, we need to handle the join logic in JS or fetch mapping
    try {
        const response = await fetch(url, { headers });
        let data = await response.json();
        
        // If searching by territory
        if (filters.territory && filters.territory !== 'todos') {
            const terrRes = await fetch(`${SUPABASE_URL}/rest/v1/territorios_rn?nome_territorio=eq.${filters.territory}`, { headers });
            const terrMapData = await terrRes.json();
            const allowedIds = terrMapData.map(t => t.cod_municipio_ibge);
            data = data.filter(d => allowedIds.includes(d.cod_municipio_ibge.toString()));
        }
        
        return data;
    } catch (e) {
        console.error("BI Filter error:", e);
        return [];
    }
}

window.API = { ...window.API, fetchFilteredPAA };
"""

with open(API_PATH, 'a', encoding='utf-8') as f:
    f.write(new_logic)

print("API logic updated with investigative filtering support.")
