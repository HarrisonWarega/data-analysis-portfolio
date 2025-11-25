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

# Map of visible industry names to folder names (subfolders under /projects)
INDUSTRY_DIRS = {
    "Business / Sales": "business_sales",
    "Health": "health",
    "Climate": "climate",
    "Transportation": "transportation",
    "Finance & Macro": "finance_macro",
    "Other": "other"
}

# ---------- Utilities ----------
def list_category_folders():
    """Return available categories that exist on disk (display_name, folder_name)."""
    available = []
    for label, folder in INDUSTRY_DIRS.items():
        if (PROJECTS_DIR / folder).exists():
            available.append((label, folder))
    return available

def list_projects_in_folder(folder_name):
    cat_path = PROJECTS_DIR / folder_name
    if not cat_path.exists():
        return []
    return sorted([d for d in cat_path.iterdir() if d.is_dir()])

def gather_all_projects():
    items = []
    for label, folder in list_category_folders():
        projects = list_projects_in_folder(folder)
        for p in projects:
            preview = p / "preview.png"
            items.append({
                "category_label": label,
                "category_folder": folder,
                "path": p,
                "name": p.name,
                "preview": str(preview) if preview.exists() else None,
                "description": "A short description of this project. Replace with your own."
            })
    return items

def read_file_text(path: Path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""

# Read owner-controlled highlights list (one folder name per line, e.g. business_sales)
def read_home_highlights():
    path = BASE / "home_highlights.txt"
    if not path.exists():
        return []
    lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()]
    # Remove empty lines and comments
    lines = [ln for ln in lines if ln and not ln.startswith("#")]
    # Limit to 3 entries
    return lines[:3]

# Ensure session keys
if "selected_project" not in st.session_state:
    st.session_state["selected_project"] = None
if "selected_category" not in st.session_state:
    st.session_state["selected_category"] = None
if "navigate_to" not in st.session_state:
    st.session_state["navigate_to"] = None

# Sidebar navigation
sidebar_choice = st.sidebar.radio("Go to", ["Home", "Projects", "Upload Dataset"])
if st.session_state.get("navigate_to"):
    page = st.session_state.pop("navigate_to")
else:
    page = sidebar_choice

# -------------------------
# HOME (landing page)
# -------------------------
if page == "Home":
    st.title("📊 Data Analysis Portfolio")

    st.markdown("""
Welcome! I am passionate about Data Science, Machine Learning, and Artificial Intelligence — 
building analyses, models, and insights that help uncover patterns, solve problems, 
and drive meaningful decisions.
""")

    st.markdown("### Explore my datasets, notebooks, analyses, and dashboards.")

    st.write("")
    st.markdown("**Portfolio Structure (How to Explore This Site):**")
    st.markdown("""
- Each project lives under `/projects/<category_folder>/<project_name>/`  
- Inside each project folder you’ll find:
  - `dataset.csv` — the dataset used in the analysis  
  - `notebook.html` — an exported Jupyter Notebook showing the work  
  - `video.txt` — a link or local filename for the presentation video  
- The Projects view groups projects by industry/category.
""")

    if st.button("📁 See my projects"):
        st.session_state["navigate_to"] = "Projects"
        st.rerun()

    st.write("---")
    st.write("Below are quick highlights of the projects currently in the repository:")

    # Owner-controlled highlights (folder names, e.g., business_sales)
    highlight_folders = read_home_highlights()
    highlights = []
    for folder in highlight_folders:
        projects = list_projects_in_folder(folder)
        if projects:
            p = projects[0]  # representative project (first one)
            preview = p / "preview.png"
            highlights.append({
                "folder": folder,
                "path": p,
                "name": p.name,
                "preview": str(preview) if preview.exists() else None,
                "label": next((lbl for lbl, f in list_category_folders() if f == folder), folder)
            })

    if not highlights:
        st.info("No highlights configured. Create `home_highlights.txt` in the repo root with category folder names (one per line).")
    else:
        # Render highlights in up to 3 columns (small cards)
        cols = st.columns(len(highlights), gap="large")
        for i, info in enumerate(highlights):
            with cols[i]:
                with st.container(border=True):
                    # smaller preview: set width param
                    if info["preview"]:
                        try:
                            st.image(info["preview"], width=340)
                        except Exception:
                            st.markdown("🗂️")
                    else:
                        st.markdown("🗂️")
                    # smaller title style
                    st.markdown(f"### {info['name'].replace('_',' ').title()}")
                    st.caption(f"{info['label']} — {info['name']}")
                    st.write("A short description of this project. Replace with your own.")
                    if st.button(f"📂 Open {info['name']}", key=f"highlight_open_{info['folder']}_{info['name']}"):
                        st.session_state["selected_category"] = info["folder"]
                        st.session_state["selected_project"] = info["name"]
                        st.session_state["navigate_to"] = "Projects"
                        st.rerun()

