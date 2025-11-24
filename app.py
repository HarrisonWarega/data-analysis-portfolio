import streamlit as st
import pandas as pd
import os
from pathlib import Path

st.set_page_config(page_title="Data Analysis Portfolio", layout="wide")

BASE = Path(__file__).parent
PROJECTS_DIR = BASE / "projects"
NOTEBOOKS_DIR = BASE / "notebooks"
VIDEOS_DIR = BASE / "videos"

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Projects", "Upload Dataset", "About"])

if page == "Home":
    st.title("Data Analysis Portfolio")
    st.write("Welcome! Explore my datasets, notebooks, analyses, and dashboards.")
    if (PROJECTS_DIR.exists()):
        cols = st.columns(3)
        for i, p in enumerate(sorted([d.name for d in PROJECTS_DIR.iterdir() if d.is_dir()])):
            with cols[i % 3]:
                st.header(p.replace('_', ' ').title())
                st.write("A brief description of the project.")
                if (PROJECTS_DIR / p / "preview.png").exists():
                    st.image(str(PROJECTS_DIR / p / "preview.png"))
                if st.button(f"Open {p}", key=f"open_{p}"):
                    st.session_state['selected_project'] = p
                    st.experimental_rerun()

elif page == "Projects":
    st.title("Projects")
    projects = [d.name for d in PROJECTS_DIR.iterdir() if d.is_dir()]
    if not projects:
        st.info("No projects found. Drop a project folder into /projects.")
    project = st.selectbox("Choose a project", projects)
    if project:
        proj_path = PROJECTS_DIR / project
        st.header(project.replace('_', ' ').title())

        # Video
        video_file = proj_path / "video.txt"
        st.subheader("🎥 Video Presentation")
        if video_file.exists():
            video_link = video_file.read_text().strip()
            if video_link.endswith(".mp4") and (proj_path / video_link).exists():
                st.video(str(proj_path / video_link))
            else:
                # assume it's an embed link (YouTube/Loom)
                st.markdown(f"[Watch video]({video_link})")
        else:
            st.info("No video configured. Add a file named 'video.txt' with a link or filename.")

        # Dataset
        st.subheader("📁 Dataset")
        datasets = list(proj_path.glob("*.csv"))
        if datasets:
            for ds in datasets:
                st.write(f"**{ds.name}**")
                df = pd.read_csv(ds)
                st.dataframe(df.head(100))
                st.download_button("Download "+ds.name, df.to_csv(index=False).encode('utf-8'), ds.name)
        else:
            st.info("No CSV datasets found in project folder.")

        # Notebooks (rendered HTML)
        st.subheader("📓 Jupyter Notebook (HTML preview)")
        notebooks = list(proj_path.glob("*.html"))
        if notebooks:
            for nb in notebooks:
                st.write(f"**{nb.name}**")
                with open(nb, "r", encoding="utf-8") as f:
                    html = f.read()
                st.components.v1.html(html, height=600)
        else:
            st.info("No exported notebook HTML files found. Convert .ipynb -> .html with nbconvert.")

        # Dashboard (a simple sample)
        st.subheader("📊 Dashboard (sample)")
        # Try to show a basic table/chart if dataset exists
        if datasets:
            df = pd.read_csv(datasets[0])
            st.write("A simple aggregated view:")
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            if numeric_cols:
                st.write(df[numeric_cols].describe())
            else:
                st.write("No numeric columns to summarize.")
        else:
            st.info("Add a CSV to see dashboard widgets here.")

elif page == "Upload Dataset":
    st.title("Upload a Dataset")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        target = st.text_input("Save as (relative filename, e.g., projects/newproj/mydata.csv)")
        if st.button("Save file"):
            if not target:
                st.error("Provide a relative path to save the file.")
            else:
                save_path = BASE / target
                save_path.parent.mkdir(parents=True, exist_ok=True)
                with open(save_path, "wb") as f:
                    f.write(uploaded.getbuffer())
                st.success(f"Saved to {save_path}")
                st.experimental_rerun()
    st.write("Tip: upload into a project folder like `projects/your_project/` so it appears in Projects.")

elif page == "About":
    st.title("About")
    st.write("A simple portfolio to showcase analysis, notebooks, datasets and dashboards.")
    st.write("Generated starter project structure. Edit files and deploy to Streamlit Cloud.")
