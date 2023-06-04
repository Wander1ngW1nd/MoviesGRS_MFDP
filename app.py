import pandas as pd
import streamlit as st


movies_data = pd.read_feather('movies.feather')

st.markdown("# Movie Recommender")
num_users = st.slider("How many people do you want to get recommendation for?", 1, 7)

tabs = st.tabs([f"user_{i + 1}" for i in range(num_users)])
ratings_template = pd.DataFrame({"movie": pd.Series(dtype='str'), "rating": pd.Series(dtype='int')})
for i, user_tab in enumerate(tabs):
    with user_tab:
        with st.form(f"user_{i}"):
            user_ratings = st.data_editor(
                ratings_template,
                column_config={
                    "movie": st.column_config.SelectboxColumn(options=movies_data.title, required=True),
                    "rating": st.column_config.NumberColumn(min_value=1, max_value=5, required=True)
                },
                num_rows="dynamic"
            )
            if st.form_submit_button(label=f"Submit Input {i}"):
                if user_ratings.empty:
                    st.warning("Null values are not allowed")
                else:
                    st.write("""
                    Thanks! Your ratings are saved!\n
                    If you want to add more ratings or correct previous, just submit the form again!\n
                    Your ratings:
                    """)
                    st.write(user_ratings)