# -------------------------
# Projects page (category -> project -> tabs)
# -------------------------
elif page == "Projects":
    st.title("📁 Projects")

    categories = list_category_folders()
    if not categories:
        st.info("No categories found under /projects/. Create category subfolders (e.g., business_sales, health).")
    else:
        labels = [label for (label, folder) in categories]
        folders = {label: folder for (label, folder) in categories}

        pre_cat_folder = st.session_state.get("selected_category", None)
        pre_cat_label = None
        if pre_cat_folder:
            for label, folder in categories:
                if folder == pre_cat_folder:
                    pre_cat_label = label
                    break

        selected_label = st.selectbox("Choose a Category", labels, index=(labels.index(pre_cat_label) if pre_cat_label in labels else 0))
        selected_folder = folders[selected_label]
        st.write("")
        st.info(f"Projects in **{selected_label}**. Each project folder contains dataset(s), exported notebook(s), and a demo video. Click a project to view its files and dashboard.")

        proj_list = list_projects_in_folder(selected_folder)
        if not proj_list:
            st.warning(f"No projects in {selected_folder} yet.")
        else:
            # Two-column listing, but with reduced image width to shrink cards
            cols = st.columns(2, gap="large")
            for i, p in enumerate(proj_list):
                c = cols[i % 2]
                with c:
                    preview = p / "preview.png"
                    with st.container(border=True):
                        if preview.exists():
                            try:
                                st.image(str(preview), width=320)
                            except Exception:
                                st.markdown("🗂️")
                        else:
                            st.markdown("🗂️")
                        st.markdown(f"### {p.name.replace('_',' ').title()}")
                        st.write("A short description of this project. Replace with your own.")
                        if st.button(f"Open {p.name}", key=f"proj_{selected_folder}_{p.name}"):
                            st.session_state["selected_project"] = p.name
                            st.session_state["selected_category"] = selected_folder
                            st.rerun()

            st.write("---")
            chosen = st.session_state.get("selected_project", None)
            if chosen:
                proj_path = PROJECTS_DIR / selected_folder / chosen
                if proj_path.exists():
                    st.header(f"{chosen.replace('_',' ').title()}")
                    tabs = st.tabs(["🎥 Video", "📁 Dataset", "📓 Notebook", "📊 Dashboard", "🔧 Files"])

                    # Video tab
                    with tabs[0]:
                        st.subheader("Video Presentation")
                        video_file = proj_path / "video.txt"
                        if video_file.exists():
                            link = read_file_text(video_file).strip()
                            local_mp4 = proj_path / link
                            if link.endswith(".mp4") and local_mp4.exists():
                                st.video(str(local_mp4))
                            else:
                                st.markdown(f"[▶️ Watch video]({link})")
                        else:
                            st.info("No video configured (create video.txt with a URL or filename).")

                    # Dataset tab
                    with tabs[1]:
                        st.subheader("Datasets")
                        datasets = sorted(proj_path.glob("*.csv"))
                        if datasets:
                            for ds in datasets:
                                st.write(f"**{ds.name}**")
                                try:
                                    df = pd.read_csv(ds)
                                    st.dataframe(df.head(200), use_container_width=True)
                                    st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), file_name=ds.name)
                                except Exception as e:
                                    st.error(f"Could not read {ds.name}: {e}")
                                st.markdown("---")
                        else:
                            st.info("No CSV datasets found in project folder.")

                    # Notebook tab
                    with tabs[2]:
                        st.subheader("Jupyter Notebook (HTML)")
                        notebooks = sorted(proj_path.glob("*.html"))
                        if notebooks:
                            for nb in notebooks:
                                st.write(f"**{nb.name}**")
                                html = read_file_text(nb)
                                if html:
                                    st.components.v1.html(html, height=600)
                                else:
                                    st.warning(f"Could not read {nb.name}")
                                st.markdown("---")
                        else:
                            st.info("No exported notebook HTML files found. Use `jupyter nbconvert <notebook>.ipynb --to html --no-input`")

                    # Dashboard tab
                    with tabs[3]:
                        st.subheader("Quick Dashboard")
                        datasets = sorted(proj_path.glob("*.csv"))
                        if datasets:
                            df = pd.read_csv(datasets[0])
                            st.write("**Summary:**")
                            st.write(df.describe())
                            numeric_cols = df.select_dtypes(include="number").columns.tolist()
                            if numeric_cols:
                                col = numeric_cols[0]
                                chart = alt.Chart(df).mark_bar().encode(
                                    alt.X(f"{col}:Q", bin=alt.Bin(maxbins=30)),
                                    y='count()'
                                ).properties(height=260)
                                st.altair_chart(chart, use_container_width=True)
                            else:
                                st.info("No numeric columns available for charts in the first dataset.")
                        else:
                            st.info("No CSV found to build dashboard.")

                    # Files tab
                    with tabs[4]:
                        st.subheader("Project Folder Files")
                        files = sorted(list(proj_path.iterdir()))
                        for f in files:
                            st.write(f"- {f.name}")
                else:
                    st.error("Selected project folder not found. It may have been moved or removed.")

# -------------------------
# Upload Dataset page
# -------------------------
elif page == "Upload Dataset":
    st.title("Upload a Dataset")
    st.write("Upload a CSV directly into a project folder so it appears on the Projects page.")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        target = st.text_input("Save as (relative path), e.g., projects/business_sales/new_project/data.csv")
        if st.button("Save file"):
            if not target:
                st.error("Enter a valid relative path.")
            else:
                save_path = BASE / target
                save_path.parent.mkdir(parents=True, exist_ok=True)
                with open(save_path, "wb") as f:
                    f.write(uploaded.getbuffer())
                st.success(f"Saved to {save_path}")
                st.rerun()
