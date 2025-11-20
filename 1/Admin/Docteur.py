from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea,
    QHBoxLayout, QMessageBox, QFrame, QSizePolicy, QLineEdit
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from Accueil.CustomPopup import CustomPopup
import sys
import requests
from Admin.AddMedecin import AddMedecin
from Admin.ModifieMed import ModifieMedecin
from Admin.cal import CalendrierRendezVous
from datetime import datetime

class PageMedecin(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #f0f4f8;")
        layout = QVBoxLayout(self)

        # Titre
        titre = QLabel("Gestion des Medecin")
        titre.setFont(QFont("Segoe UI", 20, QFont.Bold))
        titre.setStyleSheet("color: #004d40; margin: 20px 10px;")
        layout.addWidget(titre)

        # Layout pour filtres et recherche
        filtre_layout = QHBoxLayout()
        
        # Barre de recherche
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Rechercher par nom, prénom ou spécialité...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: white;
            }
        """)
        self.search_bar.textChanged.connect(self.filtrer_medecins)
        filtre_layout.addWidget(self.search_bar)
        
        # Bouton Refresh
        btn_filtre = QPushButton("Refresh")
        btn_filtre.setStyleSheet("""
            QPushButton {
                background-color: #eeeeee;
                padding: 8px 16px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #cccccc;
            }
        """)
        btn_filtre.clicked.connect(self.refrech)
        filtre_layout.addWidget(btn_filtre)
        
        layout.addLayout(filtre_layout)

        # Scroll area
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

        # Bouton ajouter
        self.btn_ajouter = QPushButton(" Ajouter un nouveau medecin")
        self.btn_ajouter.clicked.connect(self.ajout_med)
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

        self.chargerMed()
        self.afficherMed()

    def afficherMed(self):
        for index, pat in enumerate(self.medecins_a_afficher):
            
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
            main_layout.setContentsMargins(10, 10, 10, 10)

          
            prenom = pat.get('prenom', 'N/A')
            nom = pat.get('nom', 'N/A')
            specialite = pat.get('specialite', 'Généraliste')  
            horaires = pat.get('horaires', 'Non défini')       
            disponibilite = self.est_en_service(horaires)
  

           
            info_layout = QVBoxLayout()
            info_layout.setSpacing(2)

          
            line1 = QHBoxLayout()
            nom_label = QLabel(f"Dr. {prenom} {nom}")
            nom_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333; border:none;")
            specialite_label = QLabel(f" | {specialite}")
            specialite_label.setStyleSheet("font-size: 13px; color: #555; border:none;")
            line1.addWidget(nom_label)
            line1.addWidget(specialite_label)
            line1.addStretch()
            info_layout.addLayout(line1)

            
            line2 = QHBoxLayout()
            horaires_label = QLabel(f"Horaires : {horaires}")
            horaires_label.setStyleSheet("font-size: 12px; color: #555; border:none;")
            statut_label = QLabel("🟢 En service" if disponibilite else "🔴 Absent")
            statut_label.setStyleSheet("font-size: 12px; color: #444; border:none; padding-left: 20px;")
            line2.addWidget(horaires_label)
            line2.addWidget(statut_label)
            line2.addStretch()
            info_layout.addLayout(line2)

           
            main_layout.addLayout(info_layout)

            
            bouton_layout = QHBoxLayout()

            btn_confirmer = QPushButton("Consulter rendez-vous")
            btn_confirmer.clicked.connect(lambda checked, i=pat['id_medecin']: self.consulte(i))
            btn_confirmer.setFixedWidth(140)
            btn_confirmer.setStyleSheet("""
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
            bouton_layout.addWidget(btn_confirmer)

            btn_annuler = QPushButton("Supprimer")
            btn_annuler.clicked.connect(lambda checked, i=pat['id_medecin']: self.delete(i))
            btn_annuler.setFixedWidth(100)
            btn_annuler.setStyleSheet("""
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
            bouton_layout.addWidget(btn_annuler)

            btn_modifier = QPushButton("Modifier")
            btn_modifier.clicked.connect(lambda checked, i=pat['id_medecin']: self.modifie(i))
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

    def chargerMed(self):
        try:
            url = "http://127.0.0.1:5000/AfficheMed"
            resultas = requests.get(url)
            if resultas.status_code == 200:
                self.med = resultas.json()
                self.medecins_a_afficher = self.med  # Liste initiale
            else:
                self.popup = CustomPopup(popup_type="error", message="Impossible de récupérer les médecins !")
                self.popup.show_centered(self)
                self.med = []
                self.medecins_a_afficher = []
        except Exception as e:
            self.popup = CustomPopup(popup_type="error", message=f"Erreur réseau : {e}")
            self.popup.show_centered(self)
            self.med = []
            self.medecins_a_afficher = []

    def ajout_med(self):
        self.addpat_window = AddMedecin()
        self.addpat_window.setWindowModality(Qt.ApplicationModal)
        self.addpat_window.setAttribute(Qt.WA_DeleteOnClose)
        self.addpat_window.destroyed.connect(self.reagir_fermeture_addpat)
        self.addpat_window.show()

    def reagir_fermeture_addpat(self, obj):
        try:
            if self.addpat_window.ajout_effectue:
                self.popup = CustomPopup(popup_type="success", message="Medecin ajouté avec succès !")
                self.popup.show_centered(self)

                # Recharger et rafraîchir la vue
                self.refrech()
        except AttributeError:
            pass  # Fenêtre supprimée avant lecture

    def delete(self, index):
        try:
            response = requests.delete(f"http://127.0.0.1:5000/DeleteMed?index={index}")
            if response.status_code == 200:
                self.popup = CustomPopup(popup_type="success", message="Médecin supprimé!")
                self.popup.show_centered(self)
                self.refrech()  # rafraîchir la liste après suppression
            else:
                self.popup = CustomPopup(popup_type="error", message="Erreur lors de la suppression !")
                self.popup.show_centered(self)
        except Exception as e:
            self.popup = CustomPopup(popup_type="error", message="Erreur réseau")
            self.popup.show_centered(self)

    def refrech(self):
        self.chargerMed()
        self.filtrer_medecins(self.search_bar.text())  # Réappliquer le filtre actuel
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.afficherMed()

    def modifie(self, index):
        self.modifier = ModifieMedecin(index, parent=self)
        self.modifier.show()
    
    def consulte(self,index):
        self.modifier =CalendrierRendezVous(index)
        self.modifier.show()  
    
    def filtrer_medecins(self, texte):
        """Filtre la liste des médecins en fonction du texte saisi"""
        texte = texte.lower()
        if not texte:
            self.medecins_a_afficher = self.med
        else:
            self.medecins_a_afficher = [
                med for med in self.med
                if (texte in med.get('nom', '').lower() or
                    texte in med.get('prenom', '').lower() or
                    texte in med.get('specialite', '').lower())
            ]
        
        # Rafraîchir l  'affichage
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.afficherMed()
            
   
    def est_en_service(self, horaire):
    
        jours_map = {
        "lun": 0, "mar": 1, "mer": 2, "jeu": 3,
        "ven": 4, "sam": 5, "dim": 6
        }

        maintenant = datetime.now()
        jour_actuel = maintenant.weekday()
        heure_actuelle = maintenant.hour + maintenant.minute / 60.0

        try:
            if not horaire or not isinstance(horaire, str):
                return False

            parts = horaire.strip().split()  # ex: ['Lun-Ven', '08:30-16:30']
            if len(parts) != 2:
                return False

            jours_range = parts[0].lower().split('-')
            if len(jours_range) != 2:
                return False

            debut_jour = jours_map.get(jours_range[0][:3], -1)
            fin_jour = jours_map.get(jours_range[1][:3], -1)
            if debut_jour == -1 or fin_jour == -1:
                return False

            heures = parts[1].split('-')
            if len(heures) != 2:
                return False

            def convert_to_decimal(hhmm):
                h, m = map(int, hhmm.split(':'))
                return h + m / 60.0

            heure_debut = convert_to_decimal(heures[0])
            heure_fin = convert_to_decimal(heures[1])

        # Comparaison
            if debut_jour <= jour_actuel <= fin_jour and heure_debut <= heure_actuelle <= heure_fin:
                return True
            return False

        except Exception:
            return False
    




