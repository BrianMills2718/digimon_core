#!/usr/bin/env python3
"""Create climate report PDF"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import textwrap

# Read text
with open("climate_report.txt", 'r') as f:
    text = f.read()

# Create PDF
c = canvas.Canvas("climate_report.pdf", pagesize=letter)
width, height = letter

# Title
c.setFont("Helvetica-Bold", 16)
c.drawString(inch, height - inch, "Climate Change and Renewable Energy Report")

# Body text
c.setFont("Helvetica", 11)
y = height - 1.5*inch

for paragraph in text.split('\n\n')[1:]:  # Skip title
    lines = textwrap.wrap(paragraph, width=85)
    for line in lines:
        if y < inch:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height - inch
        c.drawString(inch, y, line)
        y -= 14
    y -= 7  # Extra space between paragraphs

c.save()
print("Created climate_report.pdf")