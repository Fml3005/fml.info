import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
import re
import os

def split_pdf_by_empenho(pdf_path, output_folder):
    # Criar pasta de saída se não existir
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Abrir o PDF com pdfplumber para extrair texto
    with pdfplumber.open(pdf_path) as pdf:
        # Abrir o PDF com PyPDF2 para manipular páginas
        pdf_reader = PdfReader(pdf_path)
        
        current_pages = []  # Páginas acumuladas para o arquivo atual
        last_empenho_number = None  # Número da última nota de empenho
        file_counter = {}  # Contador para evitar sobrescrição de arquivos com mesmo número
        
        print(f"Total de páginas no PDF: {len(pdf.pages)}")
        
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()  # Extrair texto da página
            if text:
                print(f"\nPágina {page_num + 1}:")
                print(f"Texto extraído: {text[:200]}...")  # Mostra os primeiros 200 caracteres
            else:
                print(f"\nPágina {page_num + 1}: Nenhum texto extraído!")
                current_pages.append(page_num)
                continue
            
            # Verificar se há "NOTA DE LIQUIDAÇÃO" ou "NOTA DE LIQUIDACAO" primeiro
            has_liquidacao = "NOTA DE LIQUIDAÇÃO" in text or "NOTA DE LIQ" in text
            if has_liquidacao:
                print(f"  -> 'NOTA DE LIQUIDAÇÃO' ou 'NOTA DE LIQUIDACAO' ou 'DANFE' encontrada, incluindo no intervalo atual.")
                current_pages.append(page_num)
                continue
            
            # Procurar "NOTA DE EMPENHO" com "Nº" ou "N" seguido de número
            match = re.search(r"NOTA DE EMPENHO\s*(Nº|N|N°|N0|Nu|N2|N9|Na|Ne|W|Ng)\s*(\d+)", text)
            if match:
                empenho_number = match.group(2)  # Capturar o número (grupo 2)
                print(f"  -> 'NOTA DE EMPENHO {empenho_number}' encontrada! Iniciando novo intervalo.")
                
                # Se já temos páginas acumuladas e um número anterior, salvar o arquivo
                if current_pages and last_empenho_number:
                    # Incrementar contador para o número de empenho
                    file_counter[last_empenho_number] = file_counter.get(last_empenho_number, 0) + 1
                    counter_suffix = f"_{file_counter[last_empenho_number]}" if file_counter[last_empenho_number] > 1 else ""
                    output_file = f"{output_folder}/NOTA_DE_EMPENHO_{last_empenho_number}{counter_suffix}.pdf"
                    
                    pdf_writer = PdfWriter()
                    for p in current_pages:
                        pdf_writer.add_page(pdf_reader.pages[p])
                    with open(output_file, "wb") as out:
                        pdf_writer.write(out)
                    print(f"Arquivo salvo: {output_file}")
                
                # Reiniciar para o novo intervalo com a página atual
                current_pages = [page_num]
                last_empenho_number = empenho_number
            else:
                print("  -> Nenhuma 'NOTA DE EMPENHO' válida encontrada.")
                current_pages.append(page_num)
        
        # Salvar o último conjunto de páginas
        if current_pages and last_empenho_number:
            file_counter[last_empenho_number] = file_counter.get(last_empenho_number, 0) + 1
            counter_suffix = f"_{file_counter[last_empenho_number]}" if file_counter[last_empenho_number] > 1 else ""
            output_file = f"{output_folder}/NOTA_DE_EMPENHO_{last_empenho_number}{counter_suffix}.pdf"
            
            pdf_writer = PdfWriter()
            for p in current_pages:
                pdf_writer.add_page(pdf_reader.pages[p])
            with open(output_file, "wb") as out:
                pdf_writer.write(out)
            print(f"Arquivo salvo: {output_file}")

# Exemplo de uso
pdf_path = r"D:\DIGITALIZAÇÕES\PAULINO NEVES\Nova pasta\EDUC-QSE-04_1.pdf"  # Caminho do PDF
output_folder = r"D:\DIGITALIZAÇÕES\PAULINO NEVES\Nova pasta"  # Caminho de saída
split_pdf_by_empenho(pdf_path, output_folder)