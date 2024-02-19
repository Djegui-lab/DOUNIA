import streamlit as st
import sqlite3

# Fonction pour créer la table dans la base de données s'il n'existe pas encore
def create_table():
    with sqlite3.connect('paiements.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paiements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_client TEXT,
                montant REAL
            )
        ''')

# Fonction pour enregistrer un paiement dans la base de données
def enregistrer_paiement(nom_client, montant):
    with sqlite3.connect('paiements.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO paiements (nom_client, montant) VALUES (?, ?)", (nom_client, montant))

# Fonction pour récupérer l'historique des paiements depuis la base de données
def get_historique_paiements():
    with sqlite3.connect('paiements.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM paiements")
        historique_paiements = cursor.fetchall()
    return historique_paiements

# Fonction pour supprimer un paiement par ID
def supprimer_paiement_par_id(paiement_id):
    with sqlite3.connect('paiements.db') as conn:
        cursor = conn.cursor()
        
        # Vérifier si l'ID existe dans la base de données
        cursor.execute("SELECT id FROM paiements WHERE id=?", (paiement_id,))
        existing_id = cursor.fetchone()
        
        if existing_id:
            # L'ID existe, procéder à la suppression
            cursor.execute("DELETE FROM paiements WHERE id=?", (paiement_id,))
            conn.commit()
            return True
        else:
            # L'ID n'existe pas dans la base de données
            return False

# Fonction pour réinitialiser l'auto-incrémentation de l'ID après avoir supprimé tous les enregistrements
def reset_autoincrement():
    # Connexion à la base de données en mode isolation_level=None pour éviter les transactions
    with sqlite3.connect('paiements.db', isolation_level=None) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM paiements")
        cursor.execute("VACUUM")
        conn.commit()

# Créer la table au démarrage de l'application
create_table()



# Titre de l'application
st.title("Gestion des paiements - Cafétéria")
st.subheader("AUTEUR : DOUNIA EL AKRAMI 🚗")

# Section pour entrer les détails du paiement
st.header("Nouveau Paiement")
# Ajouter du CSS personnalisé pour définir les couleurs de fond
st.markdown(
    """
    <style>
        body {
            background-color: #3EE0DD;  /* Couleur de fond globale */
            color: #C71585;  /* Couleur du texte global (blanc) */
        }

        .stTextInput {
            background-color: #404040;  /* Couleur de fond du champ de saisie (gris foncé) */
            color: #C71585;  /* Couleur du texte du champ de saisie (blanc) */
        }

        .stButton {
            background-color: #C71585; /* Couleur de fond du bouton (bleu-vert) */
            color: #C71585;  /* Couleur du texte du bouton (blanc) */
        }

        .table {
            color: #FFFF00;  /* Couleur du texte dans la table (blanc) */
        }

        .sum-section, .average-section, .min-section, .max-section {
            background-color: #FF69B4; /* Couleur de fond pour les sections (rose) */
            color: #ffffff;  /* Couleur du texte pour les sections (blanc) */
        }

        .custom-button {
            background-color: #3EE0DD; /* Couleur de fond des boutons spécifiques */
            color: #ffffff;  /* Couleur du texte des boutons spécifiques (blanc) */
        }
    </style>
    """,
    unsafe_allow_html=True
)
# Entrée du nom du client
nom_client = st.text_input("Nom du client")

# Entrée du montant du paiement
montant_paiement = st.number_input("Montant du paiement", min_value=0.0)

# Bouton pour enregistrer le paiement
if st.button("Enregistrer Paiement", key="custom-button-enregistrer"):
    try:
        # Enregistrer le paiement dans la base de données
        enregistrer_paiement(nom_client, montant_paiement)
        st.success(f"Paiement de {montant_paiement}€ enregistré pour {nom_client}")
    except Exception as e:
        st.error(f"Erreur lors de l'enregistrement du paiement : {e}")

# Section pour supprimer un paiement par ID
st.header("Supprimer Paiement par ID")

# Entrée de l'ID du paiement à supprimer
paiement_id_suppression = st.number_input("ID du paiement à supprimer", min_value=1)

# Bouton pour supprimer le paiement par ID
if st.button("Supprimer Paiement par ID", key="custom-button-supprimer"):
    try:
        # Appeler la fonction pour supprimer le paiement
        if supprimer_paiement_par_id(paiement_id_suppression):
            st.success(f"Paiement avec l'ID {paiement_id_suppression} supprimé avec succès.")
        else:
            st.warning(f"Aucun paiement trouvé avec l'ID {paiement_id_suppression}.")
    except Exception as e:
        st.error(f"Erreur lors de la suppression du paiement : {e}")

# Bouton pour réinitialiser la base de données (supprimer tous les enregistrements et réinitialiser l'auto-incrémentation de l'ID)
if st.button("Réinitialiser la Base de Données", key="custom-button-reinitialiser"):
    try:
        reset_autoincrement()
        st.success("Base de données réinitialisée avec succès.")
    except Exception as e:
        st.error(f"Erreur lors de la réinitialisation de la base de données : {e}")

# Section pour afficher l'historique des paiements
st.header("Historique des Paiements")

# Récupérer l'historique des paiements depuis la base de données
historique_paiements = get_historique_paiements()

# Afficher une table d'historique des paiements
st.table(historique_paiements)

# Section pour afficher la somme des paiements
st.header("Somme des Paiements")
sum_paiements = sum([montant for _, _, montant in historique_paiements])
st.markdown(f'<div class="sum-section">{sum_paiements} DHS</div>', unsafe_allow_html=True)

# Section pour afficher la moyenne des paiements
st.header("Moyenne des Paiements")
average_paiements = sum_paiements / len(historique_paiements) if historique_paiements else 0
st.markdown(f'<div class="average-section">{average_paiements} DHS</div>', unsafe_allow_html=True)

# Section pour afficher le montant minimum des paiements et le nom du client associé
st.header("Minimum des Paiements")
min_paiement = min(historique_paiements, key=lambda x: x[2]) if historique_paiements else (0, '', 0)
st.markdown(f'<div class="min-section">{min_paiement[2]} DHS pour le client {min_paiement[1]}</div>', unsafe_allow_html=True)

# Section pour afficher le montant maximum des paiements et le nom du client associé
st.header("Maximum des Paiements")
max_paiement = max(historique_paiements, key=lambda x: x[2]) if historique_paiements else (0, '', 0)
st.markdown(f'<div class="max-section">{max_paiement[2]} DHS pour le client {max_paiement[1]}</div>', unsafe_allow_html=True)
