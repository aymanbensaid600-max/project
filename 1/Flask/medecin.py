from flask import Blueprint,Flask, jsonify, request
import mysql.connector
from datetime import datetime, timedelta
from conn import get_db_connection
from collections import defaultdict
routes3 = Blueprint('med', __name__)

@routes3.route('/ajouter_medecin', methods=['POST'])
def form():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    data = request.get_json()
    print("DATA REÇUE:", data)

    try:
       
        
        query = """
            INSERT INTO medecin (nom, prenom, specialite, email, telephone,mot_de_passe, horaires, disponibilite)
            VALUES (%s, %s, %s,%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data.get("nom"),
            data.get("prenom"),
            data.get("specialite"),
            data.get("email"),
            data.get("telephone"),
            data.get("mot_de_passe"),
            data.get("horaires"),
            data.get("disponibilite", 1)  # Par défaut dispo = 1
        ))
        conn.commit()
        return jsonify({"success": True, "message": "Médecin ajouté avec succès"})

    except Exception as e:
        print("Erreur lors de l'insertion :", str(e))
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()
@routes3.route('/AfficheMed', methods=['GET'])
def Affiche():
    conn = None
    cursor = None
    try:
        conn =get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Si tu veux gérer un champ de suppression logique, ajoute le champ ISdelete dans la table medecin
        # Sinon, juste afficher tous les médecins
        query = """
            SELECT id_medecin, nom, prenom, specialite, email, telephone, horaires, disponibilite
            FROM medecin where Isdelete=0
        """
        cursor.execute(query)
        resultats = cursor.fetchall()
        print(resultats)
        return jsonify(resultats)

    except mysql.connector.Error as err:
        print("Erreur MySQL :", err)
        return jsonify({"error": str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@routes3.route('/DeleteMed', methods=['DELETE'])
def DeleteMed():
    conn = None
    cursor = None
    try:
        conn =get_db_connection()
        cursor = conn.cursor()
        id_medecin = request.args.get("index")
        print(id_medecin)
        if not id_medecin:
            return jsonify({"success": False, "message": "id_medecin manquant"}), 400

        query = "UPDATE medecin SET Isdelete = 1 WHERE id_medecin = %s"
        cursor.execute(query, (id_medecin,))
        conn.commit()
        return jsonify({"success": True, "id_desactive": id_medecin})

    except mysql.connector.Error as err:
        print("Erreur MySQL :", err)
        return jsonify({"error": str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@routes3.route('/modifieMedecin', methods=['GET'])
def modifie():
    conn = None
    cursor = None
    try:
        conn =get_db_connection()
        cursor = conn.cursor(dictionary=True)
        id_medecin = request.args.get("index")
        if not id_medecin:
            return jsonify({"error": "id_medecin manquant"}), 400

        query = "SELECT * FROM medecin WHERE id_medecin = %s"
        cursor.execute(query, (id_medecin,))
        resultat = cursor.fetchone()

        if resultat is None:
            return jsonify({"error": "Médecin non trouvé"}), 404

        return jsonify(resultat)

    except mysql.connector.Error as err:
        print("Erreur MySQL :", err)
        return jsonify({"error": str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@routes3.route('/editMedecin', methods=['POST'])
def Edit():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    data = request.get_json()
    print("DATA REÇUE:", data)

    try:
        id_medecin = data.get("id_medecin")
        if not id_medecin:
            return jsonify({"success": False, "message": "ID du médecin manquant"}), 400

        query = """
            UPDATE medecin SET 
                nom = %s,
                prenom = %s,
                specialite = %s,
                email = %s,
                telephone = %s,
                horaires = %s,
                disponibilite = %s
            WHERE id_medecin = %s
        """
        cursor.execute(query, (
            data.get("nom"),
            data.get("prenom"),
            data.get("specialite"),
            data.get("email"),
            data.get("telephone"),
            data.get("horaires"),
            data.get("disponibilite", 1),
            id_medecin
        ))
        conn.commit()

        return jsonify({"success": True, "message": "Médecin modifié avec succès."})

    except Exception as e:
        print("Erreur lors de la modification :", str(e))
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()
def arrondir_heure(dt):
    """Arrondir au créneau 30 minutes le plus proche inférieur."""
    minute = 0 if dt.minute < 30 else 30
    return dt.replace(minute=minute, second=0, microsecond=0)
@routes3.route("/pla", methods=["POST"])
def cons():
    data = request.get_json()
    if not data or "id_medecin" not in data:
        return jsonify({"error": "id_medecin manquant"}), 400

    id_medecin = data.get("id_medecin")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            r.date_heure,
            r.statut,
            CONCAT(p.prenom, ' ', p.nom) AS patient
        FROM
            rendez_vous r
        JOIN patient p ON r.id_patient = p.id_patient
        WHERE r.statut != 'Annulé'
          AND r.id_medecin = %s
        ORDER BY r.date_heure ASC
    """

    cursor.execute(query, (id_medecin,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    rdvs_par_date = defaultdict(dict)

    for row in results:
        dt = row["date_heure"]  # datetime
        dt_rounded = arrondir_heure(dt)
        date_str = dt_rounded.strftime("%Y-%m-%d")
        heure_str = dt_rounded.strftime("%H:%M")
        patient = row["patient"]
        statut = row["statut"]
        rdvs_par_date[date_str][heure_str] = f"{patient} ({statut})"

    return jsonify(rdvs_par_date)
