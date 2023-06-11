import pandas as pd
import streamlit as st

from recommender import GroupRecommender


def get_user_ratings(username: str) -> pd.DataFrame:
    with st.form(username):
        user_ratings: pd.DataFrame = st.data_editor(
            pd.DataFrame({"movie": pd.Series(dtype="str"), "rating": pd.Series(dtype="int")}),
            column_config={
                "movie": st.column_config.SelectboxColumn(options=movies_data.title, required=True),
                "rating": st.column_config.NumberColumn(min_value=1, max_value=5, required=True),
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
                Your ratings:
                """
                )
                st.write(user_ratings)

        user_ratings["username"] = username
        user_ratings.set_index(["username", "movie"], inplace=True)
        return user_ratings


def get_group_ratings(users: list[str]) -> pd.DataFrame:
    ratings = pd.DataFrame(
        {
            "username": pd.Series(dtype="str"),
            "movie": pd.Series(dtype="str"),
            "rating": pd.Series(dtype="int"),
        }
    ).set_index(["username", "movie"])

    tabs = st.tabs(users)
    for i, user in enumerate(users):
        with tabs[i]:
            user_ratings: pd.DataFrame = get_user_ratings(user)
            ratings = pd.concat(
                [
                    ratings[~ratings.index.isin(user_ratings.index)],
                    user_ratings,
                ]
            )
    st.write("Your group ratings:", ratings)
    return ratings


if __name__ == "__main__":
    movies_data: pd.DataFrame = pd.read_feather("data/movies.feather")

    st.markdown("# Movie Recommender")

    num_users: int = st.slider("How many people do you want to get recommendation for?", 1, 7)

    recommender = GroupRecommender(num_users)  # type: ignore [call-arg]
    usernames = [f"user_{i + 1}" for i in range(num_users)]

    group_ratings: pd.DataFrame = get_group_ratings(usernames).reset_index()
    included_users: int = group_ratings.username.unique().shape[0]
    if included_users == num_users:
        if st.button(label="Get recommendations"):
            st.write(recommender.make_recommendation(group_ratings))
