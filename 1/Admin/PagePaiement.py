from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea,
    QHBoxLayout, QFrame, QSizePolicy, QLineEdit
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from Accueil.CustomPopup import CustomPopup
import sys
import requests
from Admin.Addpai import AddPaiement
from Admin.editPay import EDIT_Paiement


class PagePaiement(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #f0f4f8;")
        layout = QVBoxLayout(self)

        # Titre
        titre = QLabel("Gestion des Paiement")
        titre.setFont(QFont("Segoe UI", 20, QFont.Bold))
        titre.setStyleSheet("color: #004d40; margin: 20px 10px;")
        layout.addWidget(titre)

        # Barre de recherche + Refresh dans une ligne
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par nom ou prénom...")
        self.search_input.setStyleSheet("""
    QLineEdit {
        padding: 6px;
        border: 1px solid #cccccc;
        border-radius: 8px;
        background-color: white;
        margin: 5px;
    }
""")
        self.search_input.textChanged.connect(self.filtrerPaiements)
        search_layout.addWidget(self.search_input)

        btn_filtre = QPushButton("Refresh")
        btn_filtre.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: #eeeeee;
                font-weight: bold;
                border-radius: 10px;
                margin-right: 15px;
            }
            QPushButton:hover {
                background-color: #cccccc;
            }
        """)
        btn_filtre.clicked.connect(self.refresh)
        search_layout.addWidget(btn_filtre)
        layout.addLayout(search_layout)

        # Zone de scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
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

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

        # Bouton Ajouter en bas de page
        self.btn_ajouter = QPushButton("Ajouter un nouveau paiement")
        self.btn_ajouter.clicked.connect(self.ajout_pat)
        self.btn_ajouter.setStyleSheet("""
            QPushButton {
                padding: 12px;
                background-color: #00796b;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                margin: 15px;
            }
            QPushButton:hover {
                background-color: #004d40;
            }
        """)
        self.btn_ajouter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.btn_ajouter)

        self.paiement = []
        self.paiement_filtré = []

        self.chargerPaiement()
        self.afficherPaiement()


    def afficherPaiement(self):
        # Nettoyer les anciens widgets
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Afficher uniquement les paiements filtrés
        for pat in self.paiement_filtré:
            item_widget = QFrame()
            item_widget.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 12px;
                    padding: 10px;
                    margin: 8px;
                }
            """)
            item_widget.setMinimumHeight(100)
            main_layout = QHBoxLayout(item_widget)
            main_layout.setContentsMargins(10, 10, 10, 10)
            main_layout.setSpacing(20)

            statut = (
                "<span style='color: green; font-weight: bold;'>✅ Effectué</span>"
                if pat.get("paiement_effectue", 0) == 1 else
                "<span style='color: red; font-weight: bold;'>❌ Non effectué</span>"
            )

            texte = (
                f"<b>Nom :</b> {pat['prenom']} {pat['nom']}<br>"
                f"<b>Date :</b> {pat['date_paiement']}<br>"
                f"<b>Montant :</b> {pat['montant']} MAD<br>"
                f"<b>Statut :</b> {statut}"
            )

            label = QLabel(texte)
            label.setFont(QFont("Segoe UI", 10))
            label.setWordWrap(True)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            main_layout.addWidget(label)

            bouton_layout = QHBoxLayout()

            

            btn_modifier = QPushButton("Modifier")
            btn_modifier.clicked.connect(lambda checked, i=pat['id_paiement']: self.edit(i))
            btn_modifier.setFixedWidth(100)
            btn_modifier.setStyleSheet("""
                QPushButton {
                    background-color: #fbc02d;
                    color: black;
                    border-radius: 6px;
                    padding: 8px 12px;
                }
                QPushButton:hover {
                    background-color: #f9a825;
                }
            """)
            bouton_layout.addWidget(btn_modifier)

            btn_supprimer = QPushButton(" Supprimer")
            btn_supprimer.clicked.connect(lambda checked, i=pat['id_paiement']: self.delete(i))
            btn_supprimer.setFixedWidth(100)
            btn_supprimer.setStyleSheet("""
                QPushButton {
                    background-color: #e53935;
                    color: white;
                    border-radius: 6px;
                    padding: 8px 12px;
                }
                QPushButton:hover {
                    background-color: #b71c1c;
                }
            """)
            bouton_layout.addWidget(btn_supprimer)

            bouton_container = QWidget()
            bouton_container.setLayout(bouton_layout)
            bouton_container.setStyleSheet("background-color: transparent")
            main_layout.addWidget(bouton_container, alignment=Qt.AlignRight | Qt.AlignVCenter)

            self.scroll_layout.addWidget(item_widget)

    def chargerPaiement(self):
        try:
            url = "http://127.0.0.1:5000/charger_paiement"
            resultats = requests.get(url)
            if resultats.status_code == 200:
                self.paiement = resultats.json()
                self.paiement_filtré = self.paiement.copy()
            else:
                self.popup = CustomPopup(popup_type="error", message="Impossible de récupérer les paiements !")
                self.popup.show_centered(self)
                self.paiement = []
                self.paiement_filtré = []
        except Exception as e:
            self.popup = CustomPopup(popup_type="error", message=f"Erreur réseau : {e}")
            self.popup.show_centered(self)
            self.paiement = []
            self.paiement_filtré = []

    def filtrerPaiements(self, texte):
        texte = texte.lower().strip()
        if not texte:
            self.paiement_filtré = self.paiement.copy()
        else:
            self.paiement_filtré = [
                p for p in self.paiement
                if texte in p['nom'].lower() or texte in p['prenom'].lower()
            ]
        self.afficherPaiement()

    def delete(self, index):
        try:
            url = f"http://127.0.0.1:5000/delete_pai?index={index}"
            response = requests.get(url)
            if response.status_code == 200:
                self.popup = CustomPopup(popup_type="success", message="Paiement supprimé!")
                self.popup.show_centered(self)
                self.refresh()
            else:
                self.popup = CustomPopup(popup_type="error", message="Erreur lors de la suppression !")
                self.popup.show_centered(self)
        except Exception as e:
            self.popup = CustomPopup(popup_type="error", message="Erreur réseau")
            self.popup.show_centered(self)

    def ajout_pat(self):
        self.addpai_window = AddPaiement()
        self.addpai_window.setWindowModality(Qt.ApplicationModal)
        self.addpai_window.setAttribute(Qt.WA_DeleteOnClose)
        self.addpai_window.destroyed.connect(self.reagir_fermeture_mod)
        self.addpai_window.show()

    def reagir_fermeture_mod(self, obj):
        try:
            if hasattr(self, 'addpai_window') and self.addpai_window.ajout_effect:
                self.popup = CustomPopup(popup_type="success", message="Paiement ajouté avec succès !")
                self.popup.show_centered(self)
                self.refresh()
            if hasattr(self, 'editt') and self.editt.ajout_effect:
                self.refresh()
        except AttributeError:
            pass

    def refresh(self):
        self.chargerPaiement()
        self.afficherPaiement()

    def edit(self, index):
        self.editt = EDIT_Paiement(index)
        self.editt.show()
        self.editt.setWindowModality(Qt.ApplicationModal)
        self.editt.setAttribute(Qt.WA_DeleteOnClose)
        self.editt.destroyed.connect(self.reagir_fermeture_mod)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PagePaiement()
    window.show()
    sys.exit(app.exec())
