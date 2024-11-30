"""
tt.py 
Beispiel-Programm aus https://stackoverflow.com/questions/8568500/how-to-get-dropped-file-names-in-pyqt-pyside
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QApplication,
    QFileDialog,
    #    QHeaderView,
    QLabel,
)
from PyQt6.QtGui import QPixmap, QImage, QIcon
from PyQt6.QtCore import Qt

from frm_pdfdec import Ui_frm_pdfDec

import os
import sys
from pathlib import Path
import pikepdf
import pypdfium2

import pypdfium2_raw

from PIL.ImageQt import ImageQt

# Konstanten
my_psw = "hgsruesweg1923"
my_prefix = "decrypt_"
my_path = "E:\\Daten\\Dülmen\\HGS\\HGS Rechnungen"

print(sys.platform)

class MainWindow(QMainWindow, Ui_frm_pdfDec):
    def __init__(self, myApp):
        super().__init__()
        self.app = myApp
        self.setWindowIcon(QIcon("ic_lock_open_128_28434.ico"))
        self.setupUi(self)
        self.setAcceptDrops(True)
        self.pixmap = QPixmap()
        self.lbl_datei.setText("")
        self.btn_ende.clicked.connect(self.ende)
        self.btn_finden.clicked.connect(self.findePdf)
        self.lbl_decrypted.hide()

    def ende(self):
        self.close()
        self.app.exit()

    def findePdf(self):
        global my_path

        filename, ok = QFileDialog.getOpenFileName(
            self, "Ein pdf-Dokument auswählen", my_path, "pdf-Dokument (*.pdf *.*)"
        )
        if filename:
            path = Path(filename)
            fn = str(path)
            self.lbl_datei.setText(fn)
            if os.path.exists(fn) and fn.endswith(".pdf"):
                self.pdfVerarbeiten(fn)
        # else:
        #     self.lbl_datei.setText("")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        self.btn_finden.setEnabled(True)
        lines = []
        for url in event.mimeData().urls():
            lines.append(f"{url.toLocalFile()}")
        datei = lines[0]
        if os.path.exists(datei) and datei.endswith(".pdf"):
            self.pdfVerarbeiten(datei)

    def pdfVerarbeiten(self, pdfDatei):
        breite = self.lbl_img.width()
        hoehe = self.lbl_img.height()
        inFilePath, inFileBase = os.path.split(pdfDatei)
        input_name, input_ext = os.path.splitext(inFileBase)
        output_file_name = my_prefix + inFileBase
        outFile = os.path.join(inFilePath, output_file_name)
        if viewDatei := decrypt_pdf(pdfDatei, outFile):
            if viewDatei == outFile:
                # self.lbl_decrypted.isVisible = True
                self.lbl_decrypted.show()
            else:
                # self.lbl_decrypted.isVisible = False
                self.lbl_decrypted.hide()
            qtimg, seitenanz = pdf2bild(viewDatei)
            pixmap = QPixmap.fromImage(qtimg).scaled(breite, hoehe)
            self.lbl_img.setPixmap(pixmap)
            self.lbl_img.setText(None)
            self.lbl_datei.setText(viewDatei)
        else:
            self.lbl_img.setText("Kann die Datei nicht entschlüsseln!")


def pdf2bild(pdfDatei: str) -> (object, int):
    """
    wandelt eine pdf-Datei in ein Bild
    Parameter:
        pdfDatei:   voller DateiName der pdf
    Returns:
        Tupel aus:
            QtImage der 1. Seite des pdf
            Anzahl Seiten, ist bei Mißerfolg = 0
    """
    qordner, qname = os.path.split(pdfDatei)
    purename, qext = os.path.splitext(qname)
    outname = os.path.join(qordner, purename)

    if not os.path.exists(pdfDatei):
        return (None, 0)
    anzSeiten = 0
    pdf = pypdfium2.PdfDocument(pdfDatei)
    pixmap = None
    for i in range(len(pdf)):
        page = pdf[i]
        anzSeiten += 1
        image = page.render(scale=4).to_pil()
        # print(f"Bands: {image.getbands()}")
        # print(f"Modes: {image.mode}")
        # print(f"Size: {image.size}")

        # alte ausgabe in Datei...
        # ausgabe = f"{outname}_{(i+1):2d}.jpg"
        # image.save(ausgabe)
        break  # nur 1. Seite
    pdf.close()
    return (ImageQt(image), anzSeiten)


def decrypt_pdf(in_pdf: str, out_pdf: str) -> bool:
    """
    Versucht, das pdf 'in_pdf' zu öffnen
    Gelingt das nicht, wird "None" zurückgegeben
    Gelingt es, so wird 'out_pdf' erzeugt, wenn 'in_pdf' verschlüsselt war.
    Gibt bei Verschlüsselung 'out_pdf' zurück,
    bei einer unverschlüsselten pdf wird 'in_pdf' zurückgegeben
    """
    global my_psw

    erg = None
    try:
        pdf = pikepdf.open(in_pdf, password=my_psw)
        # print(f"{in_pdf=}, {out_pdf=}")
        if pdf.is_encrypted:
            pdf.save(out_pdf)
            erg = out_pdf
        else:
            erg = in_pdf
    except:
        pass
    finally:
        pdf.close()
    return erg


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec())
