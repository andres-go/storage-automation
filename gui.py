import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QWidget, QHBoxLayout,
    QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from scan import read_barcode

# Manual variable for PersonalInfo
PERSONAL_INFO = "1234567890 - Andres Ojeda"

class ScanApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KUROBI Automation")
        self.setFixedSize(480, 800)

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)  # Add some margins

        # Set global font color and background color
        self.central_widget.setStyleSheet(
            "background-color: #FFFFFF;" 
            "color: #000000;"
        )

        # Top bar layout for user name and datetime
        self.top_bar_layout = QHBoxLayout()
        self.layout.addLayout(self.top_bar_layout)

        # User name display (top-left)
        self.user_name_label = QLabel(f"User: {PERSONAL_INFO.split('-')[1].strip()}", self)
        self.user_name_label.setAlignment(Qt.AlignLeft)
        self.user_name_label.setStyleSheet(
            "font-size: 16px; " 
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
        
        # Add extra spacing to move elements even lower
        self.layout.addSpacing(100)  # Increased from 50 to 100
        
        # Create a container for the scanned data (without border)
        self.data_container = QWidget()
        self.data_layout = QVBoxLayout(self.data_container)
        self.data_layout.setContentsMargins(0, 0, 0, 0)  # Remove internal margins
        
        # Large text area to display scanned data
        self.scanned_data_label = QLabel("Ready to scan", self)
        self.scanned_data_label.setAlignment(Qt.AlignCenter)
        self.scanned_data_label.setStyleSheet(
            "font-size: 25px;" 
            "font-weight: bold;"
        )
        self.data_layout.addWidget(self.scanned_data_label)

        # Display other scanned data (part number)
        self.scanned_data_secondary_label = QLabel(self)
        self.scanned_data_secondary_label.setAlignment(Qt.AlignCenter)
        self.scanned_data_secondary_label.setStyleSheet(
            "font-size: 16px;" 
            "font-weight: normal;"
        )
        self.data_layout.addWidget(self.scanned_data_secondary_label)
        
        # Add the data container to the main layout
        self.layout.addWidget(self.data_container)
        
        # Add even more spacing before the image
        self.layout.addSpacing(80)  # Increased from 40 to 80

        # Image area for instructions or status - center it properly
        self.image_container = QWidget()
        self.image_layout = QVBoxLayout(self.image_container)
        self.image_layout.setAlignment(Qt.AlignCenter)
        self.image_layout.setContentsMargins(0, 0, 0, 0)  # Remove internal margins
        
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_layout.addWidget(self.image_label)
        
        self.layout.addWidget(self.image_container)
        self.show_instruction_image()
        
        # Add spacer to push button to bottom
        self.layout.addStretch()

        # Button to trigger scan - larger and right-aligned
        self.scan_button = QPushButton("Scan", self)
        self.scan_button.setFixedSize(180, 60)  # Increased size from 120,40 to 180,60
        self.scan_button.setStyleSheet(
            "font-size: 18px;" 
            "font-weight: bold;"
            "padding: 10px;"
            "background-color: #2196F3;"
            "color: white;"
            "border-radius: 8px;"
        )
        self.scan_button.clicked.connect(self.perform_scan)
        
        # Right-align the button
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()  # This pushes the button to the right
        self.button_layout.addWidget(self.scan_button)
        # No stretch after the button keeps it right-aligned
        self.layout.addLayout(self.button_layout)
        
        # Add some bottom spacing
        self.layout.addSpacing(30)

        # Timer to update datetime constantly
        self.start_datetime_timer()

    def update_datetime(self):
        """Update the datetime label with the current local datetime."""
        current_datetime = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
        self.datetime_label.setText(f"{current_datetime}")

    def start_datetime_timer(self):
        """Start a timer to update the datetime every second."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)  # Update every 1000ms (1 second)

    def show_instruction_image(self):
        """Show an instruction image for the first-time scan."""
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
        """Show success or failure image based on the scan result."""
        if status == "success":
            image_path = "imgs/success.png"  # Replace with your success image path
        elif status == "failure":
            image_path = "imgs/failure.png"  # Replace with your failure image path
        else:
            image_path = "imgs/scan.png"  # Default to instruction image

        if os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(200, 200, Qt.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText(f"{status.capitalize()} image not found.")

    def perform_scan(self):
        """Perform the barcode scan and update the UI."""
        try:
            scanned_data = read_barcode()  # Call the scan function from scan.py

            if scanned_data and "ERROR" not in scanned_data:
                self.scanned_data_label.setText(f"{scanned_data}")
                self.scanned_data_secondary_label.setText(f"{scanned_data}")
                self.show_status_image("success")
                # Save to terminal
                current_datetime = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
                print(f"{PERSONAL_INFO} - {scanned_data} - {current_datetime}")
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