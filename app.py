import pandas as pd
import streamlit as st

st.markdown("# Movie Recommender")
num_users = st.slider("How many people do you want to get recommendation for?", 1, 7)

tabs = st.tabs([f"user_{i + 1}" for i in range(num_users)])
ratings_template = pd.DataFrame({"movie": pd.Series(dtype='str'), "rating": pd.Series(dtype='int')})
for i, user_tab in enumerate(tabs):
    with user_tab:
        with st.form(f"user_{i}"):
            user_ratings = st.data_editor(ratings_template, num_rows="dynamic")
            if st.form_submit_button(label=f"Submit Input {i}"):
                st.write("""
                Thanks! Your ratings are saved!\n
                If you want to add more, just submit the form one more time
                """)
                st.write(user_ratings)
