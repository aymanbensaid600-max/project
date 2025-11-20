from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

class MedecinCard(QFrame):
    def __init__(self, nom, prenom, specialite, horaires, disponibilite):
        super().__init__()
        # Réduire la hauteur fixe ici (ex: 180 au lieu de 350)
        self.setFixedHeight(60)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 8px;
            }
        """)
        main_layout = QHBoxLayout(self)
         # === Infos médecin ===
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)  # espacement plus petit
        # Ligne 1: Nom et spécialité sur la même ligne
        line1 = QHBoxLayout()
        nom_label = QLabel(f"Dr. {prenom} {nom}")
        nom_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333; border:none;")
        specialite_label = QLabel(f" | {specialite}")
        specialite_label.setStyleSheet("font-size: 13px; color: #555; border:none;")
        line1.addWidget(nom_label)
        line1.addWidget(specialite_label)
        line1.addStretch()
        info_layout.addLayout(line1)
        # Ligne 2: Horaires et disponibilité sur la même ligne
        line2 = QHBoxLayout()
        horaires_label = QLabel(f"Horaires : {horaires}")
        horaires_label.setStyleSheet("font-size: 12px; color: #555; border:none;")
        statut_label = QLabel("🟢 En service" if disponibilite else "🔴 Absent")
        statut_label.setStyleSheet("font-size: 12px; color: #444; border:none; padding-left: 20px;")
        line2.addWidget(horaires_label)
        line2.addWidget(statut_label)
        line2.addStretch()
        info_layout.addLayout(line2)
        info_layout.addStretch()
        main_layout.addLayout(info_layout)
