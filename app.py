import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Data Analysis Portfolio",
    layout="wide",
)

BASE = Path(__file__).parent
PROJECTS_DIR = BASE / "projects"

# SIDEBAR
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Projects", "Upload Dataset", "About"])

# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------
if page == "Home":
    st.title("📊 Data Analysis Portfolio")
    st.write("Welcome! Explore my datasets, notebooks, analyses, and dashboards.")
    st.divider()

    if PROJECTS_DIR.exists():
        for proj_folder in sorted([d for d in PROJECTS_DIR.iterdir() if d.is_dir()]):

            with st.container(border=True):
                col1, col2 = st.columns([1, 4])

                # Preview image if exists
                preview_path = proj_folder / "preview.png"
                if preview_path.exists():
                    col1.image(str(preview_path), use_column_width=True)
                else:
                    col1.write("🗂️")

                with col2:
                    st.subheader(proj_folder.name.replace("_", " ").title())
                    st.write("A brief description of the project.")

                    if st.button(f"Open {proj_folder.name}", key=f"open_{proj_folder}"):
                        st.session_state["selected_project"] = proj_folder.name
                        st.experimental_rerun()

            st.divider()

# ---------------------------------------------------------
# PROJECTS PAGE
# ---------------------------------------------------------
elif page == "Projects":
    st.title("📁 Projects")

    projects = [d.name for d in PROJECTS_DIR.iterdir() if d.is_dir()]

    if not projects:
        st.info("No projects found.")
    else:
        project = st.selectbox("Choose a project", projects)

        if project:
            proj_path = PROJECTS_DIR / project
            st.header(project.replace("_", " ").title())
            st.write("---")

            # Tabs
            tabs = st.tabs(["🎥 Video", "📁 Dataset", "📓 Notebook", "📊 Dashboard"])

            # ---------------- VIDEO TAB ----------------
            with tabs[0]:
                video_file = proj_path / "video.txt"
                if video_file.exists():
                    link = video_file.read_text().strip()
                    if link.endswith(".mp4") and (proj_path / link).exists():
                        st.video(str(proj_path / link))
                    else:
                        st.markdown(f"[▶️ Watch video]({link})")
                else:
                    st.info("No video configured.")

            # ---------------- DATASET TAB ----------------
            with tabs[1]:
                datasets = list(proj_path.glob("*.csv"))
                if datasets:
                    for ds in datasets:
                        st.write(f"### {ds.name}")
                        df = pd.read_csv(ds)
                        st.dataframe(df.head())
                        st.download_button("Download CSV", df.to_csv().encode(), ds.name)
                else:
                    st.info("No datasets found.")

            # ---------------- NOTEBOOK TAB ----------------
            with tabs[2]:
                notebooks = list(proj_path.glob("*.html"))
                if notebooks:
                    for nb in notebooks:
                        html = nb.read_text()
                        st.components.v1.html(html, height=800)
                else:
                    st.info("No notebook HTML files found.")

            # ---------------- DASHBOARD TAB ----------------
            with tabs[3]:
                datasets = list(proj_path.glob("*.csv"))
                if datasets:
                    df = pd.read_csv(datasets[0])
                    st.write("### Quick Summary")
                    st.write(df.describe())
                else:
                    st.info("No CSV found to build dashboard.")

# ---------------------------------------------------------
# UPLOAD PAGE
# ---------------------------------------------------------
elif page == "Upload Dataset":
    st.title("Upload a Dataset")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded:
        target = st.text_input("Save as: (e.g., projects/telecom_analysis/new.csv)")
        if st.button("Save file"):
            if not target:
                st.error("Enter a valid path.")
            else:
                save_path = BASE / target
                save_path.parent.mkdir(parents=True, exist_ok=True)
                with open(save_path, "wb") as f:
                    f.write(uploaded.getbuffer())
                st.success(f"Saved to {save_path}")
                st.experimental_rerun()

# ---------------------------------------------------------
# ABOUT
# ---------------------------------------------------------
elif page == "About":
    st.title("About This Portfolio")
    st.write("A clean, simple Streamlit portfolio for showcasing data analysis projects.")
