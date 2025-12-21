from fpdf import FPDF
import os
import re

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Nexus Engineering Assistant Documentation', align='C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

def md_to_pdf(md_file, pdf_file):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    
    with open(md_file, 'r') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(5)
            continue
            
        # Headers
        if line.startswith('# '):
            pdf.set_font("helvetica", 'B', 20)
            pdf.cell(0, 10, line[2:], ln=True)
            pdf.set_font("helvetica", size=12)
        elif line.startswith('## '):
            pdf.set_font("helvetica", 'B', 16)
            pdf.cell(0, 10, line[3:], ln=True)
            pdf.set_font("helvetica", size=12)
        elif line.startswith('### '):
            pdf.set_font("helvetica", 'B', 14)
            pdf.cell(0, 10, line[4:], ln=True)
            pdf.set_font("helvetica", size=12)
        # List items
        elif line.startswith('- ') or line.startswith('* '):
            pdf.cell(10) # Indent
            pdf.multi_cell(0, 8, f"\u2022 {line[2:]}")
        # Code blocks (basic)
        elif line.startswith('```'):
            continue # Skip the markers
        else:
            # Normal text
            pdf.multi_cell(0, 8, line)

    pdf.output(pdf_file)
    print(f"Generated {pdf_file}")

if __name__ == "__main__":
    md_to_pdf("README.md", "README.pdf")
    md_to_pdf("docs/ARCHITECTURE.md", "docs/ARCHITECTURE.pdf")
