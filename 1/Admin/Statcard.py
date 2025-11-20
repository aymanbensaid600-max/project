from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QFrame, QLabel
)
from PySide6.QtGui import QFont, QColor, QPixmap
from PySide6.QtWidgets import QGraphicsDropShadowEffect
import sys
import os

class StatistiqueCard(QFrame):
    def __init__(self, titre: str, nombre: int, couleur: str = "#1abc9c", icon_path: str = ""):
        super().__init__()

        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 15px;
                
            }}
        """)
        self.setMinimumSize(150, 160)
        

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
    
        layout.setSpacing(10)
        line1=QHBoxLayout()
        line2=QHBoxLayout()
        if os.path.exists(icon_path):
            icon_label = QLabel()
            pixmap = QPixmap(icon_path).scaled(30, 30)
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignCenter)
            line1.addWidget(icon_label)

        # Titre
        label_titre = QLabel(titre)
        label_titre.setFont(QFont("Segoe UI", 15, QFont.Bold))
        label_titre.setStyleSheet("color: #2c3e50;")
        label_titre.setAlignment(Qt.AlignCenter)
        line1.addWidget(label_titre)

        # Nombre
        label_nombre = QLabel(str(nombre))
        label_nombre.setFont(QFont("Segoe UI", 28, QFont.Bold))
        label_nombre.setStyleSheet(f"color: {couleur};")
        label_nombre.setAlignment(Qt.AlignCenter)
        line2.addWidget(label_nombre)
        layout.addLayout(line1)
        layout.addLayout(line2)
        

from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Statistiques avec Logos")
        self.setMinimumSize(700, 300)

        container = QWidget()
        layout = QVBoxLayout(container)

        # Cadre principal contenant les statistiques
        frame_stats = QFrame()
        frame_stats.setStyleSheet("background-color: #f5f5f5; border-radius: 10px;")
        frame_layout = QHBoxLayout(frame_stats)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(20)

        # Cartes de statistiques avec logos
        carte1 = StatistiqueCard("Patients", 124, "#3498db", "pati.png")
        carte2 = StatistiqueCard("Médecins", 12, "#9b59b6", "icons/medecin.png")
        carte3 = StatistiqueCard("Rendez-vous", 48, "#e67e22", "icons/calendar.png")

        frame_layout.addWidget(carte1)
        frame_layout.addWidget(carte2)
        frame_layout.addWidget(carte3)

        layout.addWidget(frame_stats)
        self.setCentralWidget(container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
