from PyQt6.QtWidgets import (
    QFileDialog, QLabel, QPushButton, QGroupBox, QMessageBox,
    QVBoxLayout, QHBoxLayout, QWidget, QSpinBox, QCheckBox, QRadioButton, QSplitter
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt
import os

# Konstanten für Dateiformate und Standardwerte
SUPPORTED_IMAGE_FORMATS = "*.png *.jpg *.jpeg *.bmp *.gif"
DEFAULT_PREVIEW_WIDTH = 400
DEFAULT_PREVIEW_HEIGHT = 300

class ClickableLabel(QLabel):
    def __init__(self, text="Kein Bild ausgewählt", parent=None, main_window=None):
        super().__init__(text, parent)
        self.main_window = main_window  # Speichert Referenz auf ImageStripper
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"border: 2px dashed gray; min-height: {DEFAULT_PREVIEW_HEIGHT}px; min-width: {DEFAULT_PREVIEW_WIDTH}px;")
        self.setAcceptDrops(True)  # Drag & Drop aktivieren
        self.original_pixmap = None
        self.current_file_path = None

    def mousePressEvent(self, event):
        if self.main_window:  # Sicherstellen, dass die Referenz existiert
            default_dir = self.main_window.config.get("input_folder", "")
        else:
            default_dir = ""

        file_path, _ = QFileDialog.getOpenFileName(self, "Bild auswählen", default_dir, f"Bilder ({SUPPORTED_IMAGE_FORMATS})")
        if file_path:
            self.current_file_path = file_path  # Speichere den Pfad
            self.original_pixmap = QPixmap(file_path) #bild laden
            self.update_pixmap()  #bild aktualisieren
            self.setText("")

            if self.main_window:
                self.main_window.selected_file = file_path

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            self.current_file_path = file_path
            self.original_pixmap = QPixmap(file_path) #bild laden
            self.update_pixmap() #bild aktualisieren
            self.setText("")
            if self.main_window:
                self.main_window.selected_file = file_path

    def update_pixmap(self):
        if self.original_pixmap: #überprüfung ob ein Bild geladen wurde
            self.setPixmap(self.original_pixmap.scaled(self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatio))

    def resizeEvent(self, event):
        self.update_pixmap()
        super().resizeEvent(event)

