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


import streamlit as st


def filter_words():
    if 'words_filter' not in st.session_state:
        st.session_state.words_filter = []

    word = st.text_input("Enter a word to filter comments", 
                            value="", 
                            placeholder="Enter a word to filter comments",
                            label_visibility="visible"
                        )
        
    if word.strip() != "" and word.strip() != "Write your word" and word not in st.session_state.words_filter:
        st.session_state.words_filter.append(word)

    container2 = st.container()
    
    if st.button("Reset", key="rest"):
        st.session_state.words_filter = []
        st.success("The list has been successfully reset.")

    options = container2.multiselect(
        'Filter by words',
        st.session_state.words_filter,
        st.session_state.words_filter
    )

    return options
    


def filter_emotion():
    genre = st.radio(
        "Filter emotion",
        ["ALL", "POS", "NEU", "NEG"],
        captions = None
        )
    if genre != 'ALL':
        emotio = []
        emotio.append(genre)
        return emotio
    else:
        emotion = ['POS', 'NEU', 'NEG']
        return emotion
