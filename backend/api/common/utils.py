import io

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.rl_config import defaultPageSize

PAGE_HEIGHT = defaultPageSize[1]
PAGE_WIDTH = defaultPageSize[0]
styles = getSampleStyleSheet()

TITLE = "Список ингредиентов для покупки"
PAGE_INFO = "Foodgram закупочка"

FONT_NAME = 'FreeSans'
pdfmetrics.registerFont(TTFont(FONT_NAME, 'FreeSans.ttf'))


def first_page(canvas, doc):
    canvas.setFont(FONT_NAME, 16)
    canvas.saveState()
    canvas.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT - 108, TITLE)
    canvas.setFont(FONT_NAME, 9)
    canvas.drawString(inch, 0.25 * inch, "Страница 1 / %s" % PAGE_INFO)
    canvas.restoreState()


def later_pages(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT_NAME, 9)
    canvas.drawString(
        inch, 0.25 * inch, "Страница %d / %s" % (doc.page, PAGE_INFO)
    )
    canvas.restoreState()


def generate_pdf_file(output_text_list):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer)
    story = [Spacer(1, inch)]
    style = styles["Normal"]
    style.fontName = FONT_NAME
    for text in output_text_list:
        p = Paragraph(text, style)
        story.append(p)
        story.append(Spacer(1, 0.05 * inch))

    doc.build(story, onFirstPage=first_page, onLaterPages=later_pages)

    buffer.seek(0)
    return buffer
