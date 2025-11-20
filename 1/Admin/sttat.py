import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QSizePolicy,
    QScrollArea, QFrame, QHBoxLayout
)
from PySide6.QtCore import Qt, QThread, Signal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class StatsWorker(QThread):
    result_ready = Signal(dict)
    error = Signal(str)

    def __init__(self, period):
        super().__init__()
        self.period = period
        self._is_running = True

    def run(self):
        try:
            summary = self.get_json("http://localhost:5000/api/stats/summary")
            ca = self.get_json(f"http://localhost:5000/api/stats/ca?period={self.period}")
            specialities = self.get_json("http://localhost:5000/api/stats/specialities")
            appointments = self.get_json("http://localhost:5000/api/stats/appointments")
            patients = self.get_json(f"http://localhost:5000/api/stats/patients?period={self.period}")

            data = {
                "summary": summary,
                "ca": ca,
                "specialities": specialities,
                "appointments": appointments,
                "patients": patients,
            }
            if self._is_running:
                self.result_ready.emit(data)
        except Exception as e:
            self.error.emit(str(e))

    def get_json(self, url):
        if not self._is_running:
            return None
        response = requests.get(url)
        if response.ok:
            return response.json()
        else:
            raise Exception(f"Erreur lors de la requête: {url}")

    def quit(self):
        self._is_running = False
        super().quit()


