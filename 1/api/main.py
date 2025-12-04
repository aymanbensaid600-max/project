# main.py
import sys
import subprocess
from PySide6.QtWidgets import QApplication
from Accueil.MedicalLoginPage import MedicalLoginPage

if __name__ == "__main__":
   
    flask_process = subprocess.Popen([sys.executable, "Flask/mainflask.py"])

   
    app = QApplication(sys.argv)
    window = MedicalLoginPage()
    window.show()
   
    exit_code = app.exec()

   
    flask_process.terminate()
    sys.exit(exit_code)
