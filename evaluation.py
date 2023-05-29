from functools import reduce
import numpy as np
import pandas as pd
from sklearn.metrics import ndcg_score


def generate_recommendations(make_recommendations, users_watch_history_test, unwatched):
    for group in [f'group{i}' for i in range(5, 8)]:
        group_unwatched = (
            unwatched
            .groupby(by=group)
            .agg({
                'userId': list,
                'unwatched': lambda x: np.array(reduce(np.intersect1d, x))
            })
            .reset_index()
        )
        group_unwatched['userId'] = group_unwatched.userId.apply(np.array)
        group_unwatched[f'{group}_rec'] = group_unwatched.apply(make_recommendations, axis=1)
        
        users_watch_history_test = users_watch_history_test.merge(group_unwatched[[group, f'{group}_rec']], on=group)
    
    return users_watch_history_test


def get_rating(row, group):
    return np.array([
        np.array(row.rating)[row.movieId == x].astype(int)[0] 
        if np.sum(row.movieId == x) else 0 
        for x in row[f'{group}_rec']     
    ])


def get_relevance(users_watch_history_test, group):
    users_watch_history_test[f'{group}_relevance'] = (
        users_watch_history_test
        .apply(lambda row: np.isin(row[f'{group}_rec'], row['movieId']).astype(int), axis=1)
    )
    return users_watch_history_test


def calc_P_k(users_watch_history_test, group):
    users_watch_history_test[f'{group}_P_k'] = (
        users_watch_history_test[f'{group}_relevance']
        .apply(lambda x: np.cumsum(x) * x / np.arange(1, len(x) + 1), 2)    
    )
    users_watch_history_test[f'{group}_P_k'] = (
        users_watch_history_test
        .apply(lambda row: row[f'{group}_P_k'].sum() / min(len(row['movieId']), len(row[f'{group}_rec'])), axis=1)
    )
    users_watch_history_test[f'{group}_P_k'] = (
        users_watch_history_test[f'{group}_P_k']
        .apply(lambda x: np.around(x, 2))
    )
    return users_watch_history_test


def calc_ndcg(users_watch_history_test, group):
    users_watch_history_test[f'{group}_rec_ratings'] = (
        users_watch_history_test
        .apply(lambda x: get_rating(x, group), axis=1)
    )

    users_watch_history_test['pseudo_model_output'] = (
        users_watch_history_test[f'{group}_rec']
        .apply(lambda x: [(len(x) - i) for i in range(len(x))])
    )

    users_watch_history_test[f'{group}_NDCG_k'] = (
        users_watch_history_test.apply(
            lambda row: ndcg_score([row[f'{group}_rec_ratings']], [row['pseudo_model_output']]),
            axis=1
        )
    )
    return users_watch_history_test


def evaluate_recommendations(users_watch_history_test):
    metrics_results = {}

    for group in [f'group{i}' for i in range(5, 8)]:
        
        users_watch_history_test = get_relevance(users_watch_history_test, group)

        users_watch_history_test = calc_P_k(users_watch_history_test, group)

        metrics_name = f"MAP_{group}"
        metrics_value = (
            users_watch_history_test
            .groupby(by=group)
            [f'{group}_P_k']
            .mean()
            .mean()
        )
        
        metrics_results[metrics_name] = metrics_value

        users_watch_history_test = calc_ndcg(users_watch_history_test, group)

        metrics_name = f"NDCG_{group}"
        metrics_value = (
            users_watch_history_test
            .groupby(by=group)
            [f'{group}_NDCG_k']
            .mean()
            .mean()
        )
        
        metrics_results[metrics_name] = metrics_value

    metrics_results_2d = {}
    for res in metrics_results:
        m, g = res.split('_')
        metrics_results_2d[m] = {**metrics_results_2d.get(m, {}), **{g: metrics_results[res]}}

    return pd.DataFrame(metrics_results_2d)