class ScalableLabel(QLabel):
    """QLabel, das Bilder dynamisch skaliert."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"border: 2px dashed gray; min-height: {DEFAULT_PREVIEW_HEIGHT}px; min-width: {DEFAULT_PREVIEW_WIDTH}px;")
        self.original_pixmap = None
        self.setText("Kein Bild generiert")

    def setPixmap(self, pixmap):
        self.original_pixmap = pixmap #das Originalbild wird nur in der Variable original_pixmap gespeichert
        self.update_pixmap()  # Bild aktualisieren

    def update_pixmap(self):
        if self.original_pixmap:
            scaled_pixmap = self.original_pixmap.scaled(
                self.width(), self.height(),
                Qt.AspectRatioMode.KeepAspectRatio
            )
            super().setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        self.update_pixmap()
        super().resizeEvent(event)

def init_ui(self):
    # Ordnerauswahl
    folder_group = QGroupBox("Ordnerauswahl")
    folder_group.setStyleSheet("QGroupBox { font-weight: bold; }")
    folder_layout = QVBoxLayout()
    dir_name_in = os.path.basename(self.config["input_folder"])
    self.btn_input_folder = QPushButton(QIcon(os.path.join(os.getcwd(), "folder.png")), f"Aktueller Input-Ordner ({dir_name_in})")
    self.btn_input_folder.setToolTip("Wählen Sie den Ordner, der die Eingabebilder enthält.")
    self.btn_input_folder.clicked.connect(self.select_input_folder)
    dir_name_out = os.path.basename(self.config["output_folder"])
    self.btn_output_folder = QPushButton(QIcon(os.path.join(os.getcwd(), "folder.png")), f"Aktueller Output-Ordner ({dir_name_out})")
    self.btn_output_folder.setToolTip("Wählen Sie den Ordner, in dem die Ausgabebilder gespeichert werden.")
    self.btn_output_folder.clicked.connect(self.select_output_folder)
    folder_layout.addWidget(self.btn_input_folder)
    folder_layout.addWidget(self.btn_output_folder)
    folder_group.setLayout(folder_layout)

    # Bildauswahl
    file_group = QGroupBox("Bildauswahl")
    file_group.setStyleSheet("QGroupBox { font-weight: bold; }")
    file_layout = QVBoxLayout()
    self.btn_select_file = QPushButton(QIcon(os.path.join(os.getcwd(), "add-image.png")), "Bild auswählen")
    self.btn_select_file.setToolTip("Wählen Sie ein Bild aus dem Eingabe-Ordner aus.")
    self.btn_select_file.clicked.connect(self.select_file)
    file_layout.addWidget(self.btn_select_file)
    file_group.setLayout(file_layout)

    # Streifen-Einstellungen
    strip_settings_group = QGroupBox("Streifen-Einstellungen")
    strip_settings_group.setStyleSheet("QGroupBox { font-weight: bold; }")
    strip_settings_layout = QVBoxLayout()
    param_direction = QHBoxLayout()
    self.horizontal_radio = QRadioButton("Horizontal")
    self.horizontal_radio.setToolTip("Schneiden Sie das Bild horizontal in Streifen.")
    self.vertical_radio = QRadioButton("Vertikal")
    self.vertical_radio.setToolTip("Schneiden Sie das Bild vertikal in Streifen.")
    if self.config["direction"] == "vertical":
        self.vertical_radio.setChecked(True)
    else:
        self.horizontal_radio.setChecked(True)
    param_direction.setAlignment(Qt.AlignmentFlag.AlignLeft)
    param_direction.addWidget(QLabel("Schneidrichtung:"))
    param_direction.addWidget(self.horizontal_radio)
    param_direction.addWidget(self.vertical_radio)
    strip_settings_layout.addLayout(param_direction)

    param_layout_strip_count = QHBoxLayout()
    self.strip_count = QSpinBox()
    self.strip_count.setRange(2, 1000)
    self.strip_count.setValue(self.config["strip_count"])
    self.strip_count.setToolTip("Geben Sie die Anzahl der Streifen an, in die das Bild geschnitten werden soll.")
    param_layout_strip_count.setAlignment(Qt.AlignmentFlag.AlignLeft)
    param_layout_strip_count.addWidget(QLabel("Anzahl Streifen:"))
    param_layout_strip_count.addWidget(self.strip_count)
    strip_settings_layout.addLayout(param_layout_strip_count)

    param_layout = QHBoxLayout()
    self.random_strips = QCheckBox("Zufällige Streifen schneiden:")
    self.random_strips.setChecked(self.config["random_strips"])
    self.random_strips.setToolTip("Aktivieren Sie diese Option, um die Streifenbreiten zufällig zu variieren.")
    self.min_strip_size = QSpinBox()
    self.min_strip_size.setRange(5, 600)
    self.min_strip_size.setValue(self.config["min_strip_size"])
    self.min_strip_size.setToolTip("Geben Sie die minimale Breite der Streifen an.")
    self.max_strip_size = QSpinBox()
    self.max_strip_size.setRange(10, 1500)
    self.max_strip_size.setValue(self.config["max_strip_size"])
    self.max_strip_size.setToolTip("Geben Sie die maximale Breite der Streifen an.")
    param_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    param_layout.addWidget(self.random_strips)
    param_layout.addWidget(QLabel("Min:"))
    param_layout.addWidget(self.min_strip_size)
    param_layout.addWidget(QLabel("Max:"))
    param_layout.addWidget(self.max_strip_size)
    strip_settings_layout.addLayout(param_layout)
    strip_settings_group.setLayout(strip_settings_layout)

    # Leere Streifen
    blank_strip_group = QGroupBox("Leere Streifen")
    blank_strip_group.setStyleSheet("QGroupBox { font-weight: bold; }")
    blank_strip_layout = QVBoxLayout()
    color_layout = QHBoxLayout()
    self.insert_blank = QCheckBox("Streifen einfügen:")
    self.insert_blank.setChecked(self.config["insert_blank"])
    self.insert_blank.setToolTip("Aktivieren Sie diese Option, um leere Streifen zwischen den Bildstreifen einzufügen.")
    self.blank_width = QSpinBox()
    self.blank_width.setRange(1, 1500)
    self.blank_width.setValue(self.config["blank_width"])
    self.blank_width.setToolTip("Geben Sie die Breite der leeren Streifen an.")
    self.btn_color = QPushButton(f"Streifenfarbe")
    self.btn_color.setToolTip("Wählen Sie die Farbe der leeren Streifen.")
    rgb_values = ", ".join(map(str, self.config["strip_color"]))
    self.btn_color.setStyleSheet(f'background-color: rgb({rgb_values}); color: black;')
    self.btn_color.clicked.connect(self.select_color)
    color_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    color_layout.addWidget(self.insert_blank)
    color_layout.addWidget(QLabel("Breite:"))
    color_layout.addWidget(self.blank_width)
    color_layout.addWidget(self.btn_color)
    blank_strip_layout.addLayout(color_layout)
    blank_strip_group.setLayout(blank_strip_layout)

    # Bildoptionen
    image_options_group = QGroupBox("Bildoptionen")
    image_options_group.setStyleSheet("QGroupBox { font-weight: bold; }")
    image_options_layout = QVBoxLayout()
    self.grayscale_checkbox = QCheckBox("Bild in Schwarz-Weiss konvertieren:")
    self.grayscale_checkbox.setChecked(self.config["grayscale"])
    self.grayscale_checkbox.setToolTip("Aktivieren Sie diese Option, um das Bild in Schwarz-Weiss zu konvertieren.")
    image_options_layout.addWidget(self.grayscale_checkbox)
    image_options_group.setLayout(image_options_layout)

    # Aktionen
    actions_group = QGroupBox("Aktionen")
    actions_group.setStyleSheet("QGroupBox { font-weight: bold; }")
    actions_layout = QVBoxLayout()
    self.btn_generate = QPushButton(QIcon(os.path.join(os.getcwd(), "picture.png")), "Bild generieren")
    self.btn_generate.setToolTip("Klicken Sie hier, um das Streifenbild zu generieren.")
    self.btn_generate.setStyleSheet(f'background-color: #B7B7B7; color: seagreen;')
    self.btn_generate.clicked.connect(self.generate_image)
    self.btn_quit = QPushButton(QIcon(os.path.join(os.getcwd(), "circle-xmark.png")), "Beenden")
    self.btn_quit.setToolTip("Klicken Sie hier, um das Programm zu beenden.")
    self.btn_quit.clicked.connect(self.close)
    self.btn_about = QPushButton("Über")
    self.btn_about.setToolTip("Klicken Sie hier, um Informationen über das Programm anzuzeigen.")
    self.btn_about.clicked.connect(self.show_about)
    actions_layout.addWidget(self.btn_generate)
    actions_layout.addWidget(self.btn_quit)
    actions_layout.addWidget(self.btn_about)
    actions_group.setLayout(actions_layout)

    # Layout zusammensetzen
    layout1 = QVBoxLayout()
    layout1.addWidget(folder_group)
    layout1.addWidget(file_group)
    layout1.addWidget(strip_settings_group)
    layout1.addWidget(blank_strip_group)
    layout1.addWidget(image_options_group)
    layout1.addStretch()
    layout1.addWidget(actions_group)

    layout2 = QVBoxLayout()
    self.img_label = ClickableLabel(parent=self, main_window=self)
    self.output_img_label = ScalableLabel(parent=self)
    layout2.addWidget(self.img_label)
    layout2.addWidget(self.output_img_label)

    # Verwende QSplitter, um die Layouts zu trennen
    splitter = QSplitter(Qt.Orientation.Horizontal)
    left_widget = QWidget()
    left_widget.setLayout(layout1)
    left_widget.setMinimumWidth(350)
    left_widget.setMaximumWidth(350)
    right_widget = QWidget()
    right_widget.setLayout(layout2)
    splitter.addWidget(left_widget)
    splitter.addWidget(right_widget)
    splitter.setStretchFactor(1, 1)  # Der rechte Bereich wird skaliert

    # Setze das Layout in einem Container
    container = QWidget()
    container_layout = QVBoxLayout()
    container_layout.addWidget(splitter)
    container.setLayout(container_layout)
    self.setCentralWidget(container)

    # Automatisches Speichern bei Änderungen
    self.strip_count.valueChanged.connect(self.save_config)
    self.random_strips.stateChanged.connect(self.save_config)
    self.min_strip_size.valueChanged.connect(self.save_config)
    self.max_strip_size.valueChanged.connect(self.save_config)
    self.horizontal_radio.toggled.connect(self.save_config)
    self.vertical_radio.toggled.connect(self.save_config)
    self.insert_blank.stateChanged.connect(self.save_config)
    self.blank_width.valueChanged.connect(self.save_config)
    self.btn_color.clicked.connect(self.select_color)
    self.btn_input_folder.clicked.connect(self.select_input_folder)
    self.btn_output_folder.clicked.connect(self.select_output_folder)
    self.grayscale_checkbox.stateChanged.connect(self.save_config)


def show_about(self):
    """Zeigt ein Popup mit Informationen über das Programm an."""
    about_text = (
        "Image Slice & Stitch\n"
        "Version: 0.25\n"
        "Autor: Thomas Cigolla\n"
        "Datum: 10.2.2025\n\n"
        "Icons von https://www.flaticon.com/\n"
        "Lizenz: MIT"
    )
    QMessageBox.about(self, "Über Image Slice & Stitch", about_text)