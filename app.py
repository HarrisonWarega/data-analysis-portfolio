import streamlit as st
import pandas as pd
from pathlib import Path
import altair as alt

# Page config
st.set_page_config(
    page_title="Data Analysis Portfolio",
    layout="wide",
)

BASE = Path(__file__).parent
PROJECTS_DIR = BASE / "projects"

# Utility functions
def list_projects():
    if not PROJECTS_DIR.exists():
        return []
    return sorted([d for d in PROJECTS_DIR.iterdir() if d.is_dir()], key=lambda p: p.name.lower())

def project_preview_info(proj_path):
    preview = proj_path / "preview.png"
    description = "A short description of this project. Replace with your own."
    return {
        "name": proj_path.name,
        "preview": str(preview) if preview.exists() else None,
        "description": description,
        "path": proj_path
    }

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Projects", "Upload Dataset", "About"])

# -------------------------
# Home (grid of cards)
# -------------------------
if page == "Home":
    st.title("📊 Data Analysis Portfolio")
    st.write("Welcome! Explore my datasets, notebooks, analyses, and dashboards.")
    st.write("")

    projects = list_projects()
    if not projects:
        st.info("No projects found. Add folders under `/projects/` with a dataset and notebook.")
    else:
        cards_per_row = 3
        rows = (len(projects) + cards_per_row - 1) // cards_per_row
        proj_infos = [project_preview_info(p) for p in projects]

        # Display grid
        idx = 0
        for r in range(rows):
            cols = st.columns(cards_per_row, gap="large")
            for c in range(cards_per_row):
                if idx >= len(proj_infos):
                    cols[c].empty()
                    idx += 1
                    continue

                info = proj_infos[idx]
                with cols[c]:
                    # Card container
                    with st.container():
                        # thumbnail or placeholder
                        if info["preview"]:
                            st.image(info["preview"], use_column_width=True)
                        else:
                            st.markdown("🗂️", unsafe_allow_html=True)

                        st.subheader(info["name"].replace("_", " ").title())
                        st.write(info["description"])

                        # small meta row
                        st.write("")
                        open_key = f"open_{info['name']}"
                        if st.button("📂 Open Project", key=open_key):
                            st.session_state["selected_project"] = info["name"]
                            st.experimental_rerun()
                idx += 1

    st.markdown("---")
    st.markdown("Tip: Add `dataset.csv`, `notebook.html` and `video.txt` to `/projects/<project_name>/` to populate each project page.")

# -------------------------
# Projects page (select + tabs)
# -------------------------
elif page == "Projects":
    st.title("📁 Projects")
    projects = [d.name for d in list_projects()]
    if not projects:
        st.info("No projects found.")
    else:
        # If a project was opened from Home, pre-select it
        preselect = st.session_state.get("selected_project", None)
        project = st.selectbox("Choose a project", projects, index=(projects.index(preselect) if preselect in projects else 0))
        proj_path = PROJECTS_DIR / project

        st.header(project.replace("_", " ").title())
        st.write("Manage and view resources for this project below.")
        st.write("")

        tabs = st.tabs(["🎥 Video", "📁 Dataset", "📓 Notebook", "📊 Dashboard", "🔧 Files"])
        # -------- Video Tab --------
        with tabs[0]:
            st.subheader("Video Presentation")
            video_file = proj_path / "video.txt"
            if video_file.exists():
                link = video_file.read_text().strip()
                # If it's local filename within project, play it
                local_mp4 = proj_path / link
                if link.endswith(".mp4") and local_mp4.exists():
                    st.video(str(local_mp4))
                else:
                    st.markdown(f"[▶️ Watch video]({link})")
            else:
                st.info("No video configured. Create `video.txt` in the project folder with a YouTube/Loom link or local mp4 filename.")

        # -------- Dataset Tab --------
        with tabs[1]:
            st.subheader("Datasets")
            datasets = sorted(proj_path.glob("*.csv"))
            if datasets:
                for ds in datasets:
                    st.write(f"**{ds.name}**")
                    df = pd.read_csv(ds)
                    st.dataframe(df.head(200), use_container_width=True)
                    st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), file_name=ds.name)
                    st.markdown("---")
            else:
                st.info("No CSV datasets found in project folder.")

        # -------- Notebook Tab --------
        with tabs[2]:
            st.subheader("Jupyter Notebook (HTML)")
            notebooks = sorted(proj_path.glob("*.html"))
            if notebooks:
                for nb in notebooks:
                    st.write(f"**{nb.name}**")
                    html = nb.read_text(encoding="utf-8")
                    st.components.v1.html(html, height=700)
                    st.markdown("---")
            else:
                st.info("No exported notebook HTML files found. Use `jupyter nbconvert <notebook>.ipynb --to html --no-input`")

        # -------- Dashboard Tab --------
        with tabs[3]:
            st.subheader("Quick Dashboard")
            datasets = sorted(proj_path.glob("*.csv"))
            if datasets:
                df = pd.read_csv(datasets[0])
                # Show a small summary and 1 example chart if numeric columns exist
                st.write("**Summary:**")
                st.write(df.describe())

                numeric_cols = df.select_dtypes(include="number").columns.tolist()
                if numeric_cols:
                    # Simple example chart: distribution of first numeric column
                    col = numeric_cols[0]
                    st.write(f"**Example chart — distribution of `{col}`**")
                    chart = alt.Chart(df).mark_bar().encode(
                        alt.X(f"{col}:Q", bin=alt.Bin(maxbins=30)),
                        y='count()'
                    ).properties(height=300)
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("No numeric columns available for charts in the first dataset.")
            else:
                st.info("No CSV found to build dashboard.")

        # -------- Files Tab (raw listing) --------
        with tabs[4]:
            st.subheader("Project Folder Files")
            files = sorted(list(proj_path.iterdir()))
            for f in files:
                st.write(f"- {f.name}")

# -------------------------
# Upload Dataset page
# -------------------------
elif page == "Upload Dataset":
    st.title("Upload a Dataset")
    st.write("Upload a CSV directly into a project folder so it appears on the Projects page.")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        target = st.text_input("Save as (relative path), e.g., projects/new_project/data.csv")
        if st.button("Save file"):
            if not target:
                st.error("Enter a valid relative path.")
            else:
                save_path = BASE / target
                save_path.parent.mkdir(parents=True, exist_ok=True)
                with open(save_path, "wb") as f:
                    f.write(uploaded.getbuffer())
                st.success(f"Saved to {save_path}")
                st.experimental_rerun()

# -------------------------
# About
# -------------------------
elif page == "About":
    st.title("About This Portfolio")
    st.write(
"""
I am passionate about Data Science, Machine Learning, and Artificial Intelligence —
building analyses, models, and insights that help uncover patterns, solve problems,
and drive meaningful decisions. This portfolio represents my ongoing journey in
understanding data deeply and communicating it clearly.

**Portfolio Structure (How to Explore This Site):**

- Each project lives under `/projects/<project_name>/`
- Inside each project folder you’ll find:
  - `dataset.csv` — the dataset used in the analysis  
  - `notebook.html` — an exported Jupyter Notebook showing the work  
  - `video.txt` — a link or local filename for the presentation video  
- The site automatically reads and displays these resources in an organized layout.
"""
    )
