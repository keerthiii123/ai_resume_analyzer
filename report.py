from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def create_pdf(text):

    doc=SimpleDocTemplate("resume_report.pdf")

    styles=getSampleStyleSheet()

    story=[Paragraph(line,styles["BodyText"]) for line in text.split("\n")]

    doc.build(story)

    return "resume_report.pdf"