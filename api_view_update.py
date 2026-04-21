"""
Updating api.js to use the territorial aggregation view.
"""
import os

API_PATH = 'src/app/api.js'
with open(API_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Update fetchPaaByTerritory
new_api_logic = """
    async fetchPaaByTerritory() {
        // Now using the centralized database view for precise aggregation
        const { data } = await supabase.from('view_paa_territorios')
            .select('*')
            .eq('ano', 2024)
            .order('total_beneficiados', { ascending: false });
        
        return (data || []).map(d => ({
            nome: d.nome_territorio,
            valor: d.total_beneficiados
        }));
    },
"""

# Find and replace the old function block
content = content.replace('async fetchPaaByTerritory() {', '/* OLD */ async _fetchPaaByTerritoryOld() {')
# Append the new one inside the window.API object
content = content.replace('window.API = {', 'window.API = {\n' + new_api_logic)

with open(API_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("api.js updated to use view_paa_territorios.")
