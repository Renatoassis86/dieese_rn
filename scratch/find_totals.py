import pypdf
import re

def find_total_ceara():
    pdf_path = 'docs/Estudo PAA_nova versão_mar 2019_Final.pdf'
    
    with open(pdf_path, 'rb') as f:
        reader = pypdf.PdfReader(f)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            
            # Procurar por "Total" e "Ceará" e "R$" no mesmo bloco de texto
            if "Total" in text and "Ceará" in text and "R$" in text:
                print(f"\n--- Possível Tabela de Totais encontrada na Página {i+1} ---")
                # Pega as linhas ao redor do termo "Total"
                lines = text.split('\n')
                for line in lines:
                    if "Total" in line or "Ceará" in line or "201" in line:
                        print(line)

if __name__ == "__main__":
    find_total_ceara()