class PageStatistique(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #f5f6fa;")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(15)

        scroll_area = QScrollArea()
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f5f5f5;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 12px;
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
        scroll_area.setWidgetResizable(True)

        container = QWidget()
        container.setMinimumWidth(750)
        self.scroll_layout = QVBoxLayout(container)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.setSpacing(15)

        self.title = QLabel("Tableau de Bord - Statistiques")
        self.title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2f3640; margin: 10px 0;")
        self.scroll_layout.addWidget(self.title)

        self.summary_frame = QFrame()
        self.summary_layout = QHBoxLayout(self.summary_frame)
        self.summary_frame.setStyleSheet("QFrame { background: transparent; }")
        self.summary_labels = []

        for color, label in zip(["#00a8ff", "#e1b12c", "#9c88ff", "#44bd32"],
                                ["Patients", "Médecins", "Rendez-vous", "CA (€)"]):
            card = self.create_summary_card(label, color)
            self.summary_labels.append(card.findChild(QLabel, "value"))
            self.summary_layout.addWidget(card)

        self.scroll_layout.addWidget(self.summary_frame)

        self.period_combo = QComboBox()
        self.period_combo.setFixedHeight(28)
        self.period_combo.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #b0bec5;
                padding: 4px 8px;
                border-radius: 6px;
                font-size: 12px;
                color: #37474f;
            }
            QComboBox:hover {
                border: 2px solid #4db6ac;
                background-color: #f0f9f8;
            }
            QComboBox:focus{
                border: 2px solid #00796b;
                background-color: #e0f2f1;
                color: #004d40;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #b0bec5;
                background-color: #e0f2f1;
            }
            QComboBox::down-arrow {
                image: url(down_arrow_icon.png);
                width: 12px;
                height: 12px;
            }
        """)
        self.period_combo.addItems(["7d", "30d", "3m", "12m"])
        self.period_combo.currentTextChanged.connect(self.update_charts)
        self.scroll_layout.addWidget(self.period_combo)

        self.ca_chart = self.create_chart()
        self.speciality_chart = self.create_chart()
        self.status_chart = self.create_chart()
        self.patient_chart = self.create_chart()

        for chart in [self.ca_chart, self.speciality_chart, self.status_chart, self.patient_chart]:
            chart.setMinimumHeight(300)

        self.scroll_layout.addWidget(self.ca_chart)
        self.scroll_layout.addWidget(self.speciality_chart)
        self.scroll_layout.addWidget(self.status_chart)
        self.scroll_layout.addWidget(self.patient_chart)

        scroll_area.setWidget(container)
        self.main_layout.addWidget(scroll_area)

        self.worker = None

        self.load_summary()
        self.update_charts("30d")

    def create_summary_card(self, label_text, bg_color):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 10px;
                padding: 10px;
                min-width: 120px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 8, 10, 8)
        value_label = QLabel("...")
        value_label.setObjectName("value")
        value_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        layout.addWidget(value_label, alignment=Qt.AlignCenter)

        text_label = QLabel(label_text)
        text_label.setStyleSheet("font-size: 12px; color: white;")
        layout.addWidget(text_label, alignment=Qt.AlignCenter)
        return frame

    def create_chart(self):
        fig = Figure(figsize=(7, 4.5))
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return canvas

    def load_summary(self):
        url = "http://localhost:5000/api/stats/summary"
        try:
            response = requests.get(url)
            if response.ok:
                data = response.json()
                self.summary_labels[0].setText(str(data['total_patients']))
                self.summary_labels[1].setText(str(data['total_doctors']))
                self.summary_labels[2].setText(str(data['total_appointments']))

                total_ca = float(data['total_ca']) if data['total_ca'] else 0.0
                self.summary_labels[3].setText(f"{total_ca:.2f} €")
        except Exception as e:
            print("Erreur load_summary:", e)

    def update_charts(self, period):
        if self.worker is not None:
            self.worker.quit()
            self.worker.wait()

        self.worker = StatsWorker(period)
        self.worker.result_ready.connect(self.handle_results)
        self.worker.error.connect(self.handle_error)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    def handle_results(self, data):
        summary = data.get("summary", {})
        if summary:
            self.summary_labels[0].setText(str(summary.get('total_patients', '...')))
            self.summary_labels[1].setText(str(summary.get('total_doctors', '...')))
            self.summary_labels[2].setText(str(summary.get('total_appointments', '...')))
            total_ca = float(summary.get('total_ca', 0.0) or 0.0)
            self.summary_labels[3].setText(f"{total_ca:.2f} €")

        self.plot_ca_chart(data.get("ca", []))
        self.plot_speciality_chart(data.get("specialities", []))
        self.plot_status_chart(data.get("appointments", []))
        self.plot_patient_chart(data.get("patients", []))

    def handle_error(self, message):
        print("Erreur thread:", message)

    def plot_ca_chart(self, data):
        if not data:
            return
        x = [d["date"] for d in data]
        y = [d["amount"] for d in data]

        self.ca_chart.figure.clear()
        ax = self.ca_chart.figure.add_subplot(111)
        ax.plot(x, y, marker='o', color='royalblue')
        ax.set_title("Évolution du Chiffre d'Affaires")
        ax.set_xlabel("Date")
        ax.set_ylabel("Montant (€)")
        ax.grid(True)
        self.ca_chart.draw()

    def plot_speciality_chart(self, data):
        if not data:
            return
        labels = [d["speciality"] for d in data]
        sizes = [d["count"] for d in data]

        self.speciality_chart.figure.clear()
        ax = self.speciality_chart.figure.add_subplot(111)
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        ax.set_title("Répartition par Spécialité")
        self.speciality_chart.draw()

    def plot_status_chart(self, data):
        if not data:
            return
        labels = [d["status"] for d in data]
        sizes = [d["count"] for d in data]

        self.status_chart.figure.clear()
        ax = self.status_chart.figure.add_subplot(111)
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        ax.set_title("Statut des Rendez-vous")
        self.status_chart.draw()

    def plot_patient_chart(self, data):
        if not data:
            return
        x = [d["date"] for d in data]
        y_new = [d["new_patients"] for d in data]
        y_total = [d["total_patients"] for d in data]

        self.patient_chart.figure.clear()
        ax = self.patient_chart.figure.add_subplot(111)
        ax.plot(x, y_new, label="Nouveaux", marker='o', color='orange')
        ax.plot(x, y_total, label="Cumulés", marker='x', color='green')
        ax.set_title("Évolution des Patients")
        ax.set_xlabel("Date")
        ax.set_ylabel("Nombre de patients")
        ax.legend()
        ax.grid(True)
        self.patient_chart.draw()

    def closeEvent(self, event):
        if self.worker is not None and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait()
        event.accept()
