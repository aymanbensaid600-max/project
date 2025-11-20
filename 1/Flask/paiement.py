from flask import Blueprint, jsonify, request
import mysql.connector
from conn import get_db_connection
from datetime import datetime, timedelta
import bcrypt

routes4 = Blueprint('pai', __name__)
@routes4.route('/ajouter_paiement', methods=['POST'])
def ajouter_paiement():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)  # <---- buffered=True ici
        data = request.get_json()
       
        query = """
            INSERT INTO paiement (date_paiement,montant,mode_paiement,id_patient,id_rdv,paiement_effectue)
            VALUES (%s, %s, %s,%s, %s, %s)
        """
        cursor.execute(query, (
            data.get("date_paiement"),
            data.get("montant"),
            data.get("mode_paiement"),
            data.get("id_patient"),
            data.get("id_rdv"),
            data.get("paiement_effectue")
        ))
        conn.commit()
        return jsonify({"success": True, "message": "Paiement ajouté avec succès"})


    except mysql.connector.Error as e:
        print(str(e))
        return jsonify({"success": False, "message": f"Erreur MySQL : {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@routes4.route('/charger_paiement', methods=['GET'])
def charger_paiement():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)

        query="""SELECT 
    paiement.id_paiement,
    patient.nom, 
    patient.prenom, 
    paiement.montant, 
    paiement.date_paiement,
    paiement.paiement_effectue,
    CASE 
        WHEN paiement.paiement_effectue = 1 THEN 'Effectué'
        ELSE 'Non effectué'
    END AS statut_paiement
FROM 
    paiement
JOIN 
    patient ON paiement.id_patient = patient.id_patient
WHERE 
    paiement.paiement_supprime = 0;
"""
        cursor.execute(query)
        resultat=cursor.fetchall()
        return jsonify(resultat)
    except mysql.connector.Error as e:
        print(str(e))
        return jsonify({"success": False, "message": f"Erreur MySQL : {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
@routes4.route('/delete_pai', methods=['GET'])
def delete_pai():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        index = request.args.get('index')
        
        query = """
            UPDATE paiement 
            SET paiement_supprime = 1 
            WHERE id_paiement = %s
        """
        cursor.execute(query, (index,))
        conn.commit()  

        return jsonify({"success": True, "message": "Paiement supprimé (soft delete) avec succès."})
        
    except mysql.connector.Error as e:
        print(str(e))
        return jsonify({"success": False, "message": f"Erreur MySQL : {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
@routes4.route('/charge_edi', methods=['POST'])
def ch_edit():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        index = request.args.get('index')
        query = """
        SELECT 
            p.id_paiement,
            p.date_paiement,
            p.montant,
            p.mode_paiement,
            p.paiement_effectue,
            
            pat.id_patient,
            pat.nom AS nom_patient,
            pat.prenom AS prenom_patient,
            
            rdv.id_rdv,
            rdv.date_heure,
            rdv.id_medecin
        FROM paiement p
        JOIN patient pat ON p.id_patient = pat.id_patient
        JOIN rendez_vous rdv ON p.id_rdv = rdv.id_rdv
        WHERE p.id_paiement = %s
        ORDER BY p.date_paiement DESC;
        """
        cursor.execute(query, (index,))
        result = cursor.fetchone()
        return jsonify(result)
    except mysql.connector.Error as e:
        print(str(e))
        return jsonify({"success": False, "message": f"Erreur MySQL : {str(e)}"}), 500


@routes4.route('/edit_pai/<int:index>', methods=['PUT'])
def edit_pai(index):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        data = request.get_json()

        query = """
        UPDATE paiement SET
            date_paiement = %s,
            montant = %s,
            paiement_effectue = %s
        WHERE id_paiement = %s
        """
        
        cursor.execute(query, (
            data['date_paiement'],
            data['montant'],
            data['paiement_effectue'],
            index
        ))
        conn.commit()
        return jsonify({"success": True})
    except mysql.connector.Error as e:
        print(str(e))
        return jsonify({"success": False, "message": f"Erreur MySQL : {str(e)}"}), 500