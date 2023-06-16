<!-- ---
title: MoviesGRS MFDP
emoji: 🏃
colorFrom: purple
colorTo: purple
sdk: streamlit
sdk_version: 1.23.0
app_file: src/app.py
pinned: false
--- -->

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