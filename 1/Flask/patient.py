from flask import Blueprint, jsonify, request,send_file, abort
import mysql.connector
from conn import get_db_connection
from datetime import datetime, timedelta
import bcrypt
import os
routes2 = Blueprint('pat', __name__)

@routes2.route('/formulaire', methods=['POST'])
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
@routes2.route('/Affiche',methods=['GET'])
def Affiche():

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Calcul des dates limites pour filtrag

        query = """SELECT id_patient,
        nom,
        prenom,
         DATE_FORMAT(date_naissance, '%Y-%m-%d') AS date_naissance,
        sexe,
        adresse,
        email,
        telephone FROM patient 
        Where ISdelete=0"""

        cursor.execute(query,)
        resultats = cursor.fetchall()
        print(resultats)
        return jsonify(resultats)

    except mysql.connector.Error as err:
        print("Erreur MySQL :", err)  #
        return jsonify({"error": str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@routes2.route('/DeletePatient', methods=['GET', 'DELETE'])
def DeletePatient():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        index = request.args.get("index")
        print(index)
        query = "UPDATE patient SET ISdelete=1 WHERE id_patient=%s"
        cursor.execute(query, (index,))
        conn.commit()
        return jsonify({"success": True, "id_supprime": index})
    except mysql.connector.Error as err:
        print("Erreur MySQL :", err)
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@routes2.route('/modifie', methods=['GET'])
def modifie():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # dict au lieu de tuple
        index = request.args.get("index")
        if not index:
            return jsonify({"error": "index manquant"}), 400

        query = "SELECT * FROM patient WHERE id_patient = %s"
        cursor.execute(query, (index,))
        resultat = cursor.fetchone()

        if resultat is None:
            return jsonify({"error": "Patient non trouvé"}), 404

        return jsonify(resultat)

    except mysql.connector.Error as err:
        print("Erreur MySQL :", err)
        return jsonify({"error": str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            conn.close()


@routes2.route('/Edit', methods=['POST'])
def Edit():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    data = request.get_json()
    print("DATA REÇUE:", data)

    try:
      
        date_str = data.get("date_naissance")
        try:
            date_naissance = datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            return jsonify({"success": False, "message": "Format de date invalide"}), 400

       
        patient_id = data.get("id_patient")
        if not patient_id:
            return jsonify({"success": False, "message": "ID du patient manquant"}), 400

        query = """
            UPDATE patient SET 
                nom = %s,
                prenom = %s,
                date_naissance = %s,
                sexe = %s,
                adresse = %s,
                email = %s,
                telephone = %s
            WHERE id_patient = %s
        """
        cursor.execute(query, (
            data.get("nom"),
            data.get("prenom"),
            date_naissance,
            data.get("sexe"),
            data.get("adresse"),
            data.get("email"),
            data.get("telephone"),
            patient_id
        ))
        conn.commit()

        return jsonify({"success": True, "message": "Patient modifié avec succès."})

    except Exception as e:
        print("Erreur lors de la modification :", str(e))
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()
@routes2.route('/historique/<int:id_patient>', methods=['GET'])
def historique_patient(id_patient):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)  # <---- buffered=True ici

        cursor.execute("SELECT * FROM patient WHERE id_patient = %s", (id_patient,))
        patient = cursor.fetchone()
        if not patient:
            return jsonify({"success": False, "message": "Patient non trouvé"}), 404

        cursor.execute("SELECT * FROM dossier_medical WHERE id_patient = %s", (id_patient,))
        dossier = cursor.fetchone()
        if not dossier:
            return jsonify({"success": False, "message": "Aucun dossier trouvé"}), 404

        cursor.execute("""
            SELECT id_suivi,date_suivi, observations, fichier_ordonnance
            FROM suivi_medical
            WHERE id_dossier = %s
            ORDER BY date_suivi ASC
        """, (dossier['id_dossier'],))
        suivis = cursor.fetchall()

        if dossier.get('date_creation'):
            dossier['date_creation'] = dossier['date_creation'].strftime("%Y-%m-%d")
        for suivi in suivis:
            if suivi.get('date_suivi'):
                suivi['date_suivi'] = suivi['date_suivi'].strftime("%Y-%m-%d")

        return jsonify({
            "success": True,
            "patient": patient,
            "dossier": {
                "id_dossier": dossier['id_dossier'],
                "date_creation": dossier['date_creation'],
                "suivis": suivis
            }
        })

    except mysql.connector.Error as e:
        return jsonify({"success": False, "message": f"Erreur MySQL : {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
@routes2.route('/telecharger_ordonnance/<int:id_suivi>', methods=['GET'])
def telecharger_ordonnance(id_suivi):
    conn =  get_db_connection()
    cursor = conn.cursor()

   
    cursor.execute("SELECT fichier_ordonnance FROM suivi_medical WHERE id_suivi = %s", (id_suivi,))
    resultat = cursor.fetchone()
    conn.close()

    if resultat:
        chemin_fichier = resultat[0]

        if chemin_fichier and os.path.exists(chemin_fichier):
           
            nom_fichier = os.path.basename(chemin_fichier)
            return send_file(
                chemin_fichier,
                download_name=nom_fichier,
                as_attachment=True
            )
        else:
            abort(404, description="Fichier d'ordonnance introuvable.")
    else:
        abort(404, description="Suivi médical non trouvé.")

