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


def set_page_config():
    st.set_page_config(
        page_title="interactive-dashboard",
        page_icon= ":bar_chart:",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def header():
    with st.container():
        st.title("Interactive dashboard :bar_chart:", anchor=False)
        st.write("---")
