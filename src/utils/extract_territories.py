import pypdf
import re
import json
import os

def extract_territories(pdf_path, output_path):
    reader = pypdf.PdfReader(pdf_path)
    territories = {}
    current_terr = None
    
    # Regex for Territory header
    terr_pattern = re.compile(r"Território\s+–\s+([\w\s\-]+)", re.IGNORECASE)
    # Regex for Municipality entry (Number. Name SIM/NÃO)
    mun_pattern = re.compile(r"^\d+\.\s+([A-ZáéíóúçñÁÉÍÓÚÇÑ\s\-'.]+)", re.MULTILINE)

    for page in reader.pages:
        text = page.extract_text()
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Check for new territory
            terr_match = terr_pattern.search(line)
            if terr_match:
                current_terr = terr_match.group(1).strip()
                if current_terr not in territories:
                    territories[current_terr] = []
                continue
            
            # Check for municipality if we are inside a territory
            if current_terr:
                mun_match = mun_pattern.match(line)
                if mun_match:
                    # Clean up the name (remove "SIM", "NÃO", or extra spaces)
                    name = mun_match.group(1).strip()
                    # Remove "SIM" or "NÃO" if they leaked into the match
                    name = re.split(r"\s+(?:SIM|NÃO)", name, flags=re.IGNORECASE)[0]
                    territories[current_terr].append(name)

    # Save to JSON (Names only)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(territories, f, indent=2, ensure_ascii=False)
    
    # ENRICHMENT: Add IBGE IDs
    ibge_path = 'data/raw/municipios_rn.json'
    if os.path.exists(ibge_path):
        with open(ibge_path, 'r', encoding='utf-16') as f:
            muns_data = json.load(f)['value']
            name_to_id = {m['nome'].lower(): m['id'] for m in muns_data}
            
            enriched = {}
            for t, muns in territories.items():
                enriched[t] = []
                for m in muns:
                    # Special check for Campo Grande name mismatch mentioned in PDF
                    search_name = m.lower()
                    if "campo grande" in search_name or "augusto severo" in search_name:
                         search_name = "campo grande"
                    
                    m_id = name_to_id.get(search_name, "NÃO ENCONTRADO")
                    enriched[t].append({"nome": m, "id": m_id})
            
            enriched_path = output_path.replace('.json', '_ibge.json')
            with open(enriched_path, 'w', encoding='utf-8') as f:
                json.dump(enriched, f, indent=2, ensure_ascii=False)
            print(f"Dicionário enriquecido salvo em: {enriched_path}")

    print(f"Sucesso! {len(territories)} territórios mapeados.")
    for t, muns in territories.items():
        print(f"- {t}: {len(muns)} municípios")

if __name__ == "__main__":
    pdf = 'docs/Seminário Territorial da Política Pública do Trabalho - Triagem Formulário e Participação (1).pdf'
    output = 'data/reference/territorios_rn.json'
    extract_territories(pdf, output)
