from flask import Flask, jsonify, request,Blueprint
import mysql.connector
from datetime import datetime, timedelta
from collections import defaultdict
import os
from conn import get_db_connection
from werkzeug.utils import secure_filename
from flask import current_app

routes7= Blueprint('robi', __name__)



@routes7.route('/charger_med', methods=['GET'])
def Affiche_med():
    conn = None
    cursor = None
    try:
        id_medecin = request.args.get('id_med')
        if not id_medecin:
            return jsonify({"error": "id_medecin manquant"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                   nom,
                   prenom,
                   specialite,
                   email,
                   telephone
            FROM medecin
            WHERE ISdelete = 0 AND id_medecin = %s
        """
        cursor.execute(query, (id_medecin,))
        resultats = cursor.fetchall()

        if resultats:
            return jsonify(resultats[0])
        else:
            return jsonify({"error": "Médecin non trouvé"}), 404

    except mysql.connector.Error as err:
        print("Erreur MySQL :", err)
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@routes7.route('/charger_mesrdv', methods=['GET'])
def mesrdv():
    conn = None
    cursor = None
    try:
        id_medecin = request.args.get('id_med')
        if not id_medecin:
            return jsonify({"error": "id_medecin manquant"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT
            r.id_rdv,
            r.date_heure,
            r.statut,
            r.id_patient,
            CONCAT(p.prenom, ' ', p.nom) AS patient
        FROM
            rendez_vous r
        JOIN patient p ON r.id_patient = p.id_patient
        WHERE r.statut != 'Annulé'
          AND r.id_medecin = %s
        ORDER BY r.date_heure ASC
        """
        cursor.execute(query, (id_medecin,))
        resultats = cursor.fetchall()

        if resultats:
            return jsonify(resultats)
        else:
            return jsonify([])

    except mysql.connector.Error as err:
        print("Erreur MySQL :", err)
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@routes7.route('/medecin_dashboard', methods=['GET'])
def medecin_dashboard():
    conn = None
    cursor = None
    try:
        id_medecin = request.args.get('id_medecin')
        if not id_medecin:
            return jsonify({"error": "id_medecin manquant"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        
        cursor.execute("""
            SELECT COUNT(DISTINCT id_patient) AS total_patients 
            FROM rendez_vous 
            WHERE id_medecin = %s
        """, (id_medecin,))
        total_patients = cursor.fetchone()['total_patients']
        
        
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT COUNT(*) AS rdv_today
            FROM rendez_vous 
            WHERE id_medecin = %s 
              AND DATE(date_heure) = %s
              AND statut != 'Annulé'
        """, (id_medecin, today))
        rdv_today = cursor.fetchone()['rdv_today']
        
       
        cursor.execute("""
            SELECT COUNT(*) AS rdv_upcoming
            FROM rendez_vous 
            WHERE id_medecin = %s 
              AND DATE(date_heure) > %s
              AND statut != 'Annulé'
        """, (id_medecin, today))
        rdv_upcoming = cursor.fetchone()['rdv_upcoming']
        
       
        cursor.execute("""
            SELECT 
                p.nom, 
                p.prenom, 
                DATE(r.date_heure) AS date,
                TIME(r.date_heure) AS heure,
                r.statut
            FROM rendez_vous r
            JOIN patient p ON r.id_patient = p.id_patient
            WHERE r.id_medecin = %s
              AND r.date_heure >= CURDATE()
              AND r.statut != 'Annulé'
            ORDER BY r.date_heure ASC
            LIMIT 10
        """, (id_medecin,))
        
        prochains_rdv = []
        for row in cursor.fetchall():
            prochains_rdv.append({
                'patient_nom': row['nom'],
                'patient_prenom': row['prenom'],
                'date': row['date'].strftime("%d/%m/%Y"),
                'heure': str(row['heure']),
                'statut': row['statut']
            })
        
        return jsonify({
            'total_patients': total_patients,
            'rdv_today': rdv_today,
            'rdv_upcoming': rdv_upcoming,
            'prochains_rdv': prochains_rdv
        })

    except mysql.connector.Error as err:
        print("Erreur MySQL:", err)
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
@routes7.route('/charger_suivi',methods=['GET'])
def charger():
    conn = None
    cursor = None
    try:
        id_medecin = request.args.get('id_medecin')
        if not id_medecin:
            return jsonify({"error": "id_medecin manquant"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query="""
      WITH dernier_suivi AS (
    SELECT s1.*
    FROM suivi_medical s1
    JOIN (
        SELECT id_dossier, MAX(date_suivi) AS max_date
        FROM suivi_medical
        GROUP BY id_dossier
    ) s2 ON s1.id_dossier = s2.id_dossier AND s1.date_suivi = s2.max_date
)

SELECT
    p.id_patient,
    p.nom,
    p.prenom,
    p.telephone,
    p.email,
    MAX(r.date_heure) AS dernier_rendez_vous,
    r.id_medecin,
    d.id_dossier,
    ds.observations,
    ds.date_suivi
FROM patient p
JOIN rendez_vous r ON r.id_patient = p.id_patient AND r.id_medecin = %s
LEFT JOIN dossier_medical d ON d.id_patient = p.id_patient
LEFT JOIN dernier_suivi ds ON ds.id_dossier = d.id_dossier
GROUP BY p.id_patient, d.id_dossier, r.id_medecin, p.nom, p.prenom, p.telephone, p.email, ds.observations, ds.date_suivi
ORDER BY dernier_rendez_vous DESC;

"""
        cursor.execute(query, (id_medecin,))
        resultats = cursor.fetchall()
        print(resultats)
        if resultats:
            return jsonify(resultats)
        else:
            return jsonify([])

    except mysql.connector.Error as err:
        print("Erreur MySQL:", err)
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
@routes7.route('/get_patient', methods=['GET'])
def get_patient():
    conn = None
    cursor = None
    try:
        id_patient = request.args.get('id_patient')
        if not id_patient:
            return jsonify({"error": "id_patient manquant"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT nom, prenom, telephone, email
            FROM patient
            WHERE id_patient = %s
        """
        cursor.execute(query, (id_patient,))
        result = cursor.fetchone()

        if result:
            return jsonify(result)
        else:
            return jsonify({"error": "Patient non trouvé"}), 404

    except mysql.connector.Error as err:
        print("Erreur MySQL :", err)
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@routes7.route('/get_rendezvous_patient', methods=['GET'])
def get_rendezvous_patient():
    conn = None
    cursor = None
    try:
        id_patient = request.args.get('id_patient')
        id_medecin = request.args.get('id_medecin')  # Nouveau paramètre optionnel

        if not id_patient:
            return jsonify({"error": "id_patient manquant"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Construction dynamique de la requête
        query = """
            SELECT r.id_rdv, r.date_heure, r.statut, m.nom AS medecin_nom, m.prenom AS medecin_prenom
            FROM rendez_vous r
            JOIN medecin m ON r.id_medecin = m.id_medecin
            WHERE r.id_patient = %s
        """
        params = [id_patient]

        if id_medecin:
            query += " AND r.id_medecin = %s"
            params.append(id_medecin)

        query += " ORDER BY r.date_heure DESC"

        cursor.execute(query, tuple(params))
        resultats = cursor.fetchall()

        return jsonify(resultats)

    except mysql.connector.Error as err:
        print("Erreur MySQL:", err)
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()



@routes7.route('/update_observation', methods=['POST'])
def update_observation():
    id_patient = request.form.get('id_patient')
    id_rdv = request.form.get('id_rdv')
    id_dossier = request.form.get('id_dossier')
    observation = request.form.get('observation', '')
    ordonnance_file = request.files.get('ordonnance')

    if not id_patient or not id_dossier or not id_rdv:
        return jsonify({'error': 'Champs requis manquants'}), 400

    chemin_fichier = None

    if ordonnance_file:
        filename = secure_filename(ordonnance_file.filename)
        patient_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(id_patient))
        os.makedirs(patient_folder, exist_ok=True)
        full_path = os.path.join(patient_folder, filename)
        ordonnance_file.save(full_path)
        chemin_fichier = full_path

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO suivi_medical (
                 id_dossier, id_rdv, observations, fichier_ordonnance, date_suivi
            ) VALUES ( %s, %s, %s, %s, NOW())
        """
        cursor.execute(sql, ( id_dossier, id_rdv, observation, chemin_fichier))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'ok'}), 200
    except mysql.connector.Error  as e:
        print("Erreur MySQL:", e)
        return jsonify({'error': 'Erreur base de données'}), 500

