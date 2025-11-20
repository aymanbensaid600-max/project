from PySide6.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QMenu, QToolButton, QLineEdit,
    QDialog, QFormLayout
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import requests
from datetime import datetime
from med.ord import FichePatient
class MesPatients(QWidget):
    def __init__(self, id_medecin):
        super().__init__()
        self.id_medecin = id_medecin
        self.setup_ui()
        self.charger_patients()
        self.apply_styles()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 25, 25, 25)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Title
        title = QLabel("Mes patients")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #00796b; background-color: transparent;")
        layout.addWidget(title)

        # Barre de recherche + bouton actualiser
        filter_layout = QHBoxLayout()
        self.search_field = QLineEdit()
        self.search_field.setObjectName("searchField")
        self.search_field.setPlaceholderText("Rechercher un patient...")
        self.search_field.textChanged.connect(self.filtrer_patients)
        filter_layout.addWidget(self.search_field)
        filter_layout.addStretch()
        refresh_btn = QPushButton("Actualiser")
        refresh_btn.clicked.connect(self.charger_patients)
        filter_layout.addWidget(refresh_btn)
        layout.addLayout(filter_layout)
        main_layout.addLayout(layout)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Prénom", "Email", "Téléphone", "Dernière visite"])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
       

        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSortingEnabled(True)

        self.table.cellDoubleClicked.connect(self.ouvrir_details_patient)

        main_layout.addWidget(self.table)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f5ff;
                color: #333333;
                font-family: 'Segoe UI';
            }

            QPushButton {
                background-color: #4a9dff;
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                border: none;
                font-size: 12px;
            }

            QPushButton#addButton {
                background-color: #4CAF50;
                padding: 8px 16px;
                min-width: 150px;
            }

            QPushButton#addButton:hover {
                background-color: #43A047;
            }

            QPushButton#actionButton {
                background-color: #2196F3;
                min-width: 40px;
                min-height: 40px;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
            }

            QTableWidget {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                gridline-color: #e0e0e0;
                border: none;
                selection-background-color: #e3f2fd;
                selection-color: #333333;
                font-size: 12px;
            }

            QHeaderView::section {
                background-color: #00796b;
                color: white;
                padding: 8px 12px;
                font-weight: bold;
                border: none;
                font-size: 12px;
            }

            QTableWidget::item {
                padding: 8px 12px;
                border: none;
            }

            QMenu {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 4px;
            }

            QMenu::item {
                padding: 6px 24px 6px 12px;
                margin: 2px;
                border-radius: 4px;
            }

            QMenu::item:selected {
                background-color: #e0f2f1;
                color: #004d40;
            }

            #searchField {
                background-color: white;
                border: 1px solid #d1d1d1;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 14px;
                min-width: 300px;
            }
        """)

    def charger_patients(self):
        try:
            response = requests.get(
                f"http://127.0.0.1:5000/charger_suivi?id_medecin={self.id_medecin}"
            )
            if response.status_code == 200:
                self.patients_data = response.json()
                self.afficher_patients(self.patients_data)
            else:
                print(f"Erreur serveur: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Erreur réseau: {e}")

    def afficher_patients(self, patients):
        self.table.setRowCount(len(patients))
        for row, patient in enumerate(patients):
            self.table.setItem(row, 0, QTableWidgetItem(str(patient['id_patient'])))
            self.table.setItem(row, 1, QTableWidgetItem(patient['nom']))
            self.table.setItem(row, 2, QTableWidgetItem(patient['prenom']))
            self.table.setItem(row, 3, QTableWidgetItem(patient['email']))
            self.table.setItem(row, 4, QTableWidgetItem(patient['telephone']))

            derniere_visite = patient.get('dernier_rendez_vous', 'N/A')
           
                
            self.table.setItem(row, 5, QTableWidgetItem(derniere_visite))

           

            for col in range(5):
                item = self.table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)

    def filtrer_patients(self):
        search_text = self.search_field.text().lower()
        if not search_text:
            self.afficher_patients(self.patients_data)
            return

        filtered_patients = []
        for patient in self.patients_data:
            if (search_text in str(patient['id_patient']).lower() or
                search_text in patient['nom'].lower() or
                search_text in patient['prenom'].lower()):
                filtered_patients.append(patient)

        self.afficher_patients(filtered_patients)

    def ouvrir_details_patient(self, row, column):
        patient_id = self.table.item(row, 0).text()
        patient = next((p for p in self.patients_data if str(p['id_patient']) == patient_id), None)
        if patient:
            self.afficher_details(patient)

    def afficher_details(self, patient):
        print(patient)
        fiche = FichePatient(patient)
        fiche.setWindowModality(Qt.ApplicationModal)
        fiche.resize(400, 300)
        fiche.show()
        fiche.exec()  # Si FichePatient hérite de QDialog, sinon juste `show()` si QWidget

   
