import pypdf
import os

def find_specific_values():
    target_pdf = 'docs/Estudo PAA_nova versão_mar 2019_Final.pdf'
    if not os.path.exists(target_pdf):
        return

    print(f"Buscando '12,7' e 'Ceará' no documento {target_pdf}...")
    with open(target_pdf, 'rb') as f:
        reader = pypdf.PdfReader(f)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if "12,7" in text or "Ceará" in text:
                # Se achar o valor, imprime o contexto (linhas ao redor)
                lines = text.split('\n')
                for line in lines:
                    if "12,7" in line or "PAA" in line:
                        print(f"[Pág {i+1}] {line}")

if __name__ == "__main__":
    find_specific_values()
