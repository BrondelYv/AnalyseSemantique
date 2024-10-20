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

# Affichage du titre principal
st.title("Analyse des Mots et Expressions Pertinents dans une Conférence")

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
stop_words = set([...])  # Ta liste de mots ici

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
