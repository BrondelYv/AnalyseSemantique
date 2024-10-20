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

# Champ de saisie pour la recherche de mots en haut de la page
search_word = st.text_input("Entrez un mot pour rechercher dans le texte", "")

# Barre latérale
st.sidebar.title("Menu")
st.sidebar.markdown("📈 Analyse sémantique des conférences")

# Affichage du titre principal
st.title("Analyse sémantique des Mots et Expressions Pertinents dans une Conférence")
st.write("Bonjour, Yvell Mvoumbi")

# Fonction pour charger le document Word et extraire le texte
def load_docx(file):
    doc = docx.Document(file)
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    return ' '.join(text)

# Fonction pour nettoyer et filtrer le texte
def preprocess_text(text):
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

# Ajouter la fonctionnalité de filtre pour rechercher des mots
def search_word_in_text(text, word):
    if word:
        st.write(f"Résultats de la recherche pour le mot : '{word}'")
        sentences_with_word = [sentence for sentence in sent_tokenize(text) if word.lower() in sentence.lower()]
        if sentences_with_word:
            for sentence in sentences_with_word:
                st.write(f"- {sentence}")
        else:
            st.write("Aucune occurrence trouvée.")
    else:
        st.write("Veuillez entrer un mot à rechercher.")

# Générer le fichier PDF à partir des résultats en utilisant une police prenant en charge l'UTF-8
def create_pdf(content):
    if content:
        pdf = FPDF()
        pdf.add_page()
        font_path = os.path.join(os.path.dirname(__file__), 'DejaVuSansCondensed.ttf')
        if not os.path.exists(font_path):
            st.error("Fichier de police introuvable. Assurez-vous que 'DejaVuSansCondensed.ttf' est dans le bon répertoire.")
            return None
        pdf.add_font('DejaVu', '', font_path, uni=True)
        pdf.set_font('DejaVu', '', 12)
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
    uploaded_file = st.file_uploader("Téléchargez un fichier Word (.docx)", type="docx")
    
    if uploaded_file is not None:
        if st.button("Lancer l'analyse sémantique"):
            with st.spinner("Analyse en cours..."):
                text = load_docx(uploaded_file)
                text_cleaned = preprocess_text(text)
                bigram_counts = extract_bigrams(text_cleaned, stop_words)
                word_counts = count_word_occurrences(text_cleaned, stop_words)
                result_text = "\n".join([f"{word} ({count} occurrences)" for word, count in word_counts])
                if search_word:
                    search_word_in_text(text, search_word)
            st.success("Analyse terminée avec succès !")
            if result_text:
                pdf = create_pdf(result_text)
                if pdf:
                    pdf_output = io.BytesIO()
                    pdf.output(pdf_output)
                    pdf_output.seek(0)
                    st.download_button("Télécharger les résultats en PDF", pdf_output, "resultat_analyse_semantique.pdf", "application/pdf")
            else:
                st.error("Impossible de générer le PDF car le contenu est vide.")
    else:
        st.write("Veuillez télécharger un fichier Word pour analyser.")

if __name__ == "__main__":
    main()
