import streamlit as st
import re
from collections import Counter
import docx
import nltk
from nltk.util import ngrams
from nltk.tokenize import sent_tokenize

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
    <div class="small-text">📈 Analyse sémantique des transcriptions des conférences</div>
""", unsafe_allow_html=True)

# Affichage du titre principal
st.title("Analyse sémantique des mots et expressions pertinents")
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

# Afficher les résultats
def display_results(word_counts, bigram_counts, text):
    st.subheader("Mots les plus fréquents et pertinents :")
    for word, count in word_counts:
        st.write(f"**{word.capitalize()}** ({count} occurrences)")
        trending_sentences = find_trending_sentences(text, word)
        if trending_sentences:
            st.write("Exemples de phrases :")
            for sentence in trending_sentences:
                st.write(f"- {sentence}")
    
    st.subheader("Expressions composées les plus fréquentes :")
    for bigram, count in bigram_counts:
        expression = ' '.join(bigram).capitalize()
        st.write(f"**{expression}** ({count} occurrences)")
        trending_sentences = find_trending_sentences(text, ' '.join(bigram))
        if trending_sentences:
            st.write("Exemples de phrases :")
            for sentence in trending_sentences:
                st.write(f"- {sentence}")

# Liste des stop words
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

# Téléchargement du fichier
uploaded_file = st.file_uploader("Téléchargez un fichier Word (.docx)", type="docx")

if uploaded_file:
    # Charger et afficher le contenu du fichier
    text = load_docx(uploaded_file)

    # Ajouter un bouton pour lancer l'analyse sémantique
    if st.button("Lancer l'analyse sémantique"):
        # Prétraiter le texte
        text_cleaned = preprocess_text(text)

        # Extraire les bigrammes et mots fréquents
        bigram_counts = extract_bigrams(text_cleaned, stop_words)
        word_counts = count_word_occurrences(text_cleaned, stop_words)

        # Afficher les résultats
        display_results(word_counts, bigram_counts, text)

        # Exécuter la recherche du mot
        search_word_in_text(text, search_word)

        # Afficher un message de succès
        st.success("Analyse sémantique terminée avec succès!")
else:
    st.write("Veuillez télécharger un fichier Word pour analyser.")
