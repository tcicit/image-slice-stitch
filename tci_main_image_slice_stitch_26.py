'''
Programm Name: Image Slice & Stitch
Autor: Thomas Cigolla, 10.2.2025
Version: 0.25
Icons von https://www.flaticon.com/
https://www.flaticon.com/icon-fonts-most-downloaded?weight=regular&type=uicon

'''
import sys
import os
import random
import uuid
import toml
from PIL import Image, ImageDraw
import logging

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QLabel, 
     QColorDialog
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from gui_layout import init_ui, show_about  # Importiere die Methoden aus gui_layout.py

CONFIG_FILE = "config.toml"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ImageStripper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Slice & Stitch")
        self.setGeometry(100, 100, 800, 600)
        self.selected_file = None  # 🛠️ Verhindert den Fehler!

        # Standard-Konfiguration laden
        self.config = {
            "input_folder": "",
            "output_folder": "",
            "strip_count": 6,
            "random_strips": False,
            "min_strip_size": 20,
            "max_strip_size": 100,
            "direction": "vertical",
            "insert_blank": False,
            "blank_width": 100,
            "strip_color": (255, 255, 255),
            "grayscale": False
        }

        self.load_config()

        self.init_ui()  # Rufe die init_ui-Methode auf

        # UI-Elemente erstellen
    def init_ui(self):
        init_ui(self)  # Rufe die init_ui-Methode aus gui_layout.py auf

    def show_about(self):
        show_about(self)  # Rufe die show_about-Methode aus gui_layout.py auf

    def save_config(self):
        """Speichert die aktuelle Konfiguration in einer TOML-Datei, sobald sich eine Einstellung ändert."""
        self.config["strip_count"] = self.strip_count.value()
        self.config["random_strips"] = self.random_strips.isChecked()
        self.config["min_strip_size"] = self.min_strip_size.value()
        self.config["max_strip_size"] = self.max_strip_size.value()
        self.config["direction"] = "horizontal" if self.horizontal_radio.isChecked() else "vertical"
        self.config["insert_blank"] = self.insert_blank.isChecked()
        self.config["blank_width"] = self.blank_width.value()
        self.config["grayscale"] = self.grayscale_checkbox.isChecked()
    
        try:
            with open(CONFIG_FILE, "w") as f:
                toml.dump(self.config, f)
        except Exception as e:
            logging.error(f"Fehler beim Speichern der Konfigurationsdatei: {e}")

    def generate_image(self):
        """Erstellt das Streifenbild und zeigt die Vorschau."""
        if not os.path.exists(self.config["output_folder"]):
            self.show_message("Der Ausgabeordner existiert nicht!")
            return

        if not self.selected_file:
            self.show_message("Bitte zuerst ein Bild auswählen!")
            return

        # File oeffnen
        try:
            img = Image.open(self.selected_file)
        except (FileNotFoundError, OSError):
            self.show_message("Fehler: Ungültiges Bildformat oder Datei nicht gefunden.")
            return

        # Bild nach schwarz weiss konvertieren
        if self.grayscale_checkbox.isChecked():
            img = img.convert("L")

        # Variabeln initalisieren
        width, height = img.size
        num_strips = self.strip_count.value()
        min_size = self.min_strip_size.value()
        max_size = self.max_strip_size.value()
        direction = self.config["direction"]
        blank_size = self.blank_width.value()
        color = tuple(self.config["strip_color"])

        strips = []
        offset = 0
        new_img_width = 0
        new_img_height = 0

        if min_size >= max_size: # Min und Max prüfen
            self.show_message("Max muss größer als Min sein!")
            return

        # Bild zerschneiden
        if direction == "vertical":
            if self.config["random_strips"] == True:
                while offset < width:
                    dim = random.randint(min_size, max_size)

                    if width < (offset + dim):   # letzen Streifen dim anpassen
                        dim = width - offset
                        if dim < min_size:       # Wenn der letzte Streifen kleiner als min Size ist igrnorieren
                            break

                    strips.append(img.crop((offset, 0, (offset + dim), height)))
                    offset += dim
            else:
                strip_dim = width // num_strips
                for i in range(num_strips):
                    strips.append(img.crop((offset, 0, (offset + strip_dim), height)))
                    offset += strip_dim

            new_img_width = offset
            new_img_height = height
        else:
            if self.config["random_strips"] == True:
                while offset < height:
                    dim = random.randint(min_size, max_size)

                    if height < (offset + dim): # letzen Streifen dim anpassen
                        dim = height - offset
                        if dim < min_size:       # Wenn der letzte Streifen kleiner als min Size ist igrnorieren
                            break

                    strips.append(img.crop((0, offset, width, (offset + dim))))
                    offset += dim
            else:
                strip_dim = height // num_strips
                for i in range(num_strips):
                    strips.append(img.crop((0, offset, width, (offset + strip_dim))))
                    offset += strip_dim

            new_img_height = offset
            new_img_width = width

        # Zufällig die normalen Streifen mischen
        random.shuffle(strips)

        # Zwischen Streifen einfügen
        if self.insert_blank.isChecked():
            if direction == "vertical":
                image = Image.new("RGB", (blank_size, height), color)
                draw = ImageDraw.Draw(image)
                draw.rectangle([0, 0, blank_size, height])
            else:
                image = Image.new("RGB", (width, blank_size), color)
                draw = ImageDraw.Draw(image)
                draw.rectangle([0, 0, width, blank_size])

            # Leere Streifen separat und in der richtigen Reihenfolge einfügen
            final_strips = []
            new_img_blank_size = 0
            for i in range(len(strips)):
                final_strips.append(strips[i])
                if i < len(strips)-1:
                    # Füge leere Streifen nach den normalen Streifen hinzu
                    final_strips.append(image)
                    new_img_blank_size += blank_size
                    
            strips = final_strips

            if direction == "vertical":
                new_img_width += new_img_blank_size
            else:
                new_img_height += new_img_blank_size

        # Bild zusammen setzen und File erstellen
        new_img = Image.new("RGB", (new_img_width, new_img_height))
        offset = 0
        if direction == "vertical":
            for strip in strips:
                new_img.paste(strip, (offset, 0))
                offset += strip.width
        else:
            for strip in strips:
                new_img.paste(strip, (0, offset))
                offset += strip.height

        output_filename = os.path.join(self.config["output_folder"], f"{uuid.uuid4()}_striped.jpg")
        new_img.save(output_filename)
        self.show_image_preview(output_filename, self.output_img_label)

    def select_input_folder(self):
        """Eingabe-Ordner auswählen und speichern."""
        self.btn_input_folder.clicked.disconnect()  # Verhindert doppelten Aufruf
        folder = QFileDialog.getExistingDirectory(self, "Eingabe-Ordner wählen")
        if folder:
            self.config["input_folder"] = folder
            dir_name_in = os.path.basename(self.config["input_folder"])
            self.btn_input_folder.setText(f"Aktueller Input-Ordner ({dir_name_in})")
            self.save_config()
        self.btn_input_folder.clicked.connect(self.select_input_folder)  # Neu verbinden

    def select_output_folder(self):
        """Ausgabe-Ordner auswählen und speichern."""
        self.btn_output_folder.clicked.disconnect()
        folder = QFileDialog.getExistingDirectory(self, "Ausgabe-Ordner wählen")
        if folder:
            self.config["output_folder"] = folder
            dir_name_out = os.path.basename(self.config["output_folder"])
            self.btn_output_folder.setText(f"Aktueller Output-Ordner ({dir_name_out})")
            self.save_config()
        self.btn_output_folder.clicked.connect(self.select_output_folder)

    def select_file(self):
        """Bild aus dem Eingabe-Ordner auswählen."""
        if not self.config["input_folder"]:
            self.show_message("Bitte zuerst einen Eingabe-Ordner wählen!")
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Bild auswählen", self.config["input_folder"], "Bilder (*.png *.jpg *.jpeg)")
        if file_path:
            self.selected_file = file_path
            self.show_image_preview(file_path, self.img_label)

    # In der ImageStripper-Klasse
    def show_image_preview(self, file_path, label):
        """Lädt und zeigt die Bildvorschau."""
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            self.show_message("Fehler: Das Bild konnte nicht geladen werden.")
            return
        label.setPixmap(pixmap) #es wird nur noch das Bild gesetzt, aber nicht skalliert.
        label.original_pixmap = pixmap  # Speichere das Original-Pixmap
        label.update_pixmap()  # Skaliere das Bild sofort auf die Größe des Labels

    def show_message(self, text):
        """Zeigt eine Nachricht in der Statusbar an."""
        self.statusBar().showMessage(text, 5000)
    
    def select_color(self):
        """Farbauswahl für leere Streifen."""
        self.btn_color.clicked.disconnect()
        color = QColorDialog.getColor()
        
        if color.isValid():
            self.config["strip_color"] = (color.red(), color.green(), color.blue())
            self.save_config()

            self.btn_color.setText(f"Farbe: RGB:{color.red()}, {color.green()}, {color.blue()}")  
            self.btn_color.setStyleSheet(f"background-color: rgb({color.red()}, {color.green()}, {color.blue()}); color: black;")

        self.btn_color.clicked.connect(self.select_color)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    self.config = toml.load(f)
            except Exception as e:
                logging.error(f"Fehler beim Laden der Konfigurationsdatei: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageStripper()
    window.show()
    sys.exit(app.exec())