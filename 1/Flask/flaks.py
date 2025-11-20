from flask import Blueprint, jsonify, request
import mysql.connector
from conn import get_db_connection
from datetime import datetime, timedelta
import bcrypt
routes1 = Blueprint('bald', __name__)



@routes1.route("/rendezvous", methods=["GET"])
def get_rendez_vous():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
    SELECT
        r.id_rdv,
        r.date_heure,
        r.statut,
        r.id_patient,
        CONCAT(p.prenom, ' ', p.nom) AS patient,
        CONCAT(m.nom, ' (', m.specialite, ')') AS medecin
    FROM
        rendez_vous r
    JOIN patient p ON r.id_patient = p.id_patient
    JOIN medecin m ON r.id_medecin = m.id_medecin
    ORDER BY r.date_heure DESC
"""
        cursor.execute(query)
        resultats = cursor.fetchall()

        for rdv in resultats:
            if isinstance(rdv["date_heure"], datetime):
                rdv["date_heure"] = rdv["date_heure"].strftime("%Y-%m-%d %H:%M:%S")

        return jsonify(resultats)

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@routes1.route("/delete", methods=["GET"])
def delete():
    id_rdv = request.args.get("id")
    if not id_rdv:
        return jsonify({"error": "id manquant"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "DELETE FROM rendez_vous WHERE id_rdv = %s"
        cursor.execute(query, (id_rdv,))
        conn.commit()
        return jsonify({"success": True, "id_supprime": id_rdv})
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
@routes1.route('/modifier_rendezvous', methods=['POST'])
def modifier_rendezvous():
    conn =get_db_connection()
    cursor = conn.cursor()
    data = request.get_json()
    print("DATA REÇUE:", data)

    try:
        id_rdv = data.get("id_rdv")
        id_medecin = data.get("id_medecin")
        date_heure = data.get("date_heure")  # format: YYYY-MM-DD HH:MM:SS

        if not id_rdv or not id_medecin or not date_heure:
            return jsonify({"success": False, "message": "Données incomplètes"}), 400

        query = """
            UPDATE rendez_vous 
            SET id_medecin = %s,
                date_heure = %s
            WHERE id_rdv = %s
        """
        cursor.execute(query, (id_medecin, date_heure, id_rdv))
        conn.commit()

        return jsonify({"success": True, "message": "Rendez-vous modifié avec succès."})

    except Exception as e:
        print("Erreur lors de la modification :", str(e))
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

@routes1.route("/get_rdv_by_id", methods=["POST"])
def get_rdv_by_id():
    data = request.get_json()
    id_rdv = data.get("id_rdv")

    if not id_rdv:
        return jsonify({"success": False, "message": "ID manquant"}), 400

    conn =get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT 
                r.id_rdv,
                r.date_heure,
                r.id_patient,
                p.nom AS patient_nom,
                p.prenom AS patient_prenom,
                r.id_medecin
            FROM rendez_vous r
            JOIN patient p ON r.id_patient = p.id_patient
            WHERE r.id_rdv = %s
        """
        cursor.execute(query, (id_rdv,))
        rdv = cursor.fetchone()
        if rdv:
            if isinstance(rdv["date_heure"], datetime):
                rdv["date_heure"] = rdv["date_heure"].strftime("%Y-%m-%d %H:%M:%S")
            return jsonify(rdv)
        else:
            return jsonify({"success": False, "message": "Rendez-vous introuvable"}), 404

    except Exception as e:
        print(e)
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@routes1.route('/ajouter_rendezvous', methods=['POST'])
def ajouter_rendezvous():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    data = request.get_json()
    print("DATA REÇUE:", data)

    try:
        # Récupération et conversion de la date
        date_str = data.get("date_heure")  # "yyyy-MM-dd HH:mm:ss"
        try:
            date_h = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return jsonify({"success": False, "message": "Format de date invalide"}), 400

        # Récupération des IDs
        patient_id = data.get("patient_id")
        medecin_id = data.get("medecin_id")

        if not all([patient_id, medecin_id]):
            return jsonify({"success": False, "message": "ID patient ou médecin manquant"}), 400

        # Insertion dans la table rendezvous (à adapter selon ta base)
        query = """
            INSERT INTO rendez_vous (date_heure, statut, id_patient, id_medecin)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (
            date_h.strftime("%Y-%m-%d %H:%M:%S"),
            "Confirmé",  # ou "en attente", selon ton besoin
            patient_id,
            medecin_id
        ))

        conn.commit()
        return jsonify({"success": True, "message": "Rendez-vous ajouté avec succès"})

    except Exception as e:
        print("Erreur lors de l'insertion :", str(e))
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()
@routes1.route("/rendezvous/<int:id_rdv>/statut", methods=["PUT"])
def changer_statut_rendezvous(id_rdv):
    conn = None
    cursor = None
    try:
        data = request.get_json()
        nouveau_statut = data.get("statut")

        if not nouveau_statut:
            return jsonify({"error": "Le champ 'statut' est requis."}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        query = "UPDATE rendez_vous SET statut = %s WHERE id_rdv = %s"
        cursor.execute(query, (nouveau_statut, id_rdv))
        conn.commit()

        return jsonify({"message": f"Statut du rendez-vous {id_rdv} mis à jour avec succès."})

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
@routes1.route('/api/stats/summary', methods=['GET'])
def get_summary_stats():
    conn =get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Patients totaux
        cursor.execute("SELECT COUNT(*) AS total FROM patient")
        total_patients = cursor.fetchone()['total']
        
        # Médecins totaux
        cursor.execute("SELECT COUNT(*) AS total FROM medecin")
        total_doctors = cursor.fetchone()['total']
        
        # Rendez-vous totaux
        cursor.execute("SELECT COUNT(*) AS total FROM rendez_vous")
        total_appointments = cursor.fetchone()['total']
        
        # Chiffre d'affaires total
        cursor.execute("SELECT SUM(montant) AS total FROM paiement")
        total_ca = cursor.fetchone()['total'] or 0
        
        return jsonify({
            'total_patients': total_patients,
            'total_doctors': total_doctors,
            'total_appointments': total_appointments,
            'total_ca': total_ca
        })
        
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@routes1.route('/api/stats/ca', methods=['GET'])
def get_ca_evolution():
    period = request.args.get('period', '30d')
    end_date = datetime.now()
    
    # Définition de la période
    if period == '7d':
        start_date = end_date - timedelta(days=7)
    elif period == '3m':
        start_date = end_date - timedelta(days=90)
    elif period == '12m':
        start_date = end_date - timedelta(days=365)
    else:  # 30d par défaut
        start_date = end_date - timedelta(days=30)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
            SELECT DATE(date_paiement) AS date, SUM(montant) AS amount
            FROM paiement
            WHERE date_paiement BETWEEN %s AND %s
            GROUP BY DATE(date_paiement)
            ORDER BY DATE(date_paiement)
        """
        cursor.execute(query, (start_date, end_date))
        results = cursor.fetchall()
        
        # Formatage des résultats
        data = [{
            'date': row['date'].strftime('%Y-%m-%d'),
            'amount': row['amount'] 
        } for row in results]
        print(data)
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@routes1.route('/api/stats/specialities', methods=['GET'])
def get_specialities_distribution():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
            SELECT specialite, COUNT(*) AS count
            FROM medecin
            GROUP BY specialite
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        data = [{
            'speciality': row['specialite'],
            'count': row['count']
        } for row in results]
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@routes1.route('/api/stats/appointments', methods=['GET'])
def get_appointments_status():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
            SELECT statut, COUNT(*) AS count
            FROM rendez_vous
            GROUP BY statut
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        data = [{
            'status': row['statut'],
            'count': row['count']
        } for row in results]
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@routes1.route('/api/stats/patients', methods=['GET'])
def get_patients_evolution():
    period = request.args.get('period', '30d')
    end_date = datetime.now()
    
    # Définition de la période
    if period == '7d':
        start_date = end_date - timedelta(days=7)
    elif period == '3m':
        start_date = end_date - timedelta(days=90)
    elif period == '12m':
        start_date = end_date - timedelta(days=365)
    else:  # 30d par défaut
        start_date = end_date - timedelta(days=30)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Nouveaux patients par jour
        new_patients_query = """
            SELECT DATE(date_naissance) AS date, COUNT(*) AS new_patients
            FROM patient
            WHERE date_naissance BETWEEN %s AND %s
            GROUP BY DATE(date_naissance)
            ORDER BY DATE(date_naissance)
        """
        cursor.execute(new_patients_query, (start_date, end_date))
        new_results = cursor.fetchall()
        
        # Patients cumulés
        cumulative_query = """
            SELECT date, SUM(new_patients) OVER (ORDER BY date) AS total_patients
            FROM (
                SELECT DATE(date_naissance) AS date, COUNT(*) AS new_patients
                FROM patient
                WHERE date_naissance BETWEEN %s AND %s
                GROUP BY DATE(date_naissance)
            ) AS sub
            ORDER BY date
        """
        cursor.execute(cumulative_query, (start_date, end_date))
        cumulative_results = cursor.fetchall()
        
        # Fusionner les résultats
        data = []
        for new_row, cum_row in zip(new_results, cumulative_results):
            data.append({
                'date': new_row['date'].strftime('%Y-%m-%d'),
                'new_patients': new_row['new_patients'],
                'total_patients': cum_row['total_patients']
            })
        
        return jsonify(data)
        
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

