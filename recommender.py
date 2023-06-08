from attrs import define, field
from typing import Optional

from functools import reduce
import numpy as np
import pandas as pd

from scipy.spatial.distance import cdist
import surprise
from surprise import Dataset, Reader, SVD


@define
class GroupRecommender:
    _group_size: int
    _movies_data: pd.DataFrame = pd.read_feather("data/movies.feather")
    _starting_user_id: int = (
        pd.read_feather("data/history_ratings.feather").userId.unique().shape[0]
    )
    _movies_embeddings: Optional[pd.DataFrame] = field(init=False)
    _svd: Optional[SVD] = field(init=False)

    def __attrs_post_init__(self):
        if self._group_size <= 3:
            self._movies_embeddings = pd.read_feather("data/movies_embeddings.feather")
        else:
            self._svd = SVD(n_factors=17, n_epochs=30)

    def _preprocess_group_ratings(self, group_ratings: pd.DataFrame):
        ratings_with_movie_id: pd.DataFrame = group_ratings.merge(
            self._movies_data, left_on="movie", right_on="title"
        )
        numbered_usernames = zip(
            np.arange(
                self._starting_user_id,
                self._starting_user_id + group_ratings.username.unique().shape[0],
            ).astype(int),
            np.sort(group_ratings.username.unique()),
        )
        userid_mapping = {u: i for i, u in numbered_usernames}
        ratings_with_movie_id["userId"] = ratings_with_movie_id.username.apply(
            lambda x: userid_mapping[x]
        )
        return ratings_with_movie_id[["userId", "movieId", "rating"]]

    def _get_unwatched_movies_ids(self, group_ratings: pd.DataFrame) -> np.array:
        movie_ids: np.array = self._movies_data.movieId.values
        watch_history: pd.DataFrame = (
            group_ratings.groupby(by="userId").agg({"movieId": list}).reset_index()
        )
        watch_history["unwatched"] = watch_history.movieId.apply(
            lambda x: movie_ids[np.isin(movie_ids, x, invert=True)]
        )  # for each user get unwatched movies ids
        if self._group_size == 1:
            unwatched_movies_ids: np.array = watch_history.loc[0, "unwatched"]
        else:
            unwatched_movies_ids: np.array = np.array(
                reduce(np.intersect1d, watch_history.unwatched)
            )  # find ids of movies not watched by everyone in the group
        return unwatched_movies_ids

    def _get_users_embeddings(self, group_ratings: pd.DataFrame) -> pd.DataFrame:
        users_data = (
            group_ratings.groupby("userId")
            .agg({col: list for col in ["movieId", "rating"]})
            .reset_index()
        )
        users_data["movieId"] = users_data["movieId"].apply(np.array)
        users_data["rating"] = users_data["rating"].apply(np.array)
        users_data["embedding"] = users_data.apply(
            lambda row: np.mean(
                self._movies_embeddings[
                    self._movies_embeddings.movieId.isin(row["movieId"])
                ].embedding
                * row["rating"],
                axis=0,
            ),
            axis=1,
        )
        return users_data

    def get_embedding_based_recommendation(
        self, group_ratings: pd.DataFrame, unwatched_movies_data: pd.DataFrame
    ) -> np.array:
        unwatched_movies_embeddings: np.array = np.stack(
            unwatched_movies_data.merge(
                self._movies_embeddings, on="movieId"
            ).embedding.values
        )

        users_embeddings: pd.DataFrame = self._get_users_embeddings(group_ratings)
        avg_user_embedding: np.array = np.mean(
            users_embeddings.embedding, axis=0
        ).reshape(1, -1)

        dist_matrix = cdist(avg_user_embedding, unwatched_movies_embeddings).reshape(-1)
        closest_films = dist_matrix.argsort()[:10]
        top_movies = unwatched_movies_data.loc[closest_films, "movieId"].values

        return top_movies

    def get_svd_based_recommendation(
        self, group_ratings: pd.DataFrame, unwatched_movies_ids: np.array
    ) -> np.array:
        train_data: pd.DataFrame = pd.read_feather("data/history_ratings.feather")
        surprise_train_dataset: surprise.Dataset = Dataset.load_from_df(
            pd.concat([train_data[["userId", "movieId", "rating"]], group_ratings]),
            Reader(rating_scale=(1, 5)),
        )
        surprise_full_trainset: surprise.Trainset = (
            surprise_train_dataset.build_full_trainset()
        )
        self._svd.fit(surprise_full_trainset)

        movie_pseudorating: np.array = self._svd.bi[unwatched_movies_ids] + (
            self._svd.qi[unwatched_movies_ids]
            @ np.mean(self._svd.pu[self._starting_user_id :], axis=0)
        )
        top_movies = unwatched_movies_ids[np.argsort(-movie_pseudorating)][:10]

        return top_movies

    def make_recommendation(self, group_ratings: pd.DataFrame) -> pd.DataFrame:
        group_ratings = self._preprocess_group_ratings(group_ratings)
        unwatched_movies_ids: np.array = self._get_unwatched_movies_ids(group_ratings)
        if self._group_size <= 3:
            unwatched_movies_data: pd.DataFrame = self._movies_data[
                self._movies_data.movieId.isin(unwatched_movies_ids)
            ].reset_index(drop=True)
            top_movies: np.array = self.get_embedding_based_recommendation(
                group_ratings, unwatched_movies_data
            )
        else:
            top_movies: np.array = self.get_svd_based_recommendation(
                group_ratings, unwatched_movies_ids
            )

        return self._movies_data[self._movies_data.movieId.isin(top_movies)]
