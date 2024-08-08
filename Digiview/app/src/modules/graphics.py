# Digiview is part of the DIGIBOOK collection.
# DIGIBOOK Copyright (C) 2024 Daniel Alcalá.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from os import path
import re
from collections import Counter


import pandas as pd
import streamlit as st
import nltk
import plotly.express as px
from stop_words import get_stop_words
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import emoji
import emojis


stopwords_add = ["''", "``", '', ',', '.', '...', '!', '?', 'y', 'si']


def pie_chart_emotions(df): 
    try:
        emotion = df["emotion_comment"]
        emotion_counts = emotion.value_counts()
        emotion_counts_df = pd.DataFrame({
                                'Emoción': emotion_counts.index, 
                                'Cantidad': emotion_counts.values
                                })
        color_mapping = {
            'POS': '#8DC63F',
            'NEG': '#FF5733',
            'NEU': ' #A0A0A0'
        }
        fig = px.pie(emotion_counts_df,
                    names='Emoción',
                    values='Cantidad',
                    title='Emociones en comentarios',
                    color='Emoción',
                    color_discrete_map=color_mapping
                    )
        fig.update_layout(
            width=400,
            height=500
        )
        st.plotly_chart(fig)
    except Exception:
        pass


def box_plot_emotions(df):
    try:

        fig = px.box(df, 
                    y="score_emotion",
                    points="all",
                    title="Distribución de puntuación de emociones"
                    )
        fig.update_yaxes(title_text="Score emotion")
        fig.add_annotation(
            text="NEG",
            x=1,
            y=-1.1,
            showarrow=False,
        )
        fig.add_annotation(
            text="NEU",
            x=1,
            y=0.1,
            showarrow=False,
        )
        fig.add_annotation(
            text="POS",
            x=1,
            y=1.1,
            showarrow=False,
        )
        fig.update_layout(
            width=400,
            height=500
        )
        st.plotly_chart(fig)
    except Exception:
        pass


def bar_chart_top_words(df, num_words=10):
    try:
        nltk.data.path.append('app/static/nltk_data')
        list_words = df['comment'].astype(str).str.lower()
        list_words = list_words.apply(nltk.tokenize.word_tokenize)
        # Lista de palabras a excluir
        stop_words_en = get_stop_words('en')
        stop_words_es = get_stop_words('es')
        stopwords = stop_words_en + stop_words_es + stopwords_add
        list_words = list_words.apply(lambda x: [word for word in x if word not in stopwords])
        # Obtener frecuencia de cada palabra
        words = list_words.tolist()
        words = [word for list_ in words for word in list_]
        word_dist = nltk.FreqDist(words)
        top_words_df = pd.DataFrame(word_dist.most_common(num_words), 
                                columns=['words', 'frequency']
                                )
        # Crear una gráfica de barras con Plotly
        fig = px.bar(
                top_words_df,
                x=top_words_df['words'],
                y=top_words_df['frequency'],
                labels={'x': 'Palabra', 'y': 'Frecuencia'},
                title=f'Top {num_words} de palabras más usadas'
            )
        fig.update_layout(
            width=500,
            height=500
        )
        st.plotly_chart(fig)
    except ValueError:
        fig = px.bar(
            labels={'x': 'Palabra', 'y': 'Frecuencia'},
            title=f'Top {num_words} de palabras más usadas'
        )
        st.plotly_chart(fig)


def bar_chart_top_emoji(df, num_emojis=10):
    try:
        # Crear una gráfica de barras con Plotly
        nltk.data.path.append('app/static/nltk_data')
        df['emojis'] = df['emojis'].apply(lambda x: ''.join(x))
        list_emojis = df['emojis'].astype(str).str.lower()
        list_emojis = list_emojis.apply(nltk.tokenize.word_tokenize)
        list_emojis = list_emojis.tolist()
        list_emojis = [emoji for list_ in list_emojis for emoji in list_]
        str_demojize = list(map(lambda i: emoji.demojize(i), list_emojis))
        str_demojize = ''.join(str_demojize)
        list_demojize = re.findall(r':[A-Za-z_]+:', str_demojize)
        emojis_str = list(map(lambda i: emoji.emojize(i, variant="emoji_type"), list_demojize))
        emojis_str = ''.join(emojis_str)
        emoji_frequencies = Counter(emojis.iter(emojis_str))
        top_emojis_df = pd.DataFrame(emoji_frequencies.most_common(10), 
                                     columns=['emojis', 'frequency']
                                    )
        fig = px.bar(
                top_emojis_df,
                x=top_emojis_df['emojis'],
                y=top_emojis_df['frequency'],
                labels={'x': 'Palabra', 'y': 'Frecuencia'},
                title=f'Top {num_emojis} de emojis más usadas'
            )
        fig.update_layout(
            width=500,
            height=500
        )
        st.plotly_chart(fig)
    except ValueError:
        fig = px.bar(
            labels={'x': 'Palabra', 'y': 'Frecuencia'},
            title=f'Top {num_emojis} de emojis más usadas'
        )
        st.plotly_chart(fig)


def wordcloud_words(df):
    try:
        nltk.data.path.append('app/static/nltk_data')
        list_words = df['comment'].astype(str).str.lower()
        list_words = list_words.apply(nltk.tokenize.word_tokenize)
        # Lista de palabras a excluir
        stop_words_en = get_stop_words('en')
        stop_words_es = get_stop_words('es')
        stopwords = stop_words_en + stop_words_es + stopwords_add
        list_words = list_words.apply(lambda x: [word for word in x if word not in stopwords])
        words = list_words.tolist()
        words = [word for list_ in words for word in list_]
        # Crear un objeto WordCloud
        wordcloud = WordCloud(
                        width=800, 
                        height=500, 
                        background_color='white').generate(' '.join(words)
                    )
        # Crear una figura de Matplotlib
        st.markdown('<br> <center> __Nube de palabras__ </center>' , unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    except ValueError:
        st.markdown('<br> <center> __Nube de palabras__ </center>' , unsafe_allow_html=True)


def wordcloud_emojis(df):
    try:
        nltk.data.path.append('app/static/nltk_data')
        df['emojis'] = df['emojis'].apply(lambda x: ''.join(x))
        list_emojis = df['emojis'].astype(str).str.lower()
        list_emojis = list_emojis.apply(nltk.tokenize.word_tokenize)
        list_emojis = list_emojis.tolist()
        list_emojis = [emoji for list_ in list_emojis for emoji in list_]
        str_demojize = list(map(lambda i: emoji.demojize(i), list_emojis))
        str_demojize = ''.join(str_demojize)
        list_demojize = re.findall(r':[A-Za-z_]+:', str_demojize)
        emojis_str = list(map(lambda i: emoji.emojize(i, variant="emoji_type"), list_demojize))
        emojis_str = ''.join(emojis_str)
        emoji_frequencies = Counter(emojis.iter(emojis_str))
        total_count = sum(emoji_frequencies.values())
        emoji_probability = {emoji: count/total_count for emoji, count in emoji_frequencies.items()}
        # Crear un objeto WordCloud
        wordcloud = WordCloud(
                        font_path='app/static/fonts/NotoEmoji-VariableFont_wght.ttf',
                        width=800, 
                        height=500, 
                        background_color='white')
        wordcloud.generate_from_frequencies(emoji_probability)
        st.markdown('<br> <center> __Nube de emoji__ </center>' , unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    except ValueError:
        st.markdown('<br> <center> __Nube de emoji__ </center>' , unsafe_allow_html=True)
