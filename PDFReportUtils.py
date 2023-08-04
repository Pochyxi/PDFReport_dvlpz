import json

from fpdf import FPDF, XPos, YPos
from PIL import Image, ImageOps, ImageDraw
import numpy as np
import os


def make_circle(self, image_path):
    img = Image.open(image_path).convert("RGBA")

    # Create same size alpha layer with circle
    alpha = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(alpha)
    draw.pieslice([0, 0, img.size[0], img.size[1]], 0, 360, fill=255)

    # Convert alpha Image to numpy array
    npAlpha = np.array(alpha)

    # Add alpha layer to RGB
    npImage = np.array(img)
    npImage[..., 3] = npAlpha

    path_img_circle = image_path.split("/")[0] + "/" + image_path.split("/")[1] + "/"
    img_name = image_path.split("/")[2].split(".")[0]
    final_path = path_img_circle + img_name + '_circle.png'

    if os.path.isfile(final_path):
        print("File already exists")
        return final_path
    else:
        print("File does not exist")
        final = Image.fromarray(npImage)
        final.save(final_path)
        return final_path

class PDF(FPDF):
    def __init__(self, orientation, unit, format, test_id):
        super().__init__(orientation, unit, format)
        self.test_id = test_id

    def header(self):
        # Seleziona font Helvetica bold 15
        self.set_font('Helvetica', 'B', 15)
        # Calcola la larghezza della pagina
        w = self.w
        # Sposta il cursore all'inizio della pagina
        self.set_xy(0, 0)
        # Colori del frame, del background e del testo
        self.set_draw_color(0, 0, 0)  # colori in RGB (neri, non visibili)
        self.set_fill_color(26, 38, 65)  # blu notte in RGB
        self.set_text_color(255, 255, 255)  # bianco
        # Spessore del frame (0 mm, non visibile)
        self.set_line_width(0)
        # Rettangolo pieno che copre tutta la larghezza della pagina (altezza 20 mm)
        self.cell(w, 20, '', 0, 0, fill=True)
        # Calcola la larghezza del titolo e posiziona il cursore al centro della pagina
        title_w = self.get_string_width(self.test_id) + 6
        self.set_xy((w - title_w) / 2, 5)  # 5 mm dal bordo superiore della pagina
        # Titolo (senza bordo e senza riempimento)
        self.cell(title_w, 10, self.test_id, 0, 0, 'C')
        # Line break
        self.ln(20)  # Sposta il cursore 20 mm sotto, pronti per il corpo della pagina

    def cover_page(self, title, logo_path_1, logo_path_2, company_name, client_name, date, app_version, author,
                   contact):
        self.set_font('Helvetica', 'B', 24)
        self.image(logo_path_1, x=10, y=10, w=50)
        self.image(logo_path_2, x=150, y=10, w=50)

        self.set_y(100)
        self.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

        self.set_font('Helvetica', '', 12)
        self.cell(0, 20, f"Company: {company_name}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.cell(0, 20, f"Client: {client_name}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.cell(0, 20, f"Date: {date}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.cell(0, 20, f"App Version: {app_version}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.cell(0, 20, f"Author: {author}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.cell(0, 20, f"Contact: {contact}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

    def footer(self):
        # Set position of the footer
        self.set_y(-15)
        # set font
        self.set_font('helvetica', 'I', 8)
        # Set font color grey
        self.set_text_color(26, 38, 65)  # blu notte in RGB
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}', align='C')


# Usa la classe
pdf = PDF('P', 'mm', 'Letter', 'POC_01')

print(make_circle("./media/TimVisionAppLogo.png"))

# Aggiungi la pagina di copertina
pdf.add_page()

title = 'Report di Testing'
logo_path_1 = make_circle('./media/NetcomGroupLogo.jpeg')
logo_path_2 = make_circle('./media/TimVisionAppLogo.png')
company_name = 'Testing Company'
client_name = 'Client Company'
date = '01/01/2023'
app_version = '1.0.0'
author = 'Test Author'
contact = 'test@email.com'
pdf.cover_page(title, logo_path_1, logo_path_2, company_name, client_name, date, app_version, author, contact)

# specifica la path del file JSON
json_file_path = './report.json'

# apri e leggi il file JSON
with open(json_file_path, 'r') as f:
    data = json.load(f)

# per ogni coppia di immagini nell'array di immagini
for (img1, img2) in zip(data['imgs'][::2], data['imgs'][1::2]):

    couple_obj = {
        "img1": img1,
        "img2": img2
    }

    # aggiungi una nuova pagina
    pdf.add_page()

    def draw_image(write=True, value=None):
        if os.path.isfile(value['path']):
            # inserisci la prima immagine nel PDF
            image = Image.open(value['path'])
            width, height = image.size
            aspect_ratio = width / height

            # calcola le dimensioni dell'immagine per il PDF
            pdf_width = 160  # la larghezza della pagina A4 è 210mm, lasciando 10mm per i margini
            pdf_height = pdf_width / aspect_ratio

            if write:
                pdf.image(value['path'], x='C', y=pdf.get_y(), w=pdf_width, h=pdf_height)

            return pdf_height


    count_lap = 0
    for key, value in couple_obj.items():
        count_lap += 1

        if count_lap == 2:
            pdf.ln(draw_image(write=False, value=value) + 10)

        if count_lap == 1:
            pdf.set_font('Helvetica', '', 12)

        pdf.cell(0, 10, f"Descrizione: {value['name']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

        draw_image(write=True, value=value)

# output del PDF
pdf.output('test_report.pdf')
