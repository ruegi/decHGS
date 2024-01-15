""" 
stripPsw.py
zeigt die pdf-Dateien des Ordneres my_path, die mit Passwort verschlüsselt sind.
Wenn eine derartige Datei selektiert ist und der Button 'pdf entschlüsseln' dedrückt wird,
wird die pdf in eine neue OHNE Paswort kopiert.
Wird die Check-Box 'pdf nach Öffnen löschen' aktiviert,
so wird die Passwort geschützte pdf gelöscht.
Die App zeigt anschließend in ihrem Fenster den Inhalt der ersten Seite der pdf an.
rg, 2024-01-15
"""

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.utils import platform
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen

import os
from pypdf import PdfReader, PdfWriter
import pypdfium2 as pdfium

# Konstanten
my_psw = "hgsruesweg1923"
my_prefix = "decrypt_"
my_path = "E:\\Daten\\Dülmen\\HGS\\HGS Rechnungen"


class MyLayout(Screen):
    def __init__(self, *args, **kwargs):
        super(MyLayout, self).__init__(*args, **kwargs)
        Window.size = (960, 960)
        Window.top = 40
        self.pdf = ""
        self.bild = ""
        self.ids.filechooser.path = my_path

    def selected(self, filename):
        self.pdf = filename[0]

    def decrypt(self):
        inFile = self.pdf
        inFilePath, inFileBase = os.path.split(inFile)
        input_name, input_ext = os.path.splitext(inFileBase)
        output_file_name = my_prefix + inFileBase
        outFile = os.path.join(inFilePath, output_file_name)
        if decrypt_pdf(inFile, outFile):
            _, self.bild = pdf2bild(outFile)
            self.ids.image.source = self.bild
            if self.ids.delSource.active:
                try:
                    os.remove(inFile)
                except:
                    pass
        else:
            pass

    def removeBild(self):
        if os.path.exists(self.bild):
            os.remove(self.bild)

    def dir_filter(self, dir, eintrag):
        return isProtected(os.path.join(dir, eintrag))


class stripPswApp(App):
    def build(self):
        return MyLayout()


def isProtected(pdf: str) -> bool:
    try:
        if PdfReader(pdf).is_encrypted:
            return True
        else:
            return False
    except:
        return False


def pdf2bild(pdfDatei):
    qordner, qname = os.path.split(pdfDatei)
    purename, qext = os.path.splitext(qname)
    outname = os.path.join(qordner, purename)

    if not os.path.exists(pdfDatei):
        return 0
    anzSeiten = 0
    pdf = pdfium.PdfDocument(
        pdfDatei,
    )

    ausgabe = ""
    for i in range(len(pdf)):
        page = pdf[i]
        image = page.render(scale=4).to_pil()
        ausgabe = f"{outname}_{(i+1):2d}.jpg"
        image.save(ausgabe)
        anzSeiten += 1
        break  # nur 1. Seite
    return (anzSeiten, ausgabe)


def decrypt_pdf(in_pdf: str, out_pdf: str) -> bool:
    erg = True
    try:
        reader = PdfReader(in_pdf, "rb")
        reader.decrypt(my_psw)
        output_PDF = PdfWriter()
        output_PDF.append_pages_from_reader(reader)
        with open(out_pdf, "wb") as f:
            output_PDF.write(f)
    except:
        erg = False
    return erg


if __name__ == "__main__":
    app = stripPswApp()
    app.run()
