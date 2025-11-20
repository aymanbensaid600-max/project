from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QStackedWidget,
    QHBoxLayout, QVBoxLayout, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QFont, QIcon, QPixmap, QMouseEvent
from PySide6.QtCore import Qt, QSize, QPoint
import sys
import requests
from Accueil.CustomPopup import CustomPopup
from med.accueilmed import AccueilMedecin  # Au lieu de AccueilPatient # Remplace par ta classe réelle
from med.rdv import MesRendezVousMedecin
from med.patmed import MesPatients
class MedecinDash(QWidget):
    def __init__(self, id=None):
        super().__init__()
        self.index = id or "Nom Patient"
        self.setWindowTitle("Dashboard Patient")
        self.resize(1000, 600)
        self.med = {}  # Initialisation vide
        self.chargerinfo()  # Charger les infos du patient depuis le backend

        # Navigation latérale
        self.Q_navig = QFrame()
        self.Q_navig.setStyleSheet("""
            border-top-right-radius: 10px;
            border-bottom-right-radius: 10px;
            background-color: #00796b;
        """)
        self.Q_navig.setMinimumWidth(150)
        self.Q_navig.setMaximumWidth(180)

        self.Qnavig = QVBoxLayout(self.Q_navig)
        self.Qnavig.setSpacing(10)
        self.Qnavig.setContentsMargins(0, 20, 0, 10)

        # Section Profil
        self.profile_clickable = QWidget()
        profile_layout = QVBoxLayout(self.profile_clickable)
        profile_layout.setContentsMargins(0, 0, 0, 0)
        profile_layout.setSpacing(5)

        icon = QLabel()
        icon.setPixmap(QPixmap("profi.png").scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon.setAlignment(Qt.AlignCenter)
        profile_layout.addWidget(icon)

        label_nom = QLabel(f"{self.med.get('nom', '')} {self.med.get('prenom', '')}")
        label_nom.setFont(QFont("Arial", 13, QFont.Bold))
        label_nom.setStyleSheet("color: white;")
        label_nom.setAlignment(Qt.AlignCenter)
        profile_layout.addWidget(label_nom)

        self.profile_clickable.mousePressEvent = self.toggle_profil_menu
        self.Qnavig.addWidget(self.profile_clickable)

        # Boutons de navigation
        self.Qnavig.addWidget(self.create_button("Accueil", "home.png", 0))
        self.Qnavig.addSpacerItem(QSpacerItem(0, 5, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.Qnavig.addWidget(self.create_button("Mes Rendez-vous", "rend.png", 1))
        self.Qnavig.addSpacerItem(QSpacerItem(0, 5, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.Qnavig.addWidget(self.create_button("Mes patients", "paiement.png", 2))
        self.Qnavig.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Menu popup (indépendant)
        self.menu_profil = QFrame(None, Qt.Popup)
        self.menu_profil.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 6px;
            }
            QPushButton {
                background-color: transparent;
                padding: 6px 12px;
                text-align: left;
                font-size: 13px;
                color: #00796b;
            }
            QPushButton:hover {
                background-color: #e0f2f1;
                color: #004d40;
            }
        """)
        layout_popup = QVBoxLayout(self.menu_profil)
        layout_popup.setContentsMargins(5, 5, 5, 5)

        btn_profil = QPushButton("Gérer le profil")
        btn_profil.clicked.connect(self.gerer_profil)
        layout_popup.addWidget(btn_profil)

        btn_logout = QPushButton("Se déconnecter")
        btn_logout.clicked.connect(self.deconnecter)
        layout_popup.addWidget(btn_logout)

        # Contenu principal
        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.stack.addWidget(AccueilMedecin(self.index))
        self.stack.addWidget(MesRendezVousMedecin(self.index))
        self.stack.addWidget(MesPatients(self.index))
    # Page Paiement
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.Q_navig)
        main_layout.addWidget(self.stack)
       
    def create_button(self, label, icon_path, index):
        btn = QPushButton(f"  {label}")
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(QSize(20, 20))
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                padding: 12px;
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

    def toggle_profil_menu(self, event: QMouseEvent):
        if self.menu_profil.isVisible():
            self.menu_profil.hide()
        else:
            global_pos = self.profile_clickable.mapToGlobal(QPoint(0, self.profile_clickable.height()))
            self.menu_profil.move(global_pos)
            self.menu_profil.show()

    def gerer_profil(self):
        print("Accès à la gestion du profil...")

    def deconnecter(self):
        print("Déconnexion...")
        QApplication.quit()

    def closeEvent(self, event):
        QApplication.quit()
        event.accept()
    def chargerinfo(self):
        try:
            url = f"http://127.0.0.1:5000/charger_med?id_med={self.index}"  # nom du paramètre corrigé
            response = requests.get(url)
            if response.status_code == 200:
                self.med= response.json()
            else:
                self.patient = {"nom": "Inconnu", "prenom": ""}
                self.popup = CustomPopup(popup_type="error", message="Impossible de récupérer les données du patient !")
                self.popup.show_centered(self)
        except Exception as e:
            self.med = {"nom": "Erreur", "prenom": ""}
            self.popup = CustomPopup(popup_type="error", message=f"Erreur réseau : {e}")
            self.popup.show_centered(self)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MedecinDash(id="1")
    window.show()
    sys.exit(app.exec())
