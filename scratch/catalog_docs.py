import pypdf
import os
import re

def catalog_paa_studies():
    docs_dir = 'docs'
    pdf_files = [
        'Estudo PAA_nova versão_mar 2019_Final.pdf',
        'Estudo temático - Superação da pobreza e inclusão produtiva no Ceará_final.pdf'
    ]
    
    catalog = {}

    for pdf_name in pdf_files:
        path = os.path.join(docs_dir, pdf_name)
        if not os.path.exists(path):
            continue
            
        print(f"Analisando: {pdf_name}")
        with open(path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text()
            
            # Buscar padrões de valores (R$ X milhões) e anos
            finds = re.findall(r'(R\$\s?[\d,\.]+\s?(?:milhões|mi|mil))', full_text, re.IGNORECASE)
            years = re.findall(r'(201\d|202\d)', full_text)
            
            catalog[pdf_name] = {
                "values": list(set(finds))[:10], # Primeiros 10 valores achados
                "years_referenced": list(set(years))
            }
            
            # Busca específica para Ceará e PAA
            if "Ceará" in full_text and "PAA" in full_text:
                print(f"  -> Contém referências diretas ao PAA no Ceará.")

    print("\n--- CATÁLOGO DE ESTUDOS ---")
    for doc, info in catalog.items():
        print(f"\nDocumento: {doc}")
        print(f"Anos citados: {sorted(info['years_referenced'])}")
        print(f"Valores monetários encontrados (amostra): {info['values']}")

if __name__ == "__main__":
    catalog_paa_studies()
