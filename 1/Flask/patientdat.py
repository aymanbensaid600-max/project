from flask import Flask, jsonify, request,Blueprint
import mysql.connector
from datetime import datetime, timedelta
from collections import defaultdict
from conn import get_db_connection
  
routes5=Blueprint('lop',__name__)

@routes5.route('/charger', methods=['GET'])
def Affiche():
    conn = None
    cursor = None
    try:
        id_patient = request.args.get('id_patient')  # ID envoyé par Qt
        if not id_patient:
            return jsonify({"error": "id_patient manquant"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT id_patient,
                   nom,
                   prenom,
                   DATE_FORMAT(date_naissance, '%%Y-%%m-%%d') AS date_naissance,
                   sexe,
                   adresse,
                   email,
                   telephone
            FROM patient
            WHERE ISdelete = 0 AND id_patient = %s
        """
        cursor.execute(query, (id_patient,))
        resultats = cursor.fetchall()

        if resultats:
            print(resultats)
            return jsonify(resultats[0])  # Un seul patient attendu
        else:
            return jsonify({"error": "Patient non trouvé"}), 404

    except mysql.connector.Error as err:
        print("Erreur MySQL :", err)
        return jsonify({"error": str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@routes5.route('/historique_rdv/<int:id_patient>', methods=['GET'])
def historique_patient(id_patient):
    conn = None
    cursor = None
    try:
        conn =get_db_connection()
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
            SELECT date_suivi, observations, fichier_ordonnance
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
        print("patient:", patient)
        print("dossier:", dossier)
        print("suivis:", suivis)

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
@routes5.route('/getMede', methods=['GET'])
def Affichemed():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
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


jours_map = {
    'Lun': 0,
    'Mar': 1,
    'Mer': 2,
    'Jeu': 3,
    'Ven': 4,
    'Sam': 5,
    'Dim': 6
}
def filtrer_creneaux(creneaux_possibles, heures_occupees, pas_minutes=30):
    heures_occupees_dt = [datetime.strptime(h, "%H:%M") for h in heures_occupees]
    creneaux_valides = []

    for c in creneaux_possibles:
        c_dt = datetime.strptime(c, "%H:%M")
        conflit = False
        for rdv_dt in heures_occupees_dt:
            # Interdire créneaux dans l'intervalle [RDV - 30min ; RDV + 60min[
            if timedelta(minutes=-30) < (c_dt - rdv_dt) < timedelta(minutes=60):
                conflit = True
                break
        if not conflit:
            creneaux_valides.append(c)
    return creneaux_valides

def generate_creneaux(heure_debut, heure_fin, pas_minutes=30):
    creneaux = []
    current = datetime.combine(datetime.today(), heure_debut)
    end = datetime.combine(datetime.today(), heure_fin)
    while current < end:
        creneaux.append(current.strftime("%H:%M"))
        current += timedelta(minutes=pas_minutes)
    return creneaux

@routes5.route("/creneaux_disponibles", methods=["GET"])
def creneaux_disponibles():
    medecin_id = request.args.get("medecin_id")
    date_str = request.args.get("date")

    if not medecin_id or not date_str:
        return jsonify({"error": "Paramètres 'medecin_id' et 'date' requis"}), 400

    try:
        medecin_id = int(medecin_id)
        date_cible = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Format invalide pour medecin_id ou date"}), 400

    jour_semaine_index = date_cible.weekday()  # 0 = Lundi, ..., 6 = Dimanche

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Récupérer les horaires du médecin
    cursor.execute("SELECT horaires FROM medecin WHERE id_medecin = %s", (medecin_id,))
    row = cursor.fetchone()
    if not row or not row["horaires"]:
        cursor.close()
        conn.close()
        return jsonify({"creneaux": []})

    horaires_str = row["horaires"]
    creneaux_possibles = []

    blocs = horaires_str.split(";")  # ex: 'Lun-Ven 09:00-17:00;Sam 10:00-14:00'
    for bloc in blocs:
        try:
            bloc = bloc.strip()
            jour_part, heure_part = bloc.split(" ")
            jours = jour_part.split("-")
            heure_debut_str, heure_fin_str = heure_part.split("-")
            heure_debut = datetime.strptime(heure_debut_str, "%H:%M").time()
            heure_fin = datetime.strptime(heure_fin_str, "%H:%M").time()

            # Cas 'Lun-Ven'
            if len(jours) == 2:
                debut_jour = jours_map[jours[0]]
                fin_jour = jours_map[jours[1]]
                if debut_jour <= jour_semaine_index <= fin_jour:
                    creneaux_possibles += generate_creneaux(heure_debut, heure_fin)
            # Cas 'Sam'
            elif len(jours) == 1:
                if jours_map[jours[0]] == jour_semaine_index:
                    creneaux_possibles += generate_creneaux(heure_debut, heure_fin)
        except Exception as e:
            continue

    # Récupérer rendez-vous pris à cette date
    query_rdv = """
        SELECT date_heure FROM rendez_vous
        WHERE id_medecin = %s
        AND DATE(date_heure) = %s
        AND statut != 'Annulé'
    """
    cursor.execute(query_rdv, (medecin_id, date_cible))
    rdvs = cursor.fetchall()
    heures_occupees = [r['date_heure'].strftime("%H:%M") for r in rdvs]

    creneaux_libres = filtrer_creneaux(creneaux_possibles, heures_occupees)

    cursor.close()
    conn.close()
    print(creneaux_libres)
    return jsonify({"creneaux": creneaux_libres})
@routes5.route('/prendre_rdv', methods=['POST'])
def ajouter_rendezvous():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    data = request.get_json()
    print("DATA REÇUE:", data)

    try:
        # Récupérer date et heure séparément
        date_str = data.get("date")      # ex: '2025-06-02'
        heure_str = data.get("heure")    # ex: '09:00'

        if not date_str or not heure_str:
            return jsonify({"success": False, "message": "Date ou heure manquante"}), 400

        date_heure_str = f"{date_str} {heure_str}:00"  # Exemple : '2025-06-02 09:00:00'

        # Convertir en objet datetime
        try:
            date_h = datetime.strptime(date_heure_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return jsonify({"success": False, "message": "Format de date/heure invalide"}), 400

        # Récupération des IDs
        patient_id = data.get("patient_id")
        medecin_id = data.get("medecin_id")

        if not all([patient_id, medecin_id]):
            print("ok")
            return jsonify({"success": False, "message": "ID patient ou médecin manquant"}), 400
            
        # Insertion dans la table rendez_vous
        query = """
            INSERT INTO rendez_vous (date_heure, statut, id_patient, id_medecin)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (
            date_h.strftime("%Y-%m-%d %H:%M:%S"),
            "Confirmé",  # ou "en attente", selon besoin
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
@routes5.route('/get_paiements_patient', methods=['POST'])
def get_paiements_patient():
    data = request.get_json()
    id_patient = data.get("id_patient")

    if not id_patient:
        return jsonify({"error": "id_patient est requis"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
    p.id_paiement,
    p.date_paiement,
    p.montant,
    p.paiement_effectue,
    f.id_facture,
    f.date_emission,
    f.montant AS montant_facture,
    s.observations
FROM paiement p
LEFT JOIN facture f ON p.id_paiement = f.id_paiement
LEFT JOIN suivi_medical s ON p.id_rdv = s.id_rdv
WHERE p.id_patient = %s
ORDER BY p.date_paiement DESC;


        """
        cursor.execute(query, (id_patient,))
        paiements = cursor.fetchall()

        results = []
        for p in paiements:
            results.append({
                "id_paiement": str(p["id_paiement"]),
                "date_paiement": p["date_paiement"].strftime("%Y-%m-%d") if p["date_paiement"] else "",
                "montant": float(p["montant"]),
                "observation": p['observations'],
                "statut": "Payé" if p["paiement_effectue"] else "En attente",
                "status": "Payé" if p["paiement_effectue"] else "En attente"
            })

        cursor.close()
        conn.close()
        print(results)
        return jsonify(results)
    
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    
@routes5.route('/get_statuts_paiement',methods=['GET'])
def get_statuts_paiement():
    data = request.get_json()
    id_patient = data.get("id_patient")
    if not id_patient:
        return jsonify({"error": "id_patient est requis"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
           SELECT
    SUM(CASE WHEN paiement_effectue = 1 THEN montant ELSE 0 END) AS total_paye,
    SUM(CASE WHEN paiement_effectue=0 THEN montant ELSE 0 END) AS total_non_paye
FROM paiement
WHERE id_patient = %s;
        """
        cursor.execute(query, (id_patient,))
        stat = cursor.fetchone()
        cursor.close()
        conn.close()
       
        return jsonify(stat)
    
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

