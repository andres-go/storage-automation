import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QWidget, QHBoxLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from scan import read_barcode
from rfid import Employee

class ScanApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KUROBI Automation")
        self.setFixedSize(480, 800)

        self.employee = Employee()
        self.rfid_buffer = ""
        self.mode = None  # 'prestamo' or 'devolucion'
        self.rfid_set = False  # True si ya se escaneó RFID en la sesión

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.central_widget.setStyleSheet(
            "background-color: #FFFFFF;"
            "color: #000000;"
        )

        # Top bar layout for user name and datetime
        self.top_bar_layout = QHBoxLayout()
        self.layout.addLayout(self.top_bar_layout)

        # User name display (top-left)
        self.user_name_label = QLabel("", self)
        self.user_name_label.setAlignment(Qt.AlignLeft)
        self.user_name_label.setStyleSheet(
            "font-size: 16px;"
            "font-weight: bold;"
        )
        self.top_bar_layout.addWidget(self.user_name_label)

        # Top-right datetime display
        self.datetime_label = QLabel(self)
        self.datetime_label.setAlignment(Qt.AlignRight)
        self.datetime_label.setStyleSheet(
            "font-size: 16px;"
        )
        self.update_datetime()
        self.top_bar_layout.addWidget(self.datetime_label)

        self.layout.addSpacing(100)

        # Main content area
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.content_container)

        # Add even more spacing before the image
        self.layout.addSpacing(80)

        # Image area for instructions or status
        self.image_container = QWidget()
        self.image_layout = QVBoxLayout(self.image_container)
        self.image_layout.setAlignment(Qt.AlignCenter)
        self.image_layout.setContentsMargins(0, 0, 0, 0)
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_layout.addWidget(self.image_label)
        self.layout.addWidget(self.image_container)

        self.layout.addStretch()

        # Scan, Reset, Devolución, and Regresar buttons
        self.scan_button = QPushButton("Scan", self)
        self.scan_button.setFixedSize(180, 60)
        self.scan_button.setStyleSheet(
            "font-size: 18px;"
            "font-weight: bold;"
            "padding: 5px;"
            "background-color: #2196F3;"
            "color: white;"
            "border-radius: 8px;"
        )
        self.scan_button.clicked.connect(self.perform_scan)

        self.exit_button = QPushButton("Salir", self)
        self.exit_button.setFixedSize(180, 60)
        self.exit_button.setStyleSheet(
            "font-size: 18px;"
            "font-weight: bold;"
            "padding: 5px;"
            "background-color: #F44336;"
            "color: white;"
            "border-radius: 8px;"
        )
        self.exit_button.clicked.connect(self.exit_to_main_menu)

        self.regresar_button = QPushButton("Regresar", self)
        self.regresar_button.setFixedSize(180, 60)
        self.regresar_button.setStyleSheet(
            "font-size: 18px;"
            "font-weight: bold;"
            "padding: 5px;"
            "background-color: #9E9E9E;"
            "color: white;"
            "border-radius: 8px;"
        )
        self.regresar_button.clicked.connect(self.show_main_menu)

        self.devolucion_button = QPushButton("Devolución", self)
        self.devolucion_button.setFixedSize(180, 60)
        self.devolucion_button.setStyleSheet(
            "font-size: 18px;"
            "font-weight: bold;"
            "padding: 5px;"
            "background-color: #4CAF50;"
            "color: white;"
            "border-radius: 8px;"
        )
        self.devolucion_button.clicked.connect(self.start_devolucion)

        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.scan_button)
        self.button_layout.addSpacing(20)
        self.button_layout.addWidget(self.exit_button)
        self.button_layout.addSpacing(20)
        self.button_layout.addWidget(self.regresar_button)
        self.button_layout.addStretch()
        self.layout.addLayout(self.button_layout)
        self.layout.addSpacing(30)

        self.start_datetime_timer()

        # Start in main menu
        self.show_main_menu()

    def update_datetime(self):
        current_datetime = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
        self.datetime_label.setText(f"{current_datetime}")

    def start_datetime_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)

    def show_instruction_image(self):
        instruction_image_path = "imgs/scan.png"
        if os.path.exists(instruction_image_path):
            pixmap = QPixmap(instruction_image_path).scaled(
                300,
                300,
                Qt.KeepAspectRatio
            )
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("Instruction image not found.")

    def show_status_image(self, status):
        if status == "success":
            image_path = "imgs/success.png"
        elif status == "failure":
            image_path = "imgs/failure.png"
        else:
            image_path = "imgs/scan.png"
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(200, 200, Qt.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText(f"{status.capitalize()} image not found.")

    def show_main_menu(self):
        self.mode = None
        # Usar clearEmpleado si no hay RFID registrado
        if not self.rfid_set:
            self.employee.clearEmpleado()
        self.rfid_buffer = ""
        self.clear_layout(self.content_layout)
        # Mostrar el nombre si ya hay uno registrado
        if self.rfid_set and self.employee.getEmployeeName():
            self.user_name_label.setText(f"User: {self.employee.getEmployeeName()}")
        else:
            self.user_name_label.setText(f"User: _____")
        self.scan_button.setVisible(False)
        self.exit_button.setVisible(False)
        self.regresar_button.setVisible(False)
        self.devolucion_button.setVisible(True)
        # Main menu label
        menu_label = QLabel("Selecciona una opción", self)
        menu_label.setAlignment(Qt.AlignCenter)
        menu_label.setStyleSheet(
            "font-size: 25px;"
            "font-weight: bold;"
        )
        self.content_layout.addWidget(menu_label)
        # Botón para préstamo (default)
        self.prestamo_button = QPushButton("Préstamo", self)
        self.prestamo_button.setFixedSize(180, 60)
        self.prestamo_button.setStyleSheet(
            "font-size: 18px;"
            "font-weight: bold;"
            "padding: 5px;"
            "background-color: #2196F3;"
            "color: white;"
            "border-radius: 8px;"
        )
        self.prestamo_button.clicked.connect(self.start_prestamo)
        prestamo_layout = QHBoxLayout()
        prestamo_layout.addStretch()
        prestamo_layout.addWidget(self.prestamo_button)
        prestamo_layout.addSpacing(20)
        prestamo_layout.addWidget(self.devolucion_button)
        prestamo_layout.addStretch()
        self.content_layout.addLayout(prestamo_layout)
        self.image_label.setText("")
        self.show_instruction_image()
        self.central_widget.setFocus()
        self.installEventFilter(self)

    def start_prestamo(self):
        self.mode = "prestamo"
        if self.rfid_set and self.employee.getEmployeeName():
            self.show_main_screen()
        else:
            self.show_login_screen("Escanear RFID para préstamo")

    def start_devolucion(self):
        self.mode = "devolucion"
        if self.rfid_set and self.employee.getEmployeeName():
            self.show_main_screen()
        else:
            self.show_login_screen("Escanear RFID para devolución")

    def show_login_screen(self, instruction="Escanear RFID"):
        self.clear_layout(self.content_layout)
        self.user_name_label.setText("")
        self.scan_button.setVisible(False)
        self.exit_button.setVisible(True)
        self.regresar_button.setVisible(True)
        self.devolucion_button.setVisible(False)
        # Show login instruction
        self.login_label = QLabel(instruction, self)
        self.login_label.setAlignment(Qt.AlignCenter)
        self.login_label.setStyleSheet(
            "font-size: 25px;"
            "font-weight: bold;"
        )
        self.content_layout.addWidget(self.login_label)
        self.image_label.setText("")
        self.show_instruction_image()
        self.central_widget.setFocus()
        self.installEventFilter(self)

    def show_main_screen(self):
        self.clear_layout(self.content_layout)
        if self.mode == "prestamo":
            self.user_name_label.setText(f"User: {self.employee.getEmployeeName()}")
            main_label = "Escanear QR para préstamo"
        else:
            self.user_name_label.setText(f"User: {self.employee.getEmployeeName()}")
            main_label = "Escanear QR para devolución"
        # Main scan label
        self.scanned_data_label = QLabel(main_label, self)
        self.scanned_data_label.setAlignment(Qt.AlignCenter)
        self.scanned_data_label.setStyleSheet(
            "font-size: 25px;"
            "font-weight: bold;"
        )
        self.content_layout.addWidget(self.scanned_data_label)
        # Secondary label
        self.scanned_data_secondary_label = QLabel(self)
        self.scanned_data_secondary_label.setAlignment(Qt.AlignCenter)
        self.scanned_data_secondary_label.setStyleSheet(
            "font-size: 16px;"
            "font-weight: normal;"
        )
        self.content_layout.addWidget(self.scanned_data_secondary_label)
        self.show_instruction_image()
        self.scan_button.setVisible(True)
        self.exit_button.setVisible(True)
        self.regresar_button.setVisible(True)
        self.devolucion_button.setVisible(False)
        self.removeEventFilter(self)

    def exit_to_main_menu(self):
        # Salir: regresa a menú principal y reinicia sesión
        self.rfid_set = False
        self.employee.clearEmpleado()
        self.show_main_menu()

    def eventFilter(self, obj, event):
        # 1. En Main menu, si escanean RFID, va directo a préstamo y el dato prevalece
        if self.mode is None:
            if event.type() == event.KeyPress:
                key = event.text()
                if key.isprintable():
                    self.rfid_buffer += key
                if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    rfid = self.rfid_buffer.strip()
                    # Solo permite escanear un RFID si aún no hay uno registrado
                    if rfid and not self.rfid_set and not self.employee.getIDEmpleado():
                        self.employee.setEmpleadoByRFID(rfid)
                        self.rfid_set = True
                        self.rfid_buffer = ""
                        self.mode = "prestamo"
                        self.show_main_screen()
                    # Si ya hay RFID registrado, ignora el nuevo escaneo
                    self.rfid_buffer = ""
                    return True
            return super().eventFilter(obj, event)
        # 2. Si ya se escaneó RFID, no volver a pedirlo al cambiar de modo
        elif self.mode in ("prestamo", "devolucion") and not self.rfid_set:
            if event.type() == event.KeyPress:
                key = event.text()
                if key.isprintable():
                    self.rfid_buffer += key
                if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    rfid = self.rfid_buffer.strip()
                    if rfid:
                        self.employee.setEmpleadoByRFID(rfid)
                        self.rfid_set = True
                        self.rfid_buffer = ""
                        self.show_main_screen()
                    return True
            return super().eventFilter(obj, event)
        else:
            return super().eventFilter(obj, event)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def perform_scan(self):
        try:
            scanned_data = read_barcode()
            if scanned_data and "ERROR" not in scanned_data:
                self.scanned_data_label.setText(f"{scanned_data}")
                self.scanned_data_secondary_label.setText(f"{scanned_data}")
                self.show_status_image("success")
                current_datetime = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
                print(f"{self.employee.getEmployeeName()} - {scanned_data} - {current_datetime} - {self.mode}")
            else:
                self.scanned_data_label.setText("No barcode detected.")
                self.scanned_data_secondary_label.setText("")
                self.show_status_image("failure")
        except Exception as e:
            self.scanned_data_label.setText(f"Error: {e}")
            self.show_status_image("failure")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScanApp()
    window.show()
    sys.exit(app.exec_())