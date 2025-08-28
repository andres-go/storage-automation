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
from monday_con import (
    process_checkout,
    INVENTORY_BOARD_ID,
    CHECKED_BOARD_ID,
    UID_COLUMN_ID,
    SERIAL_COLUMN_ID,
    PART_COLUMN_ID,
    STATUS_COLUMN_ID,
    CHECKED_BOARD_COLUMN_MAPPING
)

class ScanApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KUROBI Automation")
        self.setFixedSize(800, 413)
        self.employee = Employee()
        self.rfid_buffer = ""
        self.rfid_set = False
        self.motivo = ""

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.central_widget.setStyleSheet("background-color: #FFFFFF;")

        # --- Barra superior ---
        self.top_bar = QWidget()
        self.top_bar.setFixedHeight(80)
        self.top_bar.setStyleSheet("background-color: #455a63;")
        self.top_bar_layout = QHBoxLayout(self.top_bar)
        self.top_bar_layout.setContentsMargins(30, 10, 30, 10)
        self.top_bar_layout.setSpacing(0)
        self.logo_label = QLabel(self.top_bar)
        self.logo_label.setPixmap(QPixmap("imgs/logoKurobi.png").scaled(220, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.top_bar_layout.addWidget(self.logo_label)
        self.top_bar_layout.addStretch()
        self.layout.addWidget(self.top_bar)

        # --- Mensaje de usuario y fecha/hora ---
        self.info_bar = QWidget()
        self.info_bar.setFixedHeight(30)
        self.info_bar.setStyleSheet("background: transparent;")
        self.info_bar_layout = QHBoxLayout(self.info_bar)
        self.info_bar_layout.setContentsMargins(30, 0, 30, 0)
        self.user_name_label = QLabel("", self.info_bar)
        self.user_name_label.setAlignment(Qt.AlignLeft)
        self.user_name_label.setStyleSheet("font-size: 15px; color: #455a63; font-weight: bold;")
        self.info_bar_layout.addWidget(self.user_name_label)
        self.datetime_label = QLabel(self.info_bar)
        self.datetime_label.setAlignment(Qt.AlignRight)
        self.datetime_label.setStyleSheet("font-size: 15px; color: #455a63;")
        self.info_bar_layout.addWidget(self.datetime_label)
        self.layout.addWidget(self.info_bar)

        self.update_datetime()
        self.start_datetime_timer()

        # --- Área de resultado ---
        self.result_container = QWidget()
        self.result_layout = QVBoxLayout(self.result_container)
        self.result_layout.setContentsMargins(0, 0, 0, 0)
        self.result_layout.setSpacing(10)
        self.result_layout.setAlignment(Qt.AlignCenter)
        self.result_image = QLabel(self.result_container)
        self.result_image.setAlignment(Qt.AlignCenter)
        self.result_layout.addWidget(self.result_image)
        self.result_message = QLabel("", self.result_container)
        self.result_message.setAlignment(Qt.AlignCenter)
        self.result_message.setStyleSheet("font-size: 22px; color: #455a63; font-weight: bold;")
        self.result_layout.addWidget(self.result_message)
        self.layout.addWidget(self.result_container, stretch=1)

        # --- Botones ---
        self.button_bar = QWidget()
        self.button_bar_layout = QHBoxLayout(self.button_bar)
        self.button_bar_layout.setContentsMargins(0, 0, 20, 20)
        self.button_bar_layout.setSpacing(30)
        self.button_bar_layout.addStretch()
        self.scan_button = QPushButton("Escanear", self.button_bar)
        self.scan_button.setFixedSize(180, 50)
        self.scan_button.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #0d6324; color: white; border-radius: 8px;")
        self.scan_button.clicked.connect(self.perform_scan)
        self.scan_button.setVisible(False)
        self.button_bar_layout.addWidget(self.scan_button)
        self.regresar_button = QPushButton("Regresar", self.button_bar)
        self.regresar_button.setFixedSize(220, 50)
        self.regresar_button.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #455a63; color: white; border-radius: 8px;")
        self.regresar_button.clicked.connect(self.show_motivo_menu)
        self.regresar_button.setVisible(False)
        self.button_bar_layout.addWidget(self.regresar_button)
        self.exit_button = QPushButton("Salir", self.button_bar)
        self.exit_button.setFixedSize(180, 50)
        self.exit_button.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #A30000; color: white; border-radius: 8px;")
        self.exit_button.clicked.connect(self.reset_workflow)
        self.exit_button.setVisible(False)
        self.button_bar_layout.addWidget(self.exit_button)
        self.button_bar_layout.addStretch()
        self.layout.addWidget(self.button_bar)

        self.motivos_layout = None  # Layout de botones de motivo
        self.reset_workflow()

    def update_datetime(self):
        current_datetime = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
        self.datetime_label.setText(f"{current_datetime}")

    def start_datetime_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)

    def show_instruction_image(self):
        self.result_image.setPixmap(QPixmap("imgs/scan.png").scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.result_message.setText("")

    def show_status_image(self, status):
        # Imagen de resultado más pequeña después de escanear
        if status == "success":
            self.result_image.setPixmap(QPixmap("imgs/success.png").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        elif status == "failure":
            self.result_image.setPixmap(QPixmap("imgs/failure.png").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        elif status == "loading":
            self.result_image.setPixmap(QPixmap("imgs/loading.png").scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.result_image.setPixmap(QPixmap("imgs/scan.png").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def reset_workflow(self):
        if hasattr(self, 'motivos_layout') and self.motivos_layout is not None:
            for i in reversed(range(self.motivos_layout.count())):
                col = self.motivos_layout.itemAt(i)
                if col is not None and col.layout() is not None:
                    for j in reversed(range(col.layout().count())):
                        btn = col.layout().itemAt(j).widget()
                        if btn:
                            btn.setParent(None)
                            btn.deleteLater()
            self.result_layout.removeItem(self.motivos_layout)
            self.motivos_layout = None
        self.mode = None
        self.motivo = ""
        self.rfid_set = False
        self.employee.clearEmpleado()
        self.rfid_buffer = ""
        self.user_name_label.setText("")
        self.scan_button.setVisible(False)
        self.exit_button.setVisible(False)
        self.regresar_button.setVisible(False)
        self.result_message.setText("")
        self.show_instruction_image()
        self.removeEventFilter(self)
        self.central_widget.setFocus()
        self.installEventFilter(self)
        self.result_message.setText("Escanee su RFID para continuar")

    def show_motivo_menu(self):
        self.result_message.setText("Selecciona el motivo")
        self.scan_button.setVisible(False)
        self.exit_button.setVisible(True)
        self.regresar_button.setVisible(False)
        self.motivo = ""
        self.result_image.clear()  # No mostrar imagen en menú de motivo
        # Eliminar layout de motivos si existe
        if self.motivos_layout is not None:
            for i in reversed(range(self.motivos_layout.count())):
                col = self.motivos_layout.itemAt(i)
                if col is not None and col.layout() is not None:
                    for j in reversed(range(col.layout().count())):
                        btn = col.layout().itemAt(j).widget()
                        if btn:
                            btn.setParent(None)
                            btn.deleteLater()
            self.result_layout.removeItem(self.motivos_layout)
            self.motivos_layout = None
        # Crear layout de dos columnas para los botones
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(60)
        # Columna izquierda
        col_izq = QVBoxLayout()
        col_izq.setSpacing(30)
        btn_demo = QPushButton("Demo Oficina", self.result_container)
        btn_demo.setFixedSize(180, 50)
        btn_demo.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #455a63; color: white; border-radius: 8px;")
        btn_demo.clicked.connect(self.motivo_demo_oficina)
        col_izq.addWidget(btn_demo)
        btn_visita = QPushButton("Visita cliente", self.result_container)
        btn_visita.setFixedSize(180, 50)
        btn_visita.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #455a63; color: white; border-radius: 8px;")
        btn_visita.clicked.connect(self.motivo_visita_cliente)
        col_izq.addWidget(btn_visita)
        # Columna derecha
        col_der = QVBoxLayout()
        col_der.setSpacing(30)
        btn_cambio = QPushButton("Cambio Oficina", self.result_container)
        btn_cambio.setFixedSize(180, 50)
        btn_cambio.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #455a63; color: white; border-radius: 8px;")
        btn_cambio.clicked.connect(self.motivo_cambio_oficina)
        col_der.addWidget(btn_cambio)
        btn_prestamo = QPushButton("Préstamo cliente", self.result_container)
        btn_prestamo.setFixedSize(180, 50)
        btn_prestamo.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #455a63; color: white; border-radius: 8px;")
        btn_prestamo.clicked.connect(self.motivo_prestamo_cliente)
        col_der.addWidget(btn_prestamo)
        botones_layout.addLayout(col_izq)
        botones_layout.addLayout(col_der)
        self.result_layout.addLayout(botones_layout)
        self.motivos_layout = botones_layout

    def motivo_prestamo_cliente(self):
        self.motivo = "Préstamo cliente"
        self.show_main_screen()

    def motivo_visita_cliente(self):
        self.motivo = "Visita cliente"
        self.show_main_screen()

    def motivo_demo_oficina(self):
        self.motivo = "Demo Oficina"
        self.show_main_screen()

    def motivo_cambio_oficina(self):
        self.motivo = "Cambio Oficina"
        self.show_main_screen()

    def show_main_screen(self):
        # Eliminar layout de motivos si existe
        if self.motivos_layout is not None:
            for i in reversed(range(self.motivos_layout.count())):
                col = self.motivos_layout.itemAt(i)
                if col is not None and col.layout() is not None:
                    for j in reversed(range(col.layout().count())):
                        btn = col.layout().itemAt(j).widget()
                        if btn:
                            btn.setParent(None)
                            btn.deleteLater()
            self.result_layout.removeItem(self.motivos_layout)
            self.motivos_layout = None
        motivo_str = f" | Motivo: {self.motivo}"
        self.user_name_label.setText(f"User: {self.employee.getEmployeeName()}{motivo_str}")
        self.result_message.setText("Escanear QR o código de barras")
        # Imagen de resultado más pequeña
        self.result_image.setPixmap(QPixmap("imgs/scan.png").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.scan_button.setVisible(True)
        self.exit_button.setVisible(True)
        self.regresar_button.setVisible(True)
        self.removeEventFilter(self)

    def clear_layout(self, layout):
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            elif item.layout() is not None:
                self.clear_layout(item.layout())

    def eventFilter(self, obj, event):
        if self.mode is None:
            if event.type() == event.KeyPress:
                key = event.text()
                if key.isprintable():
                    self.rfid_buffer += key
                if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    rfid = self.rfid_buffer.strip()
                    if rfid and not self.rfid_set and not self.employee.getIDEmpleado():
                        self.employee.setEmpleadoByRFID(rfid)
                        self.rfid_set = True
                        self.rfid_buffer = ""
                        self.mode = "prestamo"
                        self.show_motivo_menu()
                    self.rfid_buffer = ""
                    return True
            return super().eventFilter(obj, event)
        else:
            return super().eventFilter(obj, event)

    def perform_scan(self):
        try:
            self.show_status_image("loading")
            self.result_message.setText("")  # Limpiar mensaje al mostrar loading
            QApplication.processEvents()  # Forzar refresco visual
            scanned_data = read_barcode()
            # Validar si el objeto ya está registrado (Checked Out) en Monday.com
            from monday_con import get_item_status_by_uid
            status = get_item_status_by_uid(
                INVENTORY_BOARD_ID,
                UID_COLUMN_ID,
                scanned_data,
                STATUS_COLUMN_ID
            )
            if status is None:
                self.show_status_image("failure")
                self.result_message.setText("No se encontró el objeto en el inventario.")
                return
            if status == "Checked Out":
                self.show_status_image("failure")
                self.result_message.setText("El ítem ya está registrado (Checked Out) en Monday.com.")
                return
            self.result_message.setText(scanned_data)
            if self.mode == "prestamo":
                motivo_completo = self.motivo
                from monday_con import process_checkout
                success = process_checkout(
                    INVENTORY_BOARD_ID,
                    CHECKED_BOARD_ID,
                    scanned_data,
                    self.employee.getEmployeeName(),
                    motivo_completo,
                    UID_COLUMN_ID,
                    SERIAL_COLUMN_ID,
                    PART_COLUMN_ID,
                    STATUS_COLUMN_ID,
                    CHECKED_BOARD_COLUMN_MAPPING
                )
                if success:
                    self.show_status_image("success")
                    self.result_message.setText("Registro en Monday.com exitoso.")
                else:
                    self.show_status_image("failure")
                    self.result_message.setText("Error al registrar en Monday.com.")
        except Exception as e:
            self.show_status_image("failure")
            self.result_message.setText(f"Error: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScanApp()
    window.show()
    sys.exit(app.exec_())