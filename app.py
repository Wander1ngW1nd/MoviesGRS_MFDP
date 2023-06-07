import pandas as pd
import streamlit as st


def get_user_ratings(username: str) -> pd.DataFrame:
    with st.form(username):
        user_ratings: pd.DataFrame = st.data_editor(
            pd.DataFrame(
                {"movie": pd.Series(dtype="str"), "rating": pd.Series(dtype="int")}
            ),
            column_config={
                "movie": st.column_config.SelectboxColumn(
                    options=movies_data.title, required=True
                ),
                "rating": st.column_config.NumberColumn(
                    min_value=1, max_value=5, required=True
                ),
            },
            num_rows="dynamic",
        )
        if st.form_submit_button():
            if user_ratings.empty:
                st.warning("Null values are not allowed")
            else:
                st.write(
                    """
                Thanks! Your ratings are saved!\n
                If you want to add more ratings or correct previous, just submit the form again!\n
                """
                )
                # st.write(user_ratings)

        user_ratings["username"] = username
        user_ratings.set_index(["username", "movie"], inplace=True)
        return user_ratings


def get_group_ratings(usernames) -> pd.DataFrame:
    group_ratings = pd.DataFrame(
        {
            "username": pd.Series(dtype="str"),
            "movie": pd.Series(dtype="str"),
            "rating": pd.Series(dtype="int"),
        }
    ).set_index(["username", "movie"])

    tabs = st.tabs(usernames)
    for i, username in enumerate(usernames):
        with tabs[i]:
            user_ratings: pd.DataFrame = get_user_ratings(username)
            group_ratings = pd.concat(
                [
                    group_ratings[~group_ratings.index.isin(user_ratings.index)],
                    user_ratings,
                ]
            )

    return group_ratings


if __name__ == "__main__":
    movies_data: pd.DataFrame = pd.read_feather("movies.feather")

    st.markdown("# Movie Recommender")

    num_users: int = st.slider(
        "How many people do you want to get recommendation for?", 1, 7
    )

    usernames = [f"user_{i + 1}" for i in range(num_users)]

    group_ratings = get_group_ratings(usernames)

    if group_ratings.index.unique(level="username").values.shape[0] == len(usernames):
        st.write(group_ratings)
        st.button(label="Get recommendations")
