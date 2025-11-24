# Data Analysis Portfolio (Starter)

This is a minimal, open-source starter repository for showcasing data analysis projects with Streamlit.

## Features
- Project pages with embedded videos (links), datasets (.csv), notebook HTML previews, and simple dashboards.
- Upload datasets from the web UI.
- Easy to deploy to Streamlit Community Cloud.

## Structure
```
/app.py
/requirements.txt
/projects/<project_name>/
    dataset.csv
    notebook.html
    video.txt
/videos/
/notebooks/
```

## How to run locally
1. Create a Python environment (recommended)
2. `pip install -r requirements.txt`
3. `streamlit run app.py`

## Deploy to Streamlit Cloud
1. Push this repo to GitHub.
2. Go to https://share.streamlit.io and connect the repo.
3. Select `app.py` and deploy.

