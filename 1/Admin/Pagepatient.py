from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea,
    QHBoxLayout, QMessageBox, QFrame, QSizePolicy,QLineEdit
)
from PySide6.QtGui import QFont
from PySide6.QtCore import QDateTime, Qt
from Accueil.CustomPopup import CustomPopup
import requests
from Admin.Addpat import Addpat
from Admin.Modifie import Modifie
from Admin.Historique import HistoriquePatient

class PagePatient(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #f0f4f8;")
        layout = QVBoxLayout(self)

        # Titre
        titre = QLabel("Gestion des Patient")
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
        self.search_input.textChanged.connect(self.filtrerPatients)
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
        btn_filtre.clicked.connect(self.refrech)
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
        self.btn_ajouter = QPushButton("Ajouter un nouveau patient")
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

        # Chargement initial
        self.patient = []
        self.filtres_patients = []
        self.chargerPatient()
        self.afficherPatient()

    def afficherPatient(self):
        for pat in self.filtres_patients:
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

            texte = (
                f"<b>{pat['prenom']} {pat['nom']}</b> | "
                f"Né(e) le {pat['date_naissance']}<br>"
                f"{pat['telephone']} | {pat['email']}"
            )

            label = QLabel(texte)
            label.setFont(QFont("Segoe UI", 10))
            label.setWordWrap(True)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            main_layout.addWidget(label)

            bouton_layout = QHBoxLayout()

            btn_consulter = QPushButton("Consulter historique")
            btn_consulter.clicked.connect(lambda _, i=pat['id_patient']: self.consulte(i))
            btn_consulter.setFixedWidth(140)
            btn_consulter.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
                    color: white;
                    border-radius: 6px;
                    padding: 8px 12px;
                }
                QPushButton:hover {
                    background-color: #388e3c;
                }
            """)
            bouton_layout.addWidget(btn_consulter)

            btn_supprimer = QPushButton("Supprimer")
            btn_supprimer.clicked.connect(lambda _, i=pat['id_patient']: self.delete(i))
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

            btn_modifier = QPushButton("Modifier")
            btn_modifier.clicked.connect(lambda _, i=pat['id_patient']: self.modifie(i))
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

            bouton_container = QWidget()
            bouton_container.setStyleSheet("background-color:transparent")
            bouton_container.setLayout(bouton_layout)
            bouton_container.setMinimumHeight(50)
            main_layout.addWidget(bouton_container, alignment=Qt.AlignRight | Qt.AlignVCenter)

            self.scroll_layout.addWidget(item_widget)

    def chargerPatient(self):
        try:
            url = "http://127.0.0.1:5000/Affiche"
            result = requests.get(url)
            if result.status_code == 200:
                self.patient = result.json()
                self.filtres_patients = self.patient.copy()
            else:
                self.popup = CustomPopup(popup_type="error", message="Impossible de récupérer les patients !")
                self.popup.show_centered(self)
                self.patient = []
                self.filtres_patients = []
        except Exception as e:
            self.popup = CustomPopup(popup_type="error", message=f"Erreur réseau : {e}")
            self.popup.show_centered(self)
            self.patient = []
            self.filtres_patients = []

    def ajout_pat(self):
        self.addpat_window = Addpat()
        self.addpat_window.setWindowModality(Qt.ApplicationModal)
        self.addpat_window.setAttribute(Qt.WA_DeleteOnClose)
        self.addpat_window.destroyed.connect(self.reagir_fermeture_addpat)
        self.addpat_window.show()

    def reagir_fermeture_addpat(self, _):
        try:
            if getattr(self.addpat_window, 'ajout_effectue', False):
                self.popup = CustomPopup(popup_type="success", message="Patient ajouté avec succès !")
                self.popup.show_centered(self)
            self.refrech()
        except AttributeError:
            pass

    def modifie(self, index):
        self.modifier = Modifie(index)
        self.modifier.setWindowModality(Qt.ApplicationModal)
        self.modifier.setAttribute(Qt.WA_DeleteOnClose)
        self.modifier.destroyed.connect(self.reagir_fermeture_mod)
        self.modifier.show()

    def reagir_fermeture_mod(self, _):
        try:
            if getattr(self.modifier, 'ajout_effectu', False):
                self.popup = CustomPopup(popup_type="success", message="Patient modifié avec succès !")
                self.popup.show_centered(self)
            self.refrech()
        except AttributeError:
            pass

    def delete(self, index):
        confirmation = QMessageBox.question(
        self,
        "Confirmation",
        "Êtes-vous sûr de vouloir supprimer ce patient ?",
        QMessageBox.Yes | QMessageBox.No
        )
    
        if confirmation == QMessageBox.Yes:
            try:
                url = f"http://127.0.0.1:5000/DeletePatient?index={index}"
                response = requests.get(url)
                if response.status_code == 200:
                    self.popup = CustomPopup(popup_type="success", message="Patient supprimé !")
                    self.popup.show_centered(self)
                    self.refrech()
                else:
                    self.popup = CustomPopup(popup_type="error", message="Erreur lors de la suppression !")
                    self.popup.show_centered(self)
            except Exception:
                self.popup = CustomPopup(popup_type="error", message="Erreur réseau")
                self.popup.show_centered(self)


    def refrech(self):
        self.chargerPatient()
        self.mettreAJourVue()

    def mettreAJourVue(self):
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.afficherPatient()

    def filtreTexte(self):
        return self.search_input.text().strip().lower()

    def filtrerPatients(self):
        texte = self.filtreTexte()
        if texte == "":
            self.filtres_patients = self.patient
        else:
            self.filtres_patients = [
                p for p in self.patient
                if texte in p['nom'].lower() or texte in p['prenom'].lower()
            ]
        self.mettreAJourVue()

    def consulte(self, index):
        self.con = HistoriquePatient(index)
        self.con.show()