from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QFrame, QHBoxLayout,
    QPushButton, QGraphicsDropShadowEffect, QScrollArea, QSizePolicy
)
from PySide6.QtGui import QColor, QFont
from Admin.MedecinCard import MedecinCard
from Admin.RendezVousCard import RendezVousCard  # <-- Import ajouté
from datetime import datetime
import requests
from Accueil.CustomPopup import CustomPopup
from Admin.Statcard import StatistiqueCard
class PageAccueil(QWidget):
    def __init__(self):
        super().__init__()

        # === Layout principal ===
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # === Barre de titre ===
        self.frame_top = QFrame()
        self.frame_top.setStyleSheet(" border-radius: 10px;")
        self.frame_top.setGraphicsEffect(self.create_shadow())
        self.title_layout = QVBoxLayout(self.frame_top)
        
        self.label = QLabel("Page d'Accueil")
        self.label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.label.setStyleSheet("color: #2c3e50; margin: 10px;")
        self.title_layout.addWidget(self.label)
        self.layout.addWidget(self.frame_top, 1)

        # === Contenu principal ===
        self.frame_bottom = QFrame()
        self.frame_bottom.setStyleSheet("background-color: #f5f5f5;")
        self.fram_layout = QHBoxLayout(self.frame_bottom)

        # === Colonne gauche ===
        self.act_act = QFrame()
        self.act_layout = QVBoxLayout(self.act_act)

        # === Section "Nos Médecins" ===
        self.first_med = QFrame()
        self.first_med.setStyleSheet(" border-radius: 10px;")
        self.first_med.setGraphicsEffect(self.create_shadow())
        self.first_med_lay = QVBoxLayout(self.first_med)

        self.title_label = QLabel("Nos Médecins")
        self.title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.title_label.setStyleSheet("color: #34495e; margin-bottom: 10px;")
        self.first_med_lay.addWidget(self.title_label)

        # === Données médecins ===
        self.chargerMed()
        self.load_summary()
        for med in self.med:
            card = MedecinCard(
                nom=med["nom"],
                prenom=med["prenom"],
                specialite=med["specialite"],
                horaires=med["horaires"],
                disponibilite=med["disponibilite"]
            )
            self.first_med_lay.addWidget(card)

        self.view_all_button = QPushButton("Voir tout")
        self.view_all_button.setFlat(True)
        self.view_all_button.setFont(QFont("Segoe UI", 10))
        self.view_all_button.setStyleSheet("color: #1abc9c; border: none;")
        self.first_med_lay.addWidget(self.view_all_button)

        scroll_first_med = QScrollArea()
        scroll_first_med.setWidgetResizable(True)
        scroll_first_med.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f5f5f5;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 12px;
                margin: 2px 0 2px 0;
            }
            QScrollBar::handle:vertical {
                background: #80cbc4;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4db6ac;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        scroll_first_med.setWidget(self.first_med)
        scroll_first_med.setMaximumHeight(400)
        scroll_first_med.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.act_layout.addWidget(scroll_first_med, 1)

        # === Section "Rendez-vous à venir" ===
        self.second_red = QFrame()
        self.second_red.setStyleSheet(" border-radius: 10px;")
        self.second_red.setGraphicsEffect(self.create_shadow())
        self.second_red_lay = QVBoxLayout(self.second_red)

        self.title_label2 = QLabel("Rendez-vous à venir")
        self.title_label2.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.title_label2.setStyleSheet("color: #34495e; margin-bottom: 10px;")
        self.second_red_lay.addWidget(self.title_label2)

        # === Données rendez-vous ===
        self.charger_rendez_vous()

        for index,rdv in enumerate(self.rendez_vous):
            if index<4:
                card = RendezVousCard(
                id_rdv=rdv["id_rdv"],
                nom_patient=rdv["patient"],
                nom_docteur=rdv["medecin"],
                date_heure=rdv["date_heure"],
                statut=rdv["statut"]
            )
            else:
                break
            self.second_red_lay.addWidget(card)

        scroll_second_red = QScrollArea()
        scroll_second_red.setWidgetResizable(True)
        scroll_second_red.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f5f5f5;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 12px;
                margin: 2px 0 2px 0;
            }
            QScrollBar::handle:vertical {
                background: #80cbc4;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4db6ac;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        scroll_second_red.setWidget(self.second_red)
        scroll_second_red.setMaximumHeight(400)
        scroll_second_red.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.act_layout.addWidget(scroll_second_red, 1)

        # === Cadre à droite ===
        self.act_med = QWidget()
        self.act_med.setStyleSheet("background-color:transparent")
        self.act_medl=QVBoxLayout(self.act_med)
        carte1 = StatistiqueCard("Patients",  self.pati, "#3498db", "pa.png")
        carte2 = StatistiqueCard("Médecins", self.medi, "#9b59b6", "icons/medecin.png")
        carte3 = StatistiqueCard("Rendez-vous", self.apoi, "#e67e22", "icons/calendar.png")

        self.act_medl.addWidget(carte1)
        self.act_medl.addWidget(carte2)
        self.act_medl.addWidget(carte3)
        

        self.fram_layout.addWidget(self.act_act, 2)
        self.fram_layout.addWidget(self.act_med, 1)

        # Ajout final
        self.layout.addWidget(self.frame_bottom, 6)

    def create_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 60))
        return shadow
    def charger_rendez_vous(self, filtre="mois"):
        try:
            url = f"http://127.0.0.1:5000/rendezvous?filtre={filtre}"
            response = requests.get(url)
            if response.status_code == 200:
                self.rendez_vous = response.json()
            else:
                 self.popup = CustomPopup(popup_type="error", message="Impposible de récupérer les rendez-vous  !")
                 self.popup.show_centered(self)
                 self.rendez_vous = []
        except Exception as e:
            self.popup = CustomPopup(popup_type="error", message=f"Erreur réseau : {e}")
            self.popup.show_centered(self)
            self.rendez_vous = []
    def chargerMed(self):
        try:
            url = "http://127.0.0.1:5000/AfficheMed"
            resultas = requests.get(url)
            if resultas.status_code == 200:
                self.med = resultas.json()
            else:
                self.popup = CustomPopup(popup_type="error", message="Impossible de récupérer les médecins !")
                self.popup.show_centered(self)
                self.med = []
        except Exception as e:
            self.popup = CustomPopup(popup_type="error", message=f"Erreur réseau : {e}")
            self.popup.show_centered(self)
            self.med = []
    def load_summary(self):
        url = "http://localhost:5000/api/stats/summary"
        try:
            response = requests.get(url)
            if response.ok:
                data = response.json()
                self.pati=data['total_patients']
                self.medi=data['total_doctors']
                self.apoi=data['total_appointments']
                
                total_ca = float(data['total_ca']) if data['total_ca'] else 0.0
                self.dat=f"{total_ca:.2f} €"
        except Exception as e:
            print("Erreur load_summary:", e)