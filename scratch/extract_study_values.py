import pypdf
import re
import pandas as pd

def extract_study_data():
    pdf_path = 'docs/Estudo PAA_nova versão_mar 2019_Final.pdf'
    data_points = []
    
    with open(pdf_path, 'rb') as f:
        reader = pypdf.PdfReader(f)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            
            # Procurar por padrões de execução anual no Ceará
            # Exemplo: "Em 2016, no Ceará, foram aplicados R$ ..."
            if "Ceará" in text and "PAA" in text:
                # Tentar capturar anos e valores próximos
                matches = re.findall(r'(201\d).*?(R\$\s?[\d,\.]+)', text, re.DOTALL)
                for year, val in matches:
                    data_points.append({"Ano": year, "Valor_Estudo": val, "Pagina": i+1})

    df_study = pd.DataFrame(data_points).drop_duplicates()
    print("\nVALORES ENCONTRADOS NO ESTUDO (CEARÁ):")
    print(df_study)
    return df_study

if __name__ == "__main__":
    extract_study_data()
