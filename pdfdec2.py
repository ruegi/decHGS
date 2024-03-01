"""
pdfdec2.py 
Eine Variante von pdfdec.py, die nur mit pymupdf auskommen soll
rg, b 28.2.24

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
import fitz

# from PIL.ImageQt import ImageQt

# Konstanten
my_psw = "hgsruesweg1923"
my_prefix = "decrypt_"
my_path = "E:\\Daten\\Dülmen\\HGS\\HGS Rechnungen"
# my_path = "."     # für Linux
tmp_image = "tmp_image.jpg"


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
        # Montage des AusgabeNamens
        inFilePath, inFileBase = os.path.split(pdfDatei)
        input_name, input_ext = os.path.splitext(inFileBase)
        output_file_name = my_prefix + inFileBase
        outFile = os.path.join(inFilePath, output_file_name)
        # decrypt der pdf und Generierung des Bildes
        viewDatei = self.decrypt_pdf(pdfDatei, outFile)
        # den 'entschlüsselt' Stempel ggf. zeigen
        if viewDatei == outFile:  # d.h., es wurde entschlüsselt
            self.lbl_decrypted.show()
        else:  # pdf war schon entschlüsselt
            self.lbl_decrypted.hide()
        if viewDatei:  # None bei Fehler im decrypt_pdf
            if os.path.exists(tmp_image):  # image ist ein QImage Objekt
                self.lbl_img.setText(None)
                pixmap = QPixmap(tmp_image)
                self.lbl_img.setPixmap(pixmap)
                os.remove(tmp_image)
            else:
                # print("imago ist None!")
                self.lbl_img.setText("Keine 1. Seite!")
            self.lbl_datei.setText(viewDatei)
        else:
            self.lbl_img.setText("Kann die Datei nicht entschlüsseln!")
        return

    def decrypt_pdf(self, in_pdf: str, out_pdf: str) -> str:
        """
        Versucht, das pdf 'in_pdf' zu öffnen
        Gelingt das nicht, wird "None" zurückgegeben
        Gelingt es, so wird 'out_pdf' erzeugt, wenn 'in_pdf' verschlüsselt war.
        Gibt bei Verschlüsselung 'out_pdf' zurück,
        bei einer unverschlüsselten pdf wird 'in_pdf' zurückgegeben
        """
        global my_psw
        global tmp_image

        pixmap = None
        quimage = None
        erg = None
        try:
            # pdf = fitz.open(in_pdf, password=my_psw)
            pdf = fitz.open(in_pdf)
            if pdf.is_encrypted:
                ret = pdf.authenticate(my_psw)
                if ret > 1:  # war verschlüsselt
                    pdf.save(out_pdf)
                    erg = out_pdf
                elif ret == 1:  # war nicht verschlüsselt
                    erg = in_pdf
                else:  # Fehler
                    pass
            else:  # war nicht verschlüsselt
                erg = in_pdf
            page = pdf[0]
        except:
            page = None

        # pixmap umforamtieren
        if page:
            pix = page.get_pixmap()  # das ist eine mupdf pixmap
            pix.save(tmp_image)
        return erg


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec())
