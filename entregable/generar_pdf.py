"""Genera la plantilla de evidencia, sin atribuir resultados no verificados."""
import argparse
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Flowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialBold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFont(TTFont('Consolas', 'C:/Windows/Fonts/consola.ttf'))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='ArialBold', italic='Arial', boldItalic='ArialBold')


class Captura(Flowable):
    def __init__(self, label, height):
        super().__init__()
        self.width = 499
        self.height = height
        self.label = label

    def draw(self):
        c = self.canv
        c.setFillColor(colors.HexColor('#f5f8fc'))
        c.setStrokeColor(colors.HexColor('#a8b7ca'))
        c.roundRect(0, 0, self.width, self.height, 8, fill=1, stroke=1)
        p = Paragraph(escape(self.label), styles['Marker'])
        _, h = p.wrap(self.width - 32, self.height - 24)
        p.drawOn(c, 16, (self.height - h) / 2)


parser = argparse.ArgumentParser()
parser.add_argument('--integrantes', default='[NOMBRE 1, NOMBRE 2, ...]')
parser.add_argument('--subdominio', default='SUBDOMINIO')
args = parser.parse_args()
styles = getSampleStyleSheet()
styles.add(ParagraphStyle('TitleCustom', fontName='ArialBold', fontSize=25,
                          leading=30, textColor=colors.HexColor('#15334b'), spaceAfter=18))
styles.add(ParagraphStyle('SectionCustom', fontName='ArialBold', fontSize=14,
                          leading=19, textColor=colors.HexColor('#15334b'), spaceAfter=10))
styles.add(ParagraphStyle('BodyCustom', fontName='Arial', fontSize=10,
                          leading=15, spaceAfter=10))
styles.add(ParagraphStyle('Marker', fontName='ArialBold', fontSize=11,
                          leading=16, alignment=1, textColor=colors.HexColor('#4a6178')))
styles.add(ParagraphStyle('CodeCustom', fontName='Consolas', fontSize=9, leading=15,
                          spaceAfter=10))


def para(text, style='BodyCustom'):
    return Paragraph(text, styles[style])


def footer(canvas, doc):
    canvas.setStrokeColor(colors.HexColor('#dce4ed'))
    canvas.line(48, 45, 547, 45)
    canvas.setFont('Arial', 8)
    canvas.setFillColor(colors.HexColor('#53687c'))
    canvas.drawString(48, 31, 'Equipo 01 | Cloudflare Workers | Evidencias por completar')
    canvas.drawRightString(547, 31, f'{doc.page} / 3')


staging = f'https://api-equipo-01-staging.{args.subdominio}.workers.dev'
production = f'https://api-equipo-01.{args.subdominio}.workers.dev'
story = [
    para('PRÁCTICA 1', 'SectionCustom'),
    para('Liberación y despliegue<br/>continuo con<br/>Cloudflare Workers', 'TitleCustom'),
    para('<b>Equipo:</b> 01 &nbsp;&nbsp; <b>Worker:</b> api-equipo-01'),
    para('<b>Integrantes:</b> ' + escape(args.integrantes)),
    para('a) Datos del equipo y b) URLs', 'SectionCustom'),
    para('<b>Staging</b><br/>' + escape(staging)),
    para('<b>Producción</b><br/>' + escape(production)),
    para('Agregar <b>/health</b> a cada URL para consultar estado, ambiente y versión.'),
    Spacer(1, 14),
    para('Estado del documento', 'SectionCustom'),
    para('Plantilla de evidencia. Los marcadores deben sustituirse por capturas reales. '
         'Las URLs con SUBDOMINIO son plantillas y no representan despliegues verificados. '
         'Los integrantes están pendientes hasta recibir sus nombres.'),
    para('Flujo esperado', 'SectionCustom'),
    para('Push a main → pruebas con Node 22 → staging automático y smoke test → '
         'aprobación manual de production → despliegue de producción y smoke test.'),
    para('La aprobación requiere configurar Required reviewers en el environment production '
         'de un repositorio público. El pipeline y los despliegues quedan pendientes de ejecución.'),
    PageBreak(),
    para('c) Pipeline y d) aprobación', 'TitleCustom'),
    para('Capturar una ejecución completa con pruebas, staging y producción exitosos. '
         'La aprobación debe capturarse cuando production espere la revisión, antes de aprobar.'),
    Captura('[PEGAR CAPTURA: pipeline completo en verde]', 238),
    Spacer(1, 18),
    Captura('[PEGAR CAPTURA: aprobación del despliegue a producción - Review deployments]', 238),
    Spacer(1, 14),
    para('Evidencia pendiente. No se han atribuido resultados a GitHub Actions.'),
    PageBreak(),
    para('e) Versión y rollback', 'TitleCustom'),
    para('Tras el pipeline de la segunda versión y su aprobación, abrir /health de producción. '
         'Capturar 1.1.0 antes de ejecutar el rollback.'),
    Captura('[PEGAR CAPTURA: /health de producción con versión 1.1.0]', 205),
    Spacer(1, 16),
    para('Ejecutar en producción y confirmar el destino 1.0.0:', 'BodyCustom'),
    para('npx wrangler rollback<br/>npx wrangler deployments list', 'CodeCustom'),
    Captura('[PEGAR CAPTURA: /health de producción tras el rollback con versión 1.0.0]', 205),
    Spacer(1, 14),
    para('Comprobar estado "ok", ambiente "produccion" y versión "1.0.0" en la respuesta real. '
         'El rollback remoto no cambia VERSION en el repositorio.'),
]
output = Path(__file__).with_name('Practica1.pdf')
doc = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=48, leftMargin=48,
                        topMargin=48, bottomMargin=62,
                        title='Práctica 1 - Cloudflare Workers - Equipo 01',
                        author='Equipo 01')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(output)
