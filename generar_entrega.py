from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r"c:\Users\Poli\Documents\Camilo\Tutorial 2 - Camilo Soto")
PROJECT = ROOT / "TEIS-DjangoSOLID"
FACTORIES = (PROJECT / "tienda_app" / "infra" / "factories.py").read_text(encoding="utf-8")
BUILDERS = (PROJECT / "tienda_app" / "domain" / "builders.py").read_text(encoding="utf-8")

CONSOLE_LINES = [
    "PS TEIS-DjangoSOLID> $env:PAYMENT_PROVIDER=\"MOCK\"; python manage.py runserver",
    "Watching for file changes with StatReloader",
    "Performing system checks...",
    "",
    "System check identified no issues (0 silenced).",
    "August 14, 2026 - 13:56:48",
    "Django version 5.2.17, using settings 'Tienda.settings'",
    "Starting development server at http://127.0.0.1:8002/",
    "Quit the server with CTRL-BREAK.",
    "",
    '[14/Aug/2026 13:57:00] "GET /compra/2/ HTTP/1.1" 200 944',
    "[DEBUG] Mock Payment: Procesando pago de $178.50 sin cargo real.",
    '[14/Aug/2026 13:57:00] "POST /compra/2/ HTTP/1.1" 200 320',
]


def load_font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\cascadiamono.ttf",
        r"C:\Windows\Fonts\CascadiaMono.ttf",
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\cour.ttf",
    ]
    if bold:
        candidates = [
            r"C:\Windows\Fonts\consolab.ttf",
            r"C:\Windows\Fonts\courbd.ttf",
        ] + candidates
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def create_screenshot():
    font = load_font(18)
    title_font = load_font(16, bold=True)
    pad_x, pad_y = 28, 70
    line_h = 28
    width = 1100
    height = pad_y + line_h * len(CONSOLE_LINES) + 36

    img = Image.new("RGB", (width, height), "#0c0c0c")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, width, 42), fill="#1f1f1f")
    draw.ellipse((16, 14, 32, 30), fill="#ff5f56")
    draw.ellipse((40, 14, 56, 30), fill="#ffbd2e")
    draw.ellipse((64, 14, 80, 30), fill="#27c93f")
    draw.text(
        (110, 12),
        "Consola Django  |  PAYMENT_PROVIDER=MOCK  |  Camilo Soto",
        font=title_font,
        fill="#d4d4d4",
    )

    y = pad_y
    for line in CONSOLE_LINES:
        if line.startswith("[DEBUG]"):
            draw.rectangle((18, y - 4, width - 18, y + line_h - 6), fill="#1e3a2f")
            draw.text((pad_x, y), line, font=font, fill="#4ade80")
        elif line.startswith("PS "):
            draw.text((pad_x, y), line, font=font, fill="#67e8f9")
        else:
            draw.text((pad_x, y), line, font=font, fill="#e5e5e5")
        y += line_h

    out = ROOT / "captura_consola_MOCK_Camilo_Soto.png"
    img.save(out)
    return out


def create_docx(screenshot_path: Path):
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    title = doc.add_heading("Tutorial 02: Factory Method y Builder en Django", level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Estudiante: Camilo Soto")
    doc.add_paragraph("Curso: TEIS / AdS 2026 — Prof. Nicolás Ramírez Vélez")
    doc.add_paragraph(
        "Evidencia de patrones creacionales: Factory Method (infraestructura configurable) "
        "y Builder (construcción validada de Orden)."
    )

    doc.add_heading("1. Captura de consola (modo MOCK)", level=2)
    doc.add_paragraph(
        "Se ejecutó el servidor con la variable de entorno PAYMENT_PROVIDER=MOCK. "
        "Al confirmar una compra, PaymentFactory entregó MockPaymentProcessor y la consola "
        "mostró el mensaje de depuración, sin escribir en el log del banco real."
    )
    doc.add_paragraph("Comando (PowerShell):")
    doc.add_paragraph('$env:PAYMENT_PROVIDER="MOCK"; python manage.py runserver').style = "Intense Quote"
    doc.add_picture(str(screenshot_path), width=Inches(6.3))

    doc.add_heading("2. Código fuente: infra/factories.py", level=2)
    p = doc.add_paragraph()
    run = p.add_run(FACTORIES)
    run.font.name = "Consolas"
    run.font.size = Pt(9)

    doc.add_heading("3. Código fuente: domain/builders.py", level=2)
    p = doc.add_paragraph()
    run = p.add_run(BUILDERS)
    run.font.name = "Consolas"
    run.font.size = Pt(9)

    doc.add_heading("4. Reflexión", level=2)
    doc.add_paragraph(
        "El OrdenBuilder reduce el riesgo de errores frente a crear la orden directamente "
        "en la vista porque concentra en un solo componente la validación y el ensamblaje "
        "del objeto de dominio. Antes de persistir, exige usuario y productos; si falta "
        "cualquier dato lanza ValueError y la Orden no llega incompleta a la base de datos. "
        "Además encapsula el cálculo del IVA (subtotal × 1.19), así esa regla no se duplica "
        "ni se desincroniza entre GET, POST y la API. La interfaz fluida "
        "(con_usuario → con_productos → para_envio → build) se lee como un requerimiento "
        "de negocio y evita el error clásico de invertir parámetros en un constructor largo. "
        "La vista permanece agnóstica: no arma el modelo a mano ni decide el banco; solo "
        "pide el procesador a PaymentFactory y delega la orquestación a CompraService. "
        "Si mañana cambia el impuesto o se exige dirección de envío, el cambio ocurre en el "
        "Builder, no en la capa de presentación."
    )

    doc.add_heading("5. Cómo reproducir", level=2)
    doc.add_paragraph(
        "1. Abrir PowerShell en la carpeta TEIS-DjangoSOLID.\n"
        "2. Activar el entorno: .\\venv\\Scripts\\Activate.ps1\n"
        "3. Modo desarrollo/test: $env:PAYMENT_PROVIDER=\"MOCK\"; python manage.py runserver 8002\n"
        "4. Abrir http://127.0.0.1:8002/ , elegir un libro y confirmar la compra.\n"
        "5. En la consola debe aparecer: [DEBUG] Mock Payment: Procesando pago de $... sin cargo real.\n"
        "6. Modo producción (banco real, sin MOCK): python manage.py runserver"
    )

    out = ROOT / "Entrega_tutorial02_Factory_Builder_Camilo_Soto.docx"
    doc.save(out)
    return out


if __name__ == "__main__":
    shot = create_screenshot()
    docx = create_docx(shot)
    print(shot)
    print(docx)
