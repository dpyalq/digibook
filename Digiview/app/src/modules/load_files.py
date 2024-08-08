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


import os
import json


import pandas as pd
import streamlit as st


def select_json(output_folder):
    json_files = [f for f in os.listdir(output_folder) if f.endswith(".json")]
    selected_file = st.selectbox("Select a JSON file:", 
                            json_files
                            )
    with open(os.path.join(output_folder, selected_file), "r", encoding='utf-8') as document:
        data = json.load(document)
    return data


def select_df(json_data):
    df = pd.DataFrame(json_data['data'])
    df = pd.DataFrame({'username': json_data["data"]["username"],
                        'comment': json_data["data"]["comment"],
                        'emojis': [item[1] for item in json_data["data"]["comment_and_emojis"]],
                        'date_comment': json_data["data"]["date_comment"],
                        'likes_comment': json_data["data"]["likes_comment"],
                        'lang': json_data["data"]["lang"],
                        'emotion_comment': json_data["data"]["emotion_comment"],
                        'score_emotion': json_data["data"]["score_emotion"]}
                        )
    df['comment'].fillna('', inplace=True)
    df['emojis'] = df['emojis'].apply(lambda x: ''.join(x))
    df["likes_comment"] = df["likes_comment"].replace('', "0")
    df['score_emotion'] = pd.to_numeric(df['score_emotion'], errors='coerce')
    return df
