---
title: Movies Group Recommender System
emoji: 🎬
colorFrom: purple
colorTo: purple
sdk: streamlit
sdk_version: 1.23.0
app_file: src/app.py
pinned: false
---

# Movies Group Recommender System

Application making personalized movie recommendations for groups of users. Based on each group member’s watch history, it provides the tailored watch list, taking into account preferences of everyone.

## Demo
![](application_demo.gif)

## Installation

1\. Install [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [docker engine](https://docs.docker.com/engine/install/)

2\. Clone the project:

```bash
git clone https://github.com/Wander1ngW1nd/MoviesGRS_MFDP
```

3\. Build an image:

```bash
docker build -t movies_grs_image MoviesGRS_MFDP
```

4\. Run application container:

```bash
docker run --name movies_grs_app -dp 8501 movies_grs_image
```

5\. Figure out which port was assigned to your application:

```bash
docker port movies_grs_app
```
&nbsp; &nbsp; You will see the similar output:

```
8501/tcp -> 0.0.0.0:<your_port_number>
```

6\. Go to:
```
http://0.0.0.0:<your_port_number>
```

Now you can use the app!

## Usage

For illustration of the steps listed below you can watch [demo](#demo)

1\. Choose the size of your group (1-7 are currently supported). You will see tabs responding to each group’s member

2\. For each member of the group:

1. Fill in the table inside the corresponding tab with ratings of the movies reflecting your preferences best
    - The more ratings — the better
    - You can add any number of movies or delete them
    - You cannot add empty ratings table
2. Submit your ratings
    - If you want to change submitted ratings, you can just refill the table and submit it again

&nbsp; &nbsp; You will be able to see all the submitted ratings on the bottom of the page

3\. Click **Get recommendation** button on the bottom of the page to get recommendations.
  - **Get recommendation** button will not appear until all the ratings are submitted
  - If your group size ≥ 4, it can take some time (~1 min) to make recommendations


## Under-the-hood description

Application source files are structured as follows:

```
src
├── app.py
├── recommender.py
└── data
    ├── history_ratings.feather
    ├── movies_embeddings.feather
    └── movies.feather
```

[app.py](src/app.py) contains front-end part of the application made with [streamlit](https://docs.streamlit.io/). This is the entry-point file of the project. It defines the application interface and performs base users’ input processing. The supposed way of its usage if described in the [corresponding section](#usage). 

[recommender.py](src/recommender.py) contains the GroupRecommender class, generating recommendations based on users’ ratings. It takes the group size on instantiation, as this parameter defines the recommendation algorithm used, by the following way (described in pseudocode):

```python
if group_size < 4:
	make_recommendation_based_on_movie_embeddings()
else:
	make_recommendations_based_on_svd_decomposition()
```

So, there are 2 different algorithms. They both firstly represent users and movies in the same vector space, but do it in different ways:

- **Movie-embeddings-based** recommender firstly creates each group member profile. The profile is constructed as the mean of embeddings of movies watched by the user, weighted on their provided ratings. Movies embeddings were precomputed by passing their plots through pretrained `paraphrase-distilroberta-base-v1` from [SentenceTransformers](https://www.sbert.net/index.html) library and saved to [data/movies_embeddings.feather](data/movies_embeddings.feather).
- **SVD-based recommender** adds group members’ ratings to those stored in [data/history_ratings.feather](data/history_ratings.feather) and performs SVD decomposition of the resulting rating matrix, receiving users’ and movies’ vector representations.

Then both algorithms take the mean of group members’ profiles as the group profile representation, and find top-10 nearest movies in the embeddings space by euclidean distance.

Certain models, parameters and usage conditions choice is described in separate repository, [MoviesGRS_experiments_MFDP](https://github.com/Wander1ngW1nd/MoviesGRS_experiments_MFDP/tree/main).


## Development

### Dependencies Management

Project’s dependencies are managed by [poetry](https://python-poetry.org/). So, all the dependencies and configuration parameters are listed in [pyproject.toml](pyproject.toml). 

To install the dependencies, follow these steps:

1\. Install [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [poetry](https://python-poetry.org/docs/#installation)

2\. Clone the project and go to the corresponding directory: 

```bash
git clone https://github.com/Wander1ngW1nd/MoviesGRS_MFDP
cd MoviesGRS_MFDP
```

3\. (Optional) If your python version does not match the requirements specified in [pyproject.toml](pyproject.toml), [install one of the matching versions](https://realpython.com/installing-python)

4\. Create virtual environment and activate it

```bash
poetry shell
```

5\. Install dependencies
Though poetry provides its way for [instaling dependencies](https://python-poetry.org/docs/basic-usage/#installing-dependencies), now it is recommended to use pip installation from [requirements.txt](requirements.txt):

```bash
pip install -r requirements.txt
```

> This is motivated by the fact that *scikit-surprise-1.1.3* does not support PEP-517 installation, and poetry native installation would just fail. Due to the same reason, if there are any dependencies that need to be added, it is recommended to add them through poetry add, and then update [requirements.txt](requirements.txt):

```bash
poetry add <needed_dependency>
poetry export -f requirements.txt --output requirements.txt
```

### Pre-commit Hooks

This project uses pre-commit hooks for code quality checking. For this purpose [https://pre-commit.com](https://pre-commit.com/) framework is utilized.

Now the following linters are used for pre-commit hooks:

- [black](https://black.readthedocs.io/en/latest/)
- [isort](https://pycqa.github.io/isort/)
- [mypy](https://mypy.readthedocs.io/en/stable/)
- [pylint](https://pylint.readthedocs.io/en/latest/index.html)

Their specific configuration details can be found in [pyproject.toml](pyproject.toml).

To initialize pre-commit hooks, you need to execute the following command:

```bash
pre-commit install
```

To manually check the staged code base before committing you can run:

```bash
pre-commit run
```

If you want to check all files, not only those staged for commit, run:

```bash
pre-commit run --all-files
```

To skip some hooks while committing:

```bash
SKIP=black git commit -m "foo"
```