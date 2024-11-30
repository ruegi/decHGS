"""
pdfdec3.py 
Eine Variante von pdfdec.py, die nur mit pymupdf & PIP auskommt
rg, 01.03.24

Änderungen
2024-11-29      Dialog eingebaut, um den neuen Dateinamen bestätigen/ändern zu lassen
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QApplication,
    QDialog,
    QFileDialog,
    QMessageBox,
    QLineEdit,
    QLabel,
    QLabel,
)
from PyQt6.QtGui import QPixmap, QImage, QIcon
from AusgabeDialogUI import Ui_Dialog as Ui_AusgabeDialog

from frm_pdfdec import Ui_frm_pdfDec

import os
import sys
import shutil
from pathlib import Path
import fitz
import datetime

from PIL.ImageQt import Image, ImageQt


# Konstanten
my_psw = "hgsruesweg1923"
if sys.platform == "linux":
    my_path = "/home/ruegi/Desktop/Daten/Dülmen/HGS/HGS Rechnungen"
elif sys.platform == "win32":
    my_path = "E:\\Daten\\Dülmen\\HGS\\HGS Rechnungen"
else:
    my_path = "./"

alt_pfad = my_path + "/crypt"
jahr = str(datetime.datetime.today().year)
monat = "{:02n}".format(datetime.datetime.today().month)
praefix = jahr + "-" + monat + "_"

tmp_image = "tmp_image.jpg"


class AusgabeDialog(QDialog, Ui_AusgabeDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)


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
        self.AusgabeDialog = None
        self.AusgabeName = None

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

    def bestaetigeAusgabeName(self, outFileName):
        # erzeugt eine Dialog, um den neuen Namen bestätigen/ändern zu lassen
        # Parameter: outFileName: Name der AusgabeDatei
        # Returns: ---
        self.AusgabeName = outFileName
        self.AusgabeDialog = AusgabeDialog()
        self.AusgabeDialog.le_rename.setText(outFileName)
        self.AusgabeDialog.accepted.connect(lambda: self.AusgabeDialogOK())
        self.AusgabeDialog.rejected.connect(lambda: self.AusgabeDialogCancel())
        self.AusgabeDialog.le_rename.setFocus()
        self.AusgabeDialog.exec()
        return

    # @pyqtSlot()
    def AusgabeDialogOK(self):
        # prüfen, ob es das Ziel schon gibt
        # Achtung! Windows unterscheidet Groß/Kleischreibung nicht!
        self.AusgabeName = self.AusgabeDialog.le_rename.text()
        return

    # @pyqtSlot()
    def AusgabeDialogCancel(self):
        # self.AusgabeName
        pass  # keine Veränderung des AusgabeNamens

    def pdfVerarbeiten(self, pdfDatei):
        global alt_pfad

        breite = self.lbl_img.width()
        hoehe = self.lbl_img.height()
        # Montage des AusgabeNamens
        inFilePath, inFileBase = os.path.split(pdfDatei)
        input_name, input_ext = os.path.splitext(inFileBase)
        output_file_name = praefix + "decrypt_" + inFileBase
        outFile = os.path.join(inFilePath, output_file_name)
        alt_pfad = os.path.join(inFilePath, "crypt")
        if not os.path.exists(alt_pfad):
            os.mkdir(alt_pfad)

        tempfile = os.path.join(inFilePath, "this_is_temp.pdf")

        # decrypt der pdf und Generierung des Bildes
        viewDatei, pixmap, decryped = self.decrypt_pdf(pdfDatei, tempfile)

        # den 'entschlüsselt' Stempel ggf. zeigen
        if decryped:  # d.h., es  wurde entschlüsselt
            self.lbl_decrypted.show()
            self.verschiebe_original(pdfDatei)
        else:  # pdf war schon entschlüsselt
            self.lbl_decrypted.hide()
        if viewDatei:  # None bei Fehler im decrypt_pdf
            if pixmap:  # pixmap ist ein QPixmap Objekt
                self.lbl_img.setText(None)
                self.lbl_img.setPixmap(pixmap)
            else:
                self.lbl_img.setText("Keine 1. Seite!")

            self.bestaetigeAusgabeName(outFile)
            outFile = self.AusgabeName  ## ggf. Anderungen ermöglichen
            if not os.path.exists(outFile):
                os.rename(tempfile, outFile)
            else:
                QMessageBox.WARNING(
                    self,
                    "Problem",
                    f"\nAchtung!!\n\nKann das Original [{inFileBase}] nicht\nnach [{alt_pfad}] verschieben!\nDie Datei exitiert dort bereits! \n\n",
                )
            self.lbl_datei.setText(outFile)

        else:
            self.lbl_img.setText("Kann die Datei nicht entschlüsseln!")
        return

    def decrypt_pdf(self, in_pdf: str, out_pdf: str) -> (str, object, bool):
        """
        Versucht, das pdf 'in_pdf' zu öffnen
        Zurückgegeben wird eine Liste aus einem String und dem Pixmap der ertens Seite des pdf:
        Bei Fehler, wird im String "None" zurückgewgeben;
        Bei Erfolg wird, wenn die Eingabe verschlüsselt war, der Name der
        entschlüsselten pdf zurückgegeben (out_pdf);
        oder bei einer 'offenen' pdf deren Name zurückgegeben (=in_pdf)
        sowie das Flag 'decrypted'(True/False).
        """
        global my_psw

        pixmap = None
        quimage = None
        erg = None
        breite = self.lbl_img.width()
        hoehe = self.lbl_img.height()
        decryped = False
        try:
            pdf = fitz.open(in_pdf)
            if pdf.is_encrypted:
                ret = pdf.authenticate(my_psw)  # erst hier das Passwort eingeben!
                if ret > 1:  # war verschlüsselt
                    pdf.save(out_pdf)  # unverschlüsselt speichern
                    erg = out_pdf
                    decryped = True
                elif ret == 1:  # war nicht verschlüsselt
                    erg = in_pdf
                else:  # Fehler
                    pass
            else:  # war nicht verschlüsselt
                erg = in_pdf
            page = pdf[0]
        except:
            page = None

        # pixmap umformatieren
        if page:
            pix = page.get_pixmap()  # das ist eine mupdf pixmap
            mode = "RGBA" if pix.alpha else "RGB"
            img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)  # PIL !
            qtimg = ImageQt(img)  # PIL !
            pixmap = QPixmap.fromImage(qtimg).scaled(breite, hoehe)
        return (erg, pixmap, decryped)

    def verschiebe_original(self, quelle):
        global alt_pfad
        quellPfad, quellName = os.path.split(quelle)
        ziel = alt_pfad + "/" + quellName
        if not os.path.exists(ziel):
            shutil.move(quelle, ziel)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec())
