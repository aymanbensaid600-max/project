import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect

class CustomPopup(QWidget):
    def __init__(self, popup_type="success", message=""):
        super().__init__()
        # Ajout de WindowStaysOnTopHint pour être au-dessus
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(300, 260)

        self.main = QWidget(self)
        self.main.setGeometry(0, 0, 300, 260)
        self.main.setStyleSheet("""
            QWidget {
                border-radius: 15px;
                background-color: #28a745;
            }
        """ if popup_type == "success" else """
            QWidget {
                border-radius: 15px;
                background-color: #dc3545;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 4)
        self.main.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.main)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        icon_wrapper = QWidget()
        icon_wrapper.setFixedSize(70, 70)
        icon_wrapper.setStyleSheet("""
         background-color: transparent;
         border: 2px solid white;
         border-radius: 35px;
         """)

        icon_label = QLabel("✔" if popup_type == "success" else "✖", parent=icon_wrapper)
        icon_label.setFont(QFont("Arial", 32))
        icon_label.setStyleSheet("color: white;")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setGeometry(0, 0, 70, 70)
        layout.addWidget(icon_wrapper, alignment=Qt.AlignCenter)

        title = QLabel("Success!" if popup_type == "success" else "Error!")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel(message)
        subtitle.setFont(QFont("Arial", 9))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)

        button = QPushButton("Continue" if popup_type == "success" else "Try again")
        button.setFixedWidth(120)
        button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
            }
        """)
        button.clicked.connect(self.close)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        layout.addWidget(button, alignment=Qt.AlignCenter)

        if popup_type == "success":
            QTimer.singleShot(3500, self.close)

    def show_centered(self, reference_widget=None):
        if reference_widget:
            center_point = reference_widget.mapToGlobal(reference_widget.rect().center())
            self.move(center_point.x() - self.width() // 2, center_point.y() - self.height() // 2)
        else:
            screen = QApplication.primaryScreen().availableGeometry()
            center = screen.center()
            self.move(center.x() - self.width() // 2, center.y() - self.height() // 2)
        self.show()
        self.raise_()
        self.activateWindow()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = QWidget()
    main_window.resize(600, 400)
    main_window.show()

    popup = CustomPopup("success", "L’opération a réussi !")
    popup.show_centered(main_window)

    sys.exit(app.exec())
