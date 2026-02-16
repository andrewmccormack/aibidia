# Aibidia - Data Engineering Exercise

## Quick Start

The project is containerised and can be run using docker compose:

```aiignore
docker compose up  --build
```

Note: The containerised version of the app isn't working yet, because of an issue with CSRF token generation.

## Local Development

The project is built using python 3.14 and [uv](https://docs.astral.sh/uv/). 

If you're using a Mac then you can install uv using homebrew:

```aiignore
brew install uv
```

To run the project simply run:

```aiignore```
uv run main.py
```aiignore```

You should be able to access the app at http://127.0.0.1:5000/

To run the tests:

```aiignore
uv run pytest
```

## Data Sources Used

I have been using the following data sources to test the app:

* [Chocolate Sales](https://www.kaggle.com/datasets/saidaminsaidaxmadov/chocolate-sales)
* [Best Selling Books (2023-2025)](https://www.kaggle.com/datasets/malaklahyani/best-selling-books-20232025)
* [Top Spotify Podcaset Episodes](https://www.kaggle.com/datasets/daniilmiheev/top-spotify-podcasts-daily-updated)