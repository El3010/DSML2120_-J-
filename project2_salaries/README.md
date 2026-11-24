# Data Science Salaries — Portfolio & Analytics App

A multipage Streamlit app that serves as my data visualization portfolio and a small analytics product.
It explores the **Data Science Job Salaries** dataset to see what is associated with higher pay in data
jobs (experience, company size, location, and remote work) through an EDA gallery and an interactive dashboard.

**Live app:** https://kuajywepecay9dgbnjd87d.streamlit.app/  <!-- TODO: paste your Streamlit Cloud URL -->

## Author
**Jose Lopez** — MSU Denver
- LinkedIn: https://www.linkedin.com/in/your-profile  <!-- TODO -->
- Email: emiliano3201@gmail.com  <!-- TODO -->

## App navigation
| Page | What it contains |
|---|---|
| 🏠 **Home** | Project overview, headline numbers, and links to each section |
| 📄 **Bio** | Professional summary, photo with alt-text, highlights, and my visualization philosophy |
| 📊 **EDA Gallery** | Four chart types (bar, histogram, box plot, heatmap), each with a guiding question, a "How to read this chart" guide, a source caption, and data-driven observations. All four charts are interactive (hover, zoom, plus dropdown/toggle/slider/checkbox controls). |
| 📈 **Dashboard** | Sidebar filters (year, experience, company size, remote work, salary range, U.S.-only toggle) that update 4 KPIs and 3 linked charts together, auto-generated insight bullets with limitations, a data-source badge, a "last refreshed" timestamp, and a filtered-CSV download |
| 🧭 **Future Work** | Five concrete next steps and a reflection on changes from my Lab 4.3 paper prototype |

## Dataset
- **Name:** Data Science Job Salaries
- **Source:** [Kaggle — Ruchi Bhatia](https://www.kaggle.com/datasets/ruchi798/data-science-job-salaries) (aggregated from the ai-jobs.net salary survey)
- **Records:** 607 rows × 11 columns (2020–2022); 565 after removing 42 duplicate rows
- **Key fields:** `work_year`, `experience_level`, `employment_type`, `job_title`, `salary_in_usd`, `employee_residence`, `remote_ratio`, `company_location`, `company_size`

**Preprocessing** (in `utils.py → load_data`, cached with `@st.cache_data`):
- Dropped the unnamed index column included in the CSV.
- Dropped exact duplicate rows and rows missing salary, experience level, or company size (no imputation).
- Mapped codes to readable, ordered labels (e.g., `EN/MI/SE/EX` → Entry/Mid/Senior/Executive; `remote_ratio` 0/50/100 → On-site/Hybrid/Fully remote; `S/M/L` → company size bands; ISO country codes → country names).
- Used `salary_in_usd` for all comparisons and added `salary_k` (thousands of USD) for compact axes.

### Ethics note
This dataset includes real people, so results must be interpreted carefully. Because the salaries are
self-reported to a public job-board survey (ai-jobs.net), they may include self-selection bias,
over-represent U.S. and English-speaking respondents, and contain only a few records for some roles and
countries, so they do not necessarily represent all data workers. The visualizations show patterns but
should not be used to make individual pay judgments or broad generalizations.

## Accessibility
- Color-blind-safe palettes: Okabe-Ito (categorical) and Cividis (heatmap); values are also shown as text so color is never the only cue.
- Descriptive chart titles, labeled axes with units (USD / thousands of USD), bar charts start at $0.
- Small groups are flagged with sample sizes (n) and an asterisk when n < 10.
- Profile image includes alt-text.

## Run locally
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
pip install -r requirements.txt
streamlit run app.py
```
Make sure `data/ds_salaries.csv` exists (download it from the Kaggle link above if needed).

## Requirements
See [`requirements.txt`](requirements.txt): streamlit, pandas, plotly, numpy (pinned versions).

## Project structure
```
streamlit_app/
├─ app.py                     # Router: defines sidebar navigation
├─ home.py                    # Home page
├─ utils.py                   # Cached data loading, labels, palette, shared layout helpers
├─ pages/
│  ├─ 1_📄_Bio.py
│  ├─ 2_📊_Charts_Gallery.py
│  ├─ 3_📈_Dashboard.py
│  └─ 4_🧭_Future_Work.py
├─ data/ds_salaries.csv
├─ assets/profile.png
├─ .streamlit/config.toml     # Theme (high-contrast, brand color)
├─ requirements.txt
└─ README.md
```

## Screenshots
<!-- TODO: add 1–3 screenshots, e.g. assets/screenshot_dashboard.png -->
![Dashboard page with filters, KPIs, and linked charts](assets/screenshot_dashboard.png)

## AI assistance acknowledgment
I used Claude to help scaffold the app's code structure and draft documentation. I reviewed, edited, and tested all content.
