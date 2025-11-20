from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout
from PySide6.QtGui import QColor
from datetime import datetime

class RendezVousCard(QFrame):
    def __init__(self, id_rdv: int, nom_patient: str, nom_docteur: str, date_heure: datetime, statut: str):
        super().__init__()
        self.setFixedHeight(60)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 8px;
            }
        """)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(15)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        line1 = QHBoxLayout()
        patient_label = QLabel(f"Patient : {nom_patient}")
        patient_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333; border:none;")
        medecin_label = QLabel(f" | Dr. {nom_docteur}")
        medecin_label.setStyleSheet("font-size: 13px; color: #555; border:none;")
        line1.addWidget(patient_label)
        line1.addWidget(medecin_label)
        line1.addStretch()
        info_layout.addLayout(line1)

        line2 = QHBoxLayout()
        
        date_str = datetime.strptime(date_heure, "%Y-%m-%d %H:%M:%S")
        date_label = QLabel(f"Date & heure : {date_str}")
        date_label.setStyleSheet("font-size: 12px; color: #555; border:none;")

        statut_colors = {
            "Confirmé": "#27ae60",
            "Annulé": "#c0392b",
            "En attente": "#f39c12"
        }
        color = statut_colors.get(statut, "#444")
        statut_label = QLabel(f"● {statut}")
        statut_label.setStyleSheet(f"font-size: 12px; color: {color}; border:none; padding-left: 15px;")

        line2.addWidget(date_label)
        line2.addWidget(statut_label)
        line2.addStretch()
        info_layout.addLayout(line2)

        main_layout.addLayout(info_layout)
