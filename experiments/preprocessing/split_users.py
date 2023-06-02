import pandas as pd


DATA_PATH = 'experiments/data/'
GROUP_SIZES = [2, 3, 4]
RANDOM_SEEDS = range(GROUP_SIZES[0], len(GROUP_SIZES) + GROUP_SIZES[0])


def split_users_by_groups() -> None:
    for i, group_size in enumerate(GROUP_SIZES):
        test_data = (
            pd.read_parquet(DATA_PATH + 'ratings_test.pq')
            .userId
            .drop_duplicates()
            .reset_index(drop=True)
        )

        unique_users = (
            pd.DataFrame(test_data)
            .sample(frac=1, random_state=RANDOM_SEEDS[i])
            .reset_index(drop=True)
        )

        users_count = unique_users.shape[0]
        if (unique_users.shape[0] % group_size) != 0:
            new_users_count = (users_count // group_size) * group_size
            unique_users = unique_users.iloc[:new_users_count, :]

        unique_users['group'] = [
            i // group_size for i in range(unique_users.shape[0])
        ]
        
        unique_users.to_parquet(DATA_PATH + f'group{group_size}.pq')

    return


if __name__ == "__main__":
    split_users_by_groups()
