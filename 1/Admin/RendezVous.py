from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea,
    QHBoxLayout, QMessageBox, QFrame, QSizePolicy, QLineEdit, QComboBox
)
from PySide6.QtGui import QFont
from PySide6.QtCore import QDateTime, Qt
import sys
import requests
from datetime import datetime
from email.utils import parsedate_to_datetime
from Admin.Addren import AddRendezVous
from Admin.editrdv import ModifierRendezVous
from Accueil.CustomPopup import CustomPopup
class PageRendezVous(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #f0f4f8;")
        layout = QVBoxLayout(self)

        # Titre
        titre = QLabel("Gestion des Rendez-vous")
        titre.setFont(QFont("Segoe UI", 20, QFont.Bold))
        titre.setStyleSheet("color: #004d40; margin: 20px 10px;")
        layout.addWidget(titre)

        # Recherche et filtre
        recherche_filtre_layout = QHBoxLayout()

        self.input_recherche = QLineEdit()
        self.input_recherche.setPlaceholderText("Rechercher par patient ou médecin")
        self.input_recherche.textChanged.connect(self.filtrer_et_afficher)
        self.input_recherche.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: white;
            }
        """)
        recherche_filtre_layout.addWidget(self.input_recherche)

        self.combo_filtre = QComboBox()
        self.combo_filtre.addItems(["Tous", "Ce jour", "Ce mois", "Dernier mois"])
        self.combo_filtre.currentIndexChanged.connect(self.filtrer_et_afficher)
        self.combo_filtre.setStyleSheet( """
             QComboBox, QDateEdit, QDoubleSpinBox {
            background-color: #ffffff;
            border: 1px solid #b0bec5;
            padding: 6px 8px;
            border-radius: 8px;
            font-size: 14px;
            min-height: 20px;
            color: #37474f;
        }
        QComboBox:hover, QDateEdit:hover, QDoubleSpinBox:hover {
            border: 2px solid #4db6ac;
            background-color: #f0f9f8;
        }
        QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus {
            border: 2px solid #00796b;
            background-color: #e0f2f1;
            color: #004d40;
        }
        QComboBox::drop-down, QDateEdit::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left: 1px solid #b0bec5;
            background-color: #e0f2f1;
        }
        QComboBox::down-arrow, QDateEdit::down-arrow {
            image: url(down_arrow_icon.png);
            width: 14px;
            height: 14px;
        }
        /* Cacher les flèches du QDoubleSpinBox */
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
            border: none;
            background: none;
            width: 0px;
            height: 0px;
        }
        """)
        recherche_filtre_layout.addWidget(self.combo_filtre)

        layout.addLayout(recherche_filtre_layout)

        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(""" QScrollArea {
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

        # Bouton ajouter
        self.btn_ajouter = QPushButton(" Programmer un nouveau rendez-vous")
        self.btn_ajouter.clicked.connect(self.ajouter_rdv)
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
        layout.addWidget(self.btn_ajouter)

        self.charger_rendez_vous()
        self.filtrer_et_afficher()

    def filtrer_et_afficher(self):
       
        filtre = self.combo_filtre.currentText()
        recherche = self.input_recherche.text().lower()

        
        now = datetime.now()
        rdvs_filtres = []
        for rdv in self.rendez_vous:
            try:
                date_rdv = datetime.strptime(rdv['date_heure'], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                date_rdv = now

            # Filtre date
            if filtre == "Ce jour":
                if date_rdv.date() != now.date():
                    continue
            elif filtre == "Ce mois":
                if date_rdv.year != now.year or date_rdv.month != now.month:
                    continue
            elif filtre == "Dernier mois":
                last_month = (now.month - 1) or 12
                year_check = now.year if now.month > 1 else now.year - 1
                if date_rdv.year != year_check or date_rdv.month != last_month:
                    continue
            # "Tous" ne filtre rien

            # Filtre recherche
            nom_patient = rdv.get("patient", "").lower()
            nom_docteur = rdv.get("medecin", "").lower()
            if recherche and recherche not in nom_patient and recherche not in nom_docteur:
                continue

            rdvs_filtres.append(rdv)
        self.refrech()
        self.afficher_rendez_vous(rdvs_filtres)

    def afficher_rendez_vous(self, rdvs=None):
        if rdvs is None:
            rdvs = self.rendez_vous

        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        statut_colors = {
            "Confirmé": "#27ae60",
            "Annulé": "#c0392b",
            "En attente": "#f39c12"
        }

        for index, rdv in enumerate(rdvs):
            try:
                date_str = datetime.strptime(rdv['date_heure'], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                date_str = datetime.now()

            nom_patient = rdv.get("patient", "Inconnu")
            nom_docteur = rdv.get("medecin", "Inconnu")
            statut = rdv.get("statut", "Inconnu")

            item_widget = QFrame()
            item_widget.setFixedHeight(60)
            item_widget.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #ccc;
                    border-radius: 8px;
                }
            """)
            main_layout = QHBoxLayout(item_widget)
            main_layout.setContentsMargins(10, 5, 10, 5)
            main_layout.setSpacing(15)

            info_layout = QVBoxLayout()
            info_layout.setSpacing(2)

            line1 = QHBoxLayout()
            patient_label = QLabel(f" Patient : {nom_patient}")
            patient_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333; border:none;")
            medecin_label = QLabel(f" |  Dr. {nom_docteur}")
            medecin_label.setStyleSheet("font-size: 13px; color: #555; border:none;")
            line1.addWidget(patient_label)
            line1.addWidget(medecin_label)
            line1.addStretch()
            info_layout.addLayout(line1)

            line2 = QHBoxLayout()
            date_label = QLabel(f"Date & heure : {date_str.strftime('%d/%m/%Y %H:%M')}")
            date_label.setStyleSheet("font-size: 12px; color: #555; border:none;")

            color = statut_colors.get(statut, "#444")
            statut_label = QLabel(f"● {statut}")
            statut_label.setStyleSheet(f"font-size: 12px; color: {color}; border:none; padding-left: 15px;")

            line2.addWidget(date_label)
            line2.addWidget(statut_label)
            line2.addStretch()
            info_layout.addLayout(line2)

            main_layout.addLayout(info_layout)

            bouton_layout = QHBoxLayout()
            bouton_layout.setSpacing(5)

            btn_confirmer = QPushButton("Confirmer")
            btn_confirmer.setFixedWidth(90)
            btn_confirmer.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
                    color: white;
                    border-radius: 6px;
                    padding: 6px 10px;
                }
                QPushButton:hover {
                    background-color: #388e3c;
                }
            """)
            btn_confirmer.setEnabled(statut != "Annulé")
            btn_confirmer.clicked.connect(lambda checked, i=index: self.changer_statut(i, "Confirmé"))
            bouton_layout.addWidget(btn_confirmer)

            btn_annuler = QPushButton("Annuler")
            btn_annuler.setFixedWidth(90)
            btn_annuler.setStyleSheet("""
                QPushButton {
                    background-color: #e53935;
                    color: white;
                    border-radius: 6px;
                    padding: 6px 10px;
                }
                QPushButton:hover {
                    background-color: #b71c1c;
                }
            """)
            btn_annuler.setEnabled(statut != "Annulé")
            btn_annuler.clicked.connect(lambda checked, i=index: self.changer_statut(i, "Annulé"))
            bouton_layout.addWidget(btn_annuler)

            btn_modifier = QPushButton("Modifier")
            btn_modifier.setFixedWidth(90)
            btn_modifier.setStyleSheet("""
                QPushButton {
                    background-color: #fbc02d;
                    color: black;
                    border-radius: 6px;
                    padding: 6px 10px;
                }
                QPushButton:hover {
                    background-color: #f9a825;
                }
            """)
            # Pour la modif on utilise l'id_rdv du rdv filtré (important)
            btn_modifier.clicked.connect(lambda checked, i=rdv['id_rdv']: self.modifier_rdv(i))
            bouton_layout.addWidget(btn_modifier)

            bouton_container = QWidget()
            bouton_container.setStyleSheet("background-color:transparent")
            bouton_container.setLayout(bouton_layout)
            bouton_container.setMinimumHeight(50)
            main_layout.addWidget(bouton_container, alignment=Qt.AlignRight | Qt.AlignVCenter)

            self.scroll_layout.addWidget(item_widget)

    

    def modifier_rdv(self, id_rdv):
        self.form = ModifierRendezVous(id_rdv)
        self.form.show()

    def ajouter_rdv(self):
        self.form = AddRendezVous()
        self.form.setWindowModality(Qt.ApplicationModal)
        self.form.setAttribute(Qt.WA_DeleteOnClose)
        self.form.destroyed.connect(self.reagir_fermeture_mod)
        self.form.show()

    def charger_rendez_vous(self):
        # Toujours charger tous les rendez-vous
        try:
            url = f"http://127.0.0.1:5000/rendezvous?filtre=tous"
            response = requests.get(url)
            if response.status_code == 200:
                self.rendez_vous = response.json()
            else:
                self.popup = CustomPopup(popup_type="error", message="Impossible de récupérer les rendez-vous !")
                self.popup.show_centered(self)
                self.rendez_vous = []
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur réseau : {e}")
            self.rendez_vous = []
    def changer_statut(self, index, nouveau_statut):
        rdv = self.rendez_vous[index]
        id_rdv = rdv['id_rdv']

    # Préparer les données à envoyer
        data = {
        "id_rdv": id_rdv,
        "statut": nouveau_statut
        }

        try:
            url = f"http://127.0.0.1:5000/rendezvous/{id_rdv}/statut"  # Exemple d'endpoint
            response = requests.put(url, json=data)

            if response.status_code == 200:
            # Mise à jour locale
                self.rendez_vous[index]['statut'] = nouveau_statut
                self.filtrer_et_afficher()
                self.refrech()
            else:
                self.popup = CustomPopup(popup_type="error", message="Impossible de mettre à jour le statut du rendez-vous !")
                self.popup.show_centered(self)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur réseau : {e}")
    def refrech(self):
        self.charger_rendez_vous()
        self.mettreAJourVue()

    def mettreAJourVue(self):
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.afficher_rendez_vous()
    def reagir_fermeture_mod(self, obj):
        try:
            if hasattr(self, 'addpai_window') and self.addpai_window.ajout_effect:
                self.popup = CustomPopup(popup_type="success", message="Rendez-vous ajouté avec succès !")
                self.popup.show_centered(self)
                self.refrech()
            if hasattr(self, 'editt') and self.editt.ajout_effect:
                self.refresh()
        except AttributeError:
            pass