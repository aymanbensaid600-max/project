from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QStackedWidget, QHBoxLayout, QVBoxLayout, QFrame, QCheckBox, QGraphicsOpacityEffect
)
from Admin.PageAccueil import PageAccueil
from Admin.Docteur import PageMedecin
from Admin.RendezVous import PageRendezVous
from Admin.Pagepatient import PagePatient
from Admin.PagePaiement import PagePaiement
from PySide6.QtGui import QFont, QPixmap, QIcon
from PySide6.QtCore import Qt,QSize
from Admin.sttat import PageStatistique

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("dashadmin")
        self.setMinimumSize(1000, 600)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Partie de navigation
        self.Q_navig = QFrame()
        self.Q_navig.setStyleSheet("border-top-right-radius: 10px; border-bottom-right-radius: 10px; background-color: #00796b;")
        self.Qnavig = QVBoxLayout(self.Q_navig)
        self.Qnavig.setSpacing(3) 
        self.Qnavig.setContentsMargins(0, 0, 0, 160) 
        
        buttons = [
        ("Accueil", "home.png", 0),
        ("Patient", "pati.png", 3),
        ("Medcin", "med.png", 1),
        ("rendez-vous", "rend.png", 2),
        ("Statistique", "stat.png", 5),
        ("Paiement","paiement.png",4)
        ]

        for text, icon, index in buttons:
            self.Qnavig.addWidget(self.create_button(text, icon, index))

        

        
          # --- Contenu principal ---
        self.stack = QStackedWidget()
        self.stack.addWidget(PageAccueil())       
        self.stack.addWidget(PageMedecin())       
        self.stack.addWidget(PageRendezVous())
        self.stack.addWidget(PagePatient())
        self.stack.addWidget(PagePaiement())
        self.stack.addWidget(PageStatistique())

        main_layout.addWidget(self.Q_navig, 1)
        main_layout.addWidget(self.stack, 7)
        
    def create_button(self,label, icon_path, index):
        btn = QPushButton(f"  {label}")
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(QSize(20, 20)) 
        btn.setStyleSheet("""
            QPushButton {
                    background-color: transparent;
                    color: white;
                    padding: 15px;
                    text-align: left;
                    font:15px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #1c3b52;
                    font: bold 14px;
                }
            """)
        btn.clicked.connect(lambda: self.stack.setCurrentIndex(index))
        return btn



    def closeEvent(self, event):
        """ Cette méthode est appelée lorsque la fenêtre est fermée (via le X) """
        QApplication.quit()  # Cela ferme l'application lorsque l'utilisateur ferme la fenêtre
        event.accept()  # Accepte l'événement de fermeture de la fenêtre

