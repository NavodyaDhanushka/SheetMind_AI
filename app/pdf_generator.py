from fpdf import FPDF
import os

def generate_pdf(username, content, output_dir):
    pdf = FPDF()
    pdf.add_page()

    font_path = os.path.join("app", "fonts", "DejaVuSans.ttf")

    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", size=12)

    pdf.multi_cell(0, 8, content)

    pdf_path = os.path.join(output_dir, f"{username}.pdf")
    pdf.output(pdf_path)

    return pdf_path
