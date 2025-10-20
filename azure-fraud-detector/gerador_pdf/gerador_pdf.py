from fpdf import FPDF

# --- INÍCIO DA CRIAÇÃO DO DOCUMENTO ---
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# --- CABEÇALHO ---
pdf.set_font("Arial", 'B', 16)
pdf.cell(200, 10, txt="Luz & Força do Rio S.A.", ln=1, align='C')
pdf.set_font("Arial", size=10)
pdf.cell(200, 5, txt="CNPJ: 01.234.567/0001-89", ln=1, align='C')
pdf.cell(200, 5, txt="Av. Rio Branco, 1 - Centro, Rio de Janeiro - RJ, 20090-003", ln=2, align='C')

pdf.ln(15) # Adiciona um espaço

# --- TÍTULO DO DOCUMENTO ---
pdf.set_font("Arial", 'B', 14)
pdf.cell(200, 10, txt="COMPROVANTE DE RESIDÊNCIA", ln=1, align='C')

pdf.ln(10) # Adiciona um espaço

# --- INFORMAÇÕES DO CLIENTE ---
pdf.set_font("Arial", size=12)
pdf.cell(40, 7, txt="Para:")
pdf.set_font("Arial", 'B', 12)
pdf.cell(100, 7, txt="CARLOS MAGNUS", ln=1)

pdf.set_font("Arial", size=12)
pdf.cell(40, 7, txt="Endereço:")
pdf.cell(100, 7, txt="Rua da Passagem, 999, Apto 101", ln=1)
pdf.cell(40, 7, txt="")
pdf.cell(100, 7, txt="Botafogo, Rio de Janeiro - RJ", ln=1)
pdf.cell(40, 7, txt="")
pdf.cell(100, 7, txt="CEP: 22290-030", ln=1)

pdf.ln(10)

# --- DETALHES DA CONTA ---
pdf.cell(40, 7, txt="Número do Cliente:")
pdf.cell(50, 7, txt="8765432-1", ln=1)

pdf.cell(40, 7, txt="Mês de Referência:")
pdf.cell(50, 7, txt="Setembro/2025", ln=1)

pdf.cell(40, 7, txt="Data de Emissão:")
pdf.cell(50, 7, txt="15/10/2025", ln=1)


pdf.ln(20)

# --- TEXTO DE VALIDAÇÃO E RODAPÉ ---
pdf.set_font("Arial", 'I', 10)
pdf.multi_cell(0, 5, txt="Este documento é uma representação da sua fatura de energia e é válido como comprovante de residência para fins cadastrais em todo o território nacional.")
pdf.ln(5)
pdf.multi_cell(0, 5, txt="Código de Validação: 9A8B7C6D-E5F4-G3H2-I1J0-K9L8M7N6P5O4")


# --- SALVAR O ARQUIVO ---
try:
    pdf.output("amostra.pdf")
    print("Arquivo 'amostra.pdf' criado com sucesso no mesmo diretório!")
except Exception as e:
    print(f"Ocorreu um erro ao criar o PDF: {e}")