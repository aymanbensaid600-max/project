from flask import Blueprint, request, jsonify
from conn import get_db_connection
from datetime import datetime
import bcrypt
routes = Blueprint('routes', __name__)



@routes.route('/connexion', methods=['POST'])
def connexion():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    data = request.get_json()
    print("Reçu :", data)

    email = data.get("email")
    mot_de_passe = data.get("mot_de_passe")

    try:
        # Chercher dans la table admin
        cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
        admin = cursor.fetchone()

        if admin and admin["mot_de_passe"] == mot_de_passe:
            return jsonify({
                "success": True,
                "message": "Connexion réussie",
                "type_utilisateur": "admin"
            })
 
        # Chercher dans la table patient
        cursor.execute("SELECT * FROM patient WHERE email = %s", (email,))
        patient = cursor.fetchone()

        if patient:
            mot_de_passe_hash = patient["mot_de_passe"].encode("utf-8")
            if bcrypt.checkpw(mot_de_passe.encode("utf-8"), mot_de_passe_hash):
                return jsonify({
                    "success": True,
                    "message": "Connexion réussie",
                    "type_utilisateur": "patient",
                    "id_pat":patient['id_patient']
                })
        
        cursor.execute("SELECT * FROM medecin WHERE email = %s", (email,))
        med = cursor.fetchone()
        if med  and med["mot_de_passe"] == mot_de_passe:
                return jsonify({
                    "success": True,
                    "message": "Connexion réussie",
                    "type_utilisateur": "medecin",
                    "id_med":med['id_medecin']
                })

        return jsonify({
            "success": False,
            "message": "Email ou mot de passe incorrect"
        }), 401

    finally:
        cursor.close()
        conn.close()

@routes.route('/formulaire', methods=['POST'])
def formulaire():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    data = request.get_json()
    print("DATA REÇUE:", data)

    try:
        print("Vérification des données avant insertion...")

        # Conversion de la date au bon format pour MySQL
        date_str = data.get("date_naissance")
        try:
            date_naissance = datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            return jsonify({"success": False, "message": "Format de date invalide"}), 400

        print("Date convertie:", date_naissance)
        print("Insertion des données dans la base...")

        # Insertion du patient
        query = """
            INSERT INTO patient (nom, prenom, date_naissance, sexe, adresse, email, telephone, mot_de_passe)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data.get("nom"),
            data.get("prenom"),
            date_naissance,
            data.get("sexe"),
            data.get("adresse"),
            data.get("email"),
            data.get("telephone"),
            data.get("password")
        ))
        conn.commit()

        # Récupération de l'ID du patient nouvellement inséré
        patient_id = cursor.lastrowid
        print("ID patient inséré :", patient_id)

        # Création du dossier médical associé (vous pouvez personnaliser les champs)
        query_dossier = """
            INSERT INTO dossier_medical (id_patient, date_creation)
            VALUES (%s, NOW())
        """
        cursor.execute(query_dossier, (patient_id,))
        conn.commit()
        print("Dossier médical créé pour le patient.")

        return jsonify({"success": True, "message": "Inscription réussie avec création du dossier médical"})

    except Exception as e:
        print("Erreur lors de l'insertion :", str(e))
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()
