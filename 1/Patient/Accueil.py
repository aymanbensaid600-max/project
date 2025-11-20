from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QListWidget,
    QListWidgetItem, QTextEdit
)
from PySide6.QtGui import QFont, QColor, QPalette
from PySide6.QtCore import Qt
import requests
from PySide6.QtWidgets import QApplication
import sys
class PageAccueil(QWidget):
    def __init__(self, id_patient):
        super().__init__()
        self.id_patient = id_patient
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f0f4f5"))
        self.setPalette(palette)

        self.init_ui()
        self.charger_donnees()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # Titre principal
        self.label_bienvenue = QLabel("👋 Bienvenue dans votre espace personnel")
        self.label_bienvenue.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.label_bienvenue.setStyleSheet("color: #004d40;")
        self.label_bienvenue.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_bienvenue)

        # Cartes de sections
        self.section_rdv = self.creer_carte("📅 Prochains rendez-vous")
        self.liste_rdv = QListWidget()
        self.liste_rdv.setStyleSheet(self.liste_style())
        self.section_rdv.layout().addWidget(self.liste_rdv)
        layout.addWidget(self.section_rdv)

        self.section_suivi = self.creer_carte("🩺 Dernier suivi médical")
        self.suivi_text = QTextEdit()
        self.suivi_text.setReadOnly(True)
        self.suivi_text.setStyleSheet(self.liste_style())
        self.section_suivi.layout().addWidget(self.suivi_text)
        layout.addWidget(self.section_suivi)

        self.section_paiement = self.creer_carte("💳 Paiements en attente")
        self.liste_paiement = QListWidget()
        self.liste_paiement.setStyleSheet(self.liste_style())
        self.section_paiement.layout().addWidget(self.liste_paiement)
        layout.addWidget(self.section_paiement)

    def creer_carte(self, titre):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 15px;
                border: 1px solid #e0e0e0;
                padding: 15px;
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(12)

        titre_label = QLabel(titre)
        titre_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        titre_label.setStyleSheet("color: #333333;")
        layout.addWidget(titre_label)

        return frame

    def liste_style(self):
        return """
            QListWidget, QTextEdit {
                background-color: #f9f9f9;
                border-radius: 10px;
                border: 1px solid #dddddd;
                padding: 8px;
                font-size: 13px;
                font-family: Segoe UI;
                color: #444444;
            }
        """

    def charger_donnees(self):
        # Rendez-vous
        try:
            r = requests.get(f"http://127.0.0.1:5000/patient/rendezvous_prochains?id_patient={self.id_patient}")
            if r.status_code == 200 and r.json():
                for rdv in r.json():
                    item = QListWidgetItem(f"📅 {rdv['date']} à {rdv['heure']} avec Dr. {rdv['medecin']}")
                    self.liste_rdv.addItem(item)
            else:
                self.liste_rdv.addItem("Aucun rendez-vous à venir.")
        except:
            self.liste_rdv.addItem("Erreur lors du chargement des rendez-vous.")

        # Suivi médical
        try:
            r = requests.get(f"http://127.0.0.1:5000/patient/dernier_suivi?id_patient={self.id_patient}")
            if r.status_code == 200:
                data = r.json()
                texte = f"📆 Date : {data['date']}\n👨‍⚕️ Médecin : Dr. {data['medecin']}\n\n📝 Observations :\n{data['observation']}"
                self.suivi_text.setText(texte)
            else:
                self.suivi_text.setText("Aucun suivi trouvé.")
        except:
            self.suivi_text.setText("Erreur lors du chargement du suivi médical.")

        # Paiements en attente
        try:
            r = requests.get(f"http://127.0.0.1:5000/patient/paiements_non_effectues?id_patient={self.id_patient}")
            if r.status_code == 200 and r.json():
                for paiement in r.json():
                    self.liste_paiement.addItem(f"💰 {paiement['date']} - {paiement['montant']} MAD")
            else:
                self.liste_paiement.addItem("Aucun paiement en attente.")
        except:
            self.liste_paiement.addItem("Erreur lors du chargement des paiements.")
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Exemple avec un ID patient fictif = 1
    id_patient = 1
    fenetre = PageAccueil(id_patient)
    fenetre.setWindowTitle("Espace Patient")
    fenetre.resize(900, 650)
    fenetre.show()

    sys.exit(app.exec())