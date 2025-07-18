#!/usr/bin/env python3
"""Create a test PDF from text"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import textwrap

def create_pdf(text_file, pdf_file):
    """Create a PDF from a text file."""
    # Read text
    with open(text_file, 'r') as f:
        text = f.read()
    
    # Create PDF
    c = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter
    
    # Set font
    c.setFont("Helvetica", 12)
    
    # Write text
    y = height - inch
    for paragraph in text.split('\n\n'):
        lines = textwrap.wrap(paragraph, width=80)
        for line in lines:
            if y < inch:
                c.showPage()
                c.setFont("Helvetica", 12)
                y = height - inch
            c.drawString(inch, y, line)
            y -= 15
        y -= 10  # Extra space between paragraphs
    
    c.save()
    print(f"Created PDF: {pdf_file}")

if __name__ == "__main__":
    create_pdf("test_document.txt", "test_document.pdf")