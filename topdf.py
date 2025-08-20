from fpdf import FPDF
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# Obtener los datos de la tabla
response = supabase.table("registro").select("*").execute()
records = response.data

class kurobiPDF(FPDF):

    # formato membreatado
    def header(self):
        self.image('imgs/Formato_Membretado_ig.png', 0, 0, 210)

    # formato para header row
    def table_header(self):
        self.set_font("Arial", "B", 10)

        self.set_fill_color(230, 230, 230) # gris
        self.set_text_color(0, 0, 0)

        # Header content
        self.cell(20, 10, "ID", 1, 0, 'C', 1)
        self.cell(60, 10, "Empleado", 1, 0, 'C', 1)
        self.cell(40, 10, "Fecha/Hora Salida", 1, 0, 'C', 1)
        self.cell(70, 10, "Código de Barras", 1, 0, 'C', 1)
        self.ln()

    def table_data(self, records):
            # formato para data row
        self.set_font("Arial", "", 10)
        self.set_text_color(0, 0, 0)
        self.set_fill_color(255, 255, 255)

        # load data from supabase
        for record in records:
            self.cell(20, 10, str(record.get("id", "")), 1, 0, 'C', 1)
            self.cell(60, 10, record.get("empleado", ""), 1, 0, 'C', 1)
            self.cell(40, 10, str(record.get("tiempo_salida", ""))[:16], 1, 0, 'C', 1)  # Limitar longitud de fecha/hora
            self.cell(70, 10, record.get("barcode", ""), 1, 0, 'C', 1)
            self.ln()

pdf = kurobiPDF()
pdf.add_page()
pdf.set_font("Arial", "B", 16)

pdf.set_xy(20, 65)  # position below the header image
pdf.cell(0, 10, "Reporte de Registros", 0, 1, "C")
pdf.ln(10)

# Add table
pdf.table_header()

pdf.table_data(records)

# Guardar el PDF
pdf_path = "pdfRegistros/reporte_registros.pdf"
pdf.output(pdf_path)
print(f"PDF generado exitosamente: {pdf_path}")
