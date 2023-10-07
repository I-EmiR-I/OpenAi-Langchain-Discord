from PyPDF2 import PdfReader, PdfWriter
import time

#Put your own path in this script :)

def combine_pdfs(pdf_file1, pdf_file2, output_file):
    pdf1 = PdfReader(pdf_file1)
    pdf2 = PdfReader(pdf_file2)
    output_pdf = PdfWriter()

    # Add content from the first PDF
    for page in pdf1.pages:
        output_pdf.add_page(page)

    # Add content from the second PDF
    for page in pdf2.pages:
        output_pdf.add_page(page)

    # Append a timestamp to the output file name to avoid conflicts
    timestamp = time.strftime('%Y%m%d%H%M%S')
    unique_output_file = f"{output_file.split('.pdf')[0]}_{timestamp}.pdf"

    # Save the combined PDF to the unique output file
    with open(unique_output_file, 'wb') as f:
        output_pdf.write(f)
        setDB(f"BaseDeDatos_{timestamp}.pdf")

def getDB():
    with open(r'C:\Users\javie\OneDrive\Escritorio\OpenAi\ruta_temporal\db.txt', 'r') as file:
        first_line = file.readline().strip()  # Read the first line and remove leading/trailing whitespace
    print('funciono correctamente')
    return first_line

def setDB(db):
    with open(r'C:\Users\javie\OneDrive\Escritorio\OpenAi\ruta_temporal\db.txt', 'w') as file:
        file.write(db)
print(getDB())
