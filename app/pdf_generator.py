from fpdf import FPDF
import os

def generate_pdf(filename, content, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f"{filename}.pdf")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, content)

    pdf.output(pdf_path)
    return pdf_path
