import streamlit as st
import re
from collections import Counter
import docx
import nltk
from nltk.util import ngrams
from nltk.tokenize import sent_tokenize
from fpdf import FPDF
import io
import os

# Configuration de la page
st.set_page_config(layout="wide", initial_sidebar_state="expanded")
nltk.download('punkt')  # Assurez-vous de télécharger 'punkt'

# Appliquer des styles CSS personnalisés
st.markdown("""
    <style>
    [data-testid="stSidebarContent"] {
        color: grey;
        background-color: #FEFEFE;
    }
    .stApp {
        background-color: #EBF4F7;
    }
    .main-container {
        background-color: #FFFFFF;
        border-radius: 10px;
        font-family: 'Arial';
    }
    .col-container {
        background-color: #FFFBEC;
        border-radius: 10px;
    }
    div.stButton > button {
        background-color: #EFE9FF;
        color: black;
        padding: 10px 20px;
        border-radius: 10px;
        border: none;
    }
    .header-text {
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# Affichage de l'alerte et du champ de recherche en haut
st.markdown("""
    <style>
    .alert-band {
        background-color: #F6F6F6;
        padding: 10px;
        border-radius: 10px;
        align-items: center;
        justify-content: center;
        font-size: 13x;
        color: black;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
    <div class="alert-band">
        <span class="page-title-name-user">Yvell Mvoumbi</span> <span class="emoji">🔔</span>
    </div>
""", unsafe_allow_html=True)

# Champ de saisie pour la recherche de mots en haut de la page
search_word = st.text_input("Entrez un mot pour rechercher dans le texte", "")

# Barre latérale
st.sidebar.title("Menu")
st.sidebar.markdown("""
    <div class="small-text">📈 Analyse sémantique des conférences</div>
""", unsafe_allow_html=True)

# Affichage du titre principal
st.title("Analyse sémantique des Mots et Expressions Pertinents dans une Conférence")
st.markdown("""
    <div class="page-title">👋 Bonjour, <span class="page-title-name-user">Yvell Mvoumbi</span></div>
""", unsafe_allow_html=True)

# Fonction pour charger le document Word et extraire le texte
def load_docx(file):
    doc = docx.Document(file)
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    return ' '.join(text)

# Fonction pour nettoyer et filtrer le texte
def preprocess_text(text):
    # Nettoyer le texte (supprimer les caractères non alphanumériques)
    return re.sub(r'\W+', ' ', text.lower())

# Extraire les bigrammes
def extract_bigrams(text, stop_words):
    words = [word for word in text.split() if word not in stop_words]
    bigrams = ngrams(words, 2)
    return Counter(bigrams).most_common(10)

# Compter les occurrences des mots individuels
def count_word_occurrences(text, stop_words):
    words = text.split()
    filtered_words = [word for word in words if word not in stop_words]
    return Counter(filtered_words).most_common(20)

# Segmenter les phrases
def simple_sent_tokenize(text):
    return re.split(r'(?<=[.!?]) +', text)

# Trouver les phrases contenant des mots pertinents
def find_trending_sentences(text, word_or_phrase):
    sentences = simple_sent_tokenize(text)
    relevant_sentences = [sentence for sentence in sentences if word_or_phrase in sentence.lower()]
    return relevant_sentences[:3]

# Ajouter la fonctionnalité de filtre pour rechercher des mots
def search_word_in_text(text, word):
    if word:
        st.write(f"**Résultats de la recherche pour le mot : '{word}'**")
        sentences_with_word = [sentence for sentence in simple_sent_tokenize(text) if word.lower() in sentence.lower()]
        if sentences_with_word:
            for sentence in sentences_with_word:
                st.write(f"- {sentence}")
        else:
            st.write("Aucune occurrence trouvée.")
    else:
        st.write("Veuillez entrer un mot à rechercher.")

# Afficher les résultats et retourner le texte pour le PDF
def display_results(word_counts, bigram_counts, text):
    result_text = ""  # Cette variable contiendra le texte pour le PDF
    st.subheader("Mots les plus fréquents et pertinents :")
    result_text += "Mots les plus fréquents et pertinents :\n"
    
    for word, count in word_counts:
        result_text += f"{word.capitalize()} ({count} occurrences)\n"
        st.write(f"**{word.capitalize()}** ({count} occurrences)")
        trending_sentences = find_trending_sentences(text, word)
        if trending_sentences:
            st.write("Exemples de phrases :")
            result_text += "Exemples de phrases :\n"
            for sentence in trending_sentences:
                result_text += f"- {sentence}\n"
                st.write(f"- {sentence}")
    
    st.subheader("Expressions composées les plus fréquentes :")
    result_text += "\nExpressions composées les plus fréquentes :\n"
    for bigram, count in bigram_counts:
        expression = ' '.join(bigram).capitalize()
        result_text += f"{expression} ({count} occurrences)\n"
        st.write(f"**{expression}** ({count} occurrences)")
        trending_sentences = find_trending_sentences(text, ' '.join(bigram))
        if trending_sentences:
            st.write("Exemples de phrases :")
            result_text += "Exemples de phrases :\n"
            for sentence in trending_sentences:
                result_text += f"- {sentence}\n"
                st.write(f"- {sentence}")
    
    return result_text  # Retourne le texte pour le PDF

# Générer le fichier PDF à partir des résultats en utilisant une police prenant en charge l'UTF-8
def create_pdf(content):
    if content:  # Vérifier que le contenu n'est pas None ou vide
        pdf = FPDF()
        pdf.add_page()
        
        # Chemin vers la police DejaVu
        font_path = os.path.join(os.path.dirname(__file__), 'DejaVuSansCondensed.ttf')
        if not os.path.exists(font_path):
            st.error("Fichier de police introuvable. Assurez-vous que 'DejaVuSansCondensed.ttf' est dans le bon répertoire.")
            return None
        
        # Utilisation de DejaVu ou une autre police Unicode
        pdf.add_font('DejaVu', '', font_path, uni=True)
        pdf.set_font('DejaVu', '', 12)  # Utiliser la police DejaVu pour les caractères Unicode
        
        # Encoder le contenu en UTF-8
        for line in content.split('\n'):
            pdf.cell(200, 10, txt=line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
        return pdf
    else:
        st.error("Le contenu est vide, impossible de générer le PDF.")

stop_words = set([
    # Articles et pronoms
    "le", "la", "les", "et", "de", "du", "des", "en", "pour", "avec",
    "sur", "par", "à", "un", "une", "d", "l", "que", "qui", "est",
    "ce", "nous", "il", "elle", "ils", "elles", "ne", "pas", "mais",
    "aux", "dans", "on", "vous", "je", "qu", "si", "c", "n", "a", "ça",
    "y", "au", "plus", "fait", "va", "dire", "là", "ou", "alors", "être",
    "peut", "tout", "quand", "même", "sont", "très", "donc", "hui", "1",
    "intervenant", "aujourd", "été", "j'ai", "avez", "aussi", "s", "cette", "se", "ont", "m", "peu",
    "comme", "lorsque", "quand", "si", "puisque", "parce que", "afin que",
    "bien que", "quoique", "malgré que", "avant que", "sans que", "pour que",
    "depuis que", "dès que", "jusqu'à ce que", "à condition que",
    "pourvu que", "pendant que", "tandis que", "alors que", "où", "bien", "j", "ai",
    
    # Conjonctions de subordination
    "comme", "lorsque", "quand", "si", "puisque", "parce que", "afin que",
    "bien que", "quoique", "malgré que", "avant que", "sans que", "pour que",
    "depuis que", "dès que", "jusqu'à ce que", "à condition que",
    "pourvu que", "pendant que", "tandis que", "alors que", "où",
    
    # Verbes courants
    "avoir", "être", "faire", "aller", "pouvoir", "vouloir", "devoir",
    "falloir", "venir", "prendre", "mettre", "savoir", "voir", "croire",
    "trouver", "donner", "parler", "passer", "penser", "aimer", "demander", "était",
    
    # Mots de liaison
    "cependant", "toutefois", "d'ailleurs", "en effet", "de plus", "également",
    "enfin", "donc", "ainsi", "puis", "ensuite", "par ailleurs", "autrefois",
    
    # Adjectifs possessifs
    "mon", "ton", "son", "notre", "votre", "leur", "ma", "ta", "sa",
    "mes", "tes", "ses", "nos", "vos", "leurs"
])

# Fonction principale pour lancer l'analyse
def main():
    # Téléchargement du fichier
    uploaded_file = st.file_uploader("Téléchargez un fichier Word (.docx)", type="docx")
    
    if uploaded_file is not None:
        # Bouton pour lancer l'analyse
        if st.button("Lancer l'analyse sémantique"):
            with st.spinner("Analyse en cours..."):
                # Charger et prétraiter le texte
                text = load_docx(uploaded_file)
                text_cleaned = preprocess_text(text)
                
                # Extraire les bigrammes et compter les mots
                bigram_counts = extract_bigrams(text_cleaned, stop_words)
                word_counts = count_word_occurrences(text_cleaned, stop_words)
                
                # Afficher les résultats
                result_text = display_results(word_counts, bigram_counts, text)
                
                # Exécuter la recherche du mot
                if search_word:
                    search_word_in_text(text, search_word)
            
            st.success("Analyse terminée avec succès !")
            
            if result_text:  # Vérifier que result_text n'est pas vide
                # Ajouter un bouton pour télécharger le fichier PDF avec les résultats
                pdf = create_pdf(result_text)
                if pdf:
                    pdf_output = io.BytesIO()
                    pdf.output(pdf_output)
                    pdf_output.seek(0)
                    st.download_button(
                        label="Télécharger les résultats en PDF",
                        data=pdf_output,
                        file_name="resultat_analyse_semantique.pdf",
                        mime="application/pdf"
                    )
            else:
                st.error("Impossible de générer le PDF car le contenu est vide.")
    else:
        st.write("Veuillez télécharger un fichier Word pour analyser.")

# Appeler la fonction principale
if __name__ == "__main__":
    main()
