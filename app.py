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

# --- Utilities --------------------------------------------------------------
def list_category_folders():
    """Return available categories that exist on disk (display_name, folder_name)."""
    available = []
    for label, folder in INDUSTRY_DIRS.items():
        if (PROJECTS_DIR / folder).exists():
            available.append((label, folder))
    return available

def list_projects_in_folder(folder_name):
    """Return sorted list of project folder Path objects inside the given category folder."""
    cat_path = PROJECTS_DIR / folder_name
    if not cat_path.exists():
        return []
    return sorted([d for d in cat_path.iterdir() if d.is_dir()])

def gather_all_projects():
    """Collect all projects across categories. Returns list of dicts with category info."""
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

# Ensure session keys exist
if "selected_project" not in st.session_state:
    st.session_state["selected_project"] = None
if "selected_category" not in st.session_state:
    st.session_state["selected_category"] = None
if "navigate_to" not in st.session_state:
    st.session_state["navigate_to"] = None

# Sidebar navigation (the radio is the primary control, but we also allow programmatic navigation)
sidebar_choice = st.sidebar.radio("Go to", ["Home", "Projects", "Upload Dataset"])
# Programmatic navigation override
if st.session_state.get("navigate_to"):
    page = st.session_state.pop("navigate_to")
else:
    page = sidebar_choice

# -------------------------
# HOME (landing page: introduces you + CTA to projects)
# -------------------------
if page == "Home":
    st.title("📊 Data Analysis Portfolio")
    st.markdown(
        "Welcome! Explore my datasets, notebooks, analyses, and dashboards. "
        "I am passionate about Data Science, Machine Learning, and Artificial Intelligence — "
        "building analyses, models, and insights that help uncover patterns, solve problems, "
        "and drive meaningful decisions."
    )
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

    st.write("")
    # CTA to Projects
    if st.button("📁 See my projects"):
        st.session_state["navigate_to"] = "Projects"
        st.rerun()

    st.write("---")
    st.write("Below are quick highlights of the projects currently in the repository:")

    all_projects = gather_all_projects()
    if not all_projects:
        st.info("No projects found. Add category subfolders and project folders under `/projects/`.")
    else:
        # Render a simple 3-column flowing grid that fills left-to-right then next row.
        # This approach avoids creating large empty rows because we always produce 3 columns
        # and fill them in sequence (no row-height stretching).
        cols = st.columns(3, gap="large")
        col_index = 0
        for info in all_projects:
            with cols[col_index]:
                with st.container(border=True):
                    if info["preview"]:
                        st.image(info["preview"], use_container_width=True)
                    else:
                        st.markdown("🗂️")
                    st.subheader(info["name"].replace("_", " ").title())
                    st.caption(f"{info['category_label']} — {info['path'].name}")
                    st.write(info["description"])
                    # The Open button now navigates to Projects and pre-selects the category + project
                    if st.button(f"📂 Open {info['name']}", key=f"open_{info['category_folder']}_{info['name']}"):
                        st.session_state["selected_category"] = info["category_folder"]
                        st.session_state["selected_project"] = info["name"]
                        st.session_state["navigate_to"] = "Projects"
                        st.rerun()
            col_index = (col_index + 1) % 3

# -------------------------
# Projects page (category -> project -> tabs)
# -------------------------
elif page == "Projects":
    st.title("📁 Projects")

    # categories to display (label -> folder)
    categories = list_category_folders()
    if not categories:
        st.info("No categories found under `/projects/`. Create category subfolders (e.g., business_sales, health).")
    else:
        labels = [label for (label, folder) in categories]
        folders = {label: folder for (label, folder) in categories}

        # Preselect category if navigated from home
        pre_cat_folder = st.session_state.get("selected_category", None)
        pre_cat_label = None
        if pre_cat_folder:
            # find matching label
            for label, folder in categories:
                if folder == pre_cat_folder:
                    pre_cat_label = label
                    break

        selected_label = st.selectbox("Choose a Category", labels, index=(labels.index(pre_cat_label) if pre_cat_label in labels else 0))
        selected_folder = folders[selected_label]
        st.write("")
        # description of what to expect in this category (basic generic message)
        st.info(f"Projects in **{selected_label}**. Each project folder contains dataset(s), exported notebook(s), and a demo video. Click a project to view its files and dashboard.")

        # list projects in this category
        proj_list = list_projects_in_folder(selected_folder)
        if not proj_list:
            st.warning("No projects in this category yet. Create a folder under `/projects/{selected_folder}/` and add your files.")
        else:
            # Show projects as cards in two columns (more space for details)
            cols = st.columns(2, gap="large")
            for i, p in enumerate(proj_list):
                c = cols[i % 2]
                with c:
                    preview = p / "preview.png"
                    with st.container(border=True):
                        if preview.exists():
                            st.image(str(preview), use_container_width=True)
                        else:
                            st.markdown("🗂️")
                        st.subheader(p.name.replace("_", " ").title())
                        st.write("A short description of this project. Replace with your own.")
                        if st.button(f"Open {p.name}", key=f"proj_{selected_folder}_{p.name}"):
                            st.session_state["selected_project"] = p.name
                            st.session_state["selected_category"] = selected_folder
                            # jump to the project details area below (we re-render same page)
                            st.rerun()

            st.write("---")
            # If a project has been selected, show its tabs
            chosen = st.session_state.get("selected_project", None)
            if chosen:
                proj_path = PROJECTS_DIR / selected_folder / chosen
                if proj_path.exists():
                    st.header(f"{chosen.replace('_', ' ').title()}")
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
                                    st.components.v1.html(html, height=700)
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
