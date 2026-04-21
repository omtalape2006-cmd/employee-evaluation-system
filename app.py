import streamlit as st
import sqlite3
import pandas as pd
import random
from difflib import get_close_matches

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_db_connection():
    return sqlite3.connect("hr_expert_system.db", check_same_thread=False)

# -----------------------------
# CREATE TABLE IF NOT EXISTS
# -----------------------------
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        task_vol REAL,
        quality REAL,
        collab REAL,
        learning INTEGER,
        soft_skills REAL,
        attendance REAL,
        kpi REAL,
        leadership INTEGER,
        deadlines REAL,
        complexity REAL,
        projects INTEGER,
        final_score REAL
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="AI HR Expert System", layout="wide")
st.title("🤖 Advanced AI HR Expert System")
st.markdown("---")

# -----------------------------
# SIDEBAR INPUT FORM
# -----------------------------
st.sidebar.header("📝 New Evaluation")

with st.sidebar.form("input_form"):
    name = st.text_input("Employee Name")
    kpi = st.slider("KPI Score", 0, 100, 75)
    quality = st.slider("Quality Score", 0, 100, 75)
    task_vol = st.slider("Task Volume", 0, 100, 75)
    attendance = st.slider("Attendance %", 0, 100, 90)
    deadlines = st.slider("Deadline Adherence", 0, 10, 8)
    soft_skills = st.select_slider("Soft Skills/Peer Rating", options=[1,2,3,4,5], value=3)
    collab = st.select_slider("Collaboration", options=[1,2,3,4,5], value=3)
    learning = st.slider("New Skills (0-10)", 0, 10, 2)
    leadership = st.slider("Leadership (0-10)", 0, 10, 2)
    complexity = st.slider("Complexity (1-5)", 1, 5, 3)
    projects = st.number_input("No. of Projects", min_value=0, value=3)

    submitted = st.form_submit_button("Analyze & Save")

    if submitted:

        performance = (kpi * 0.4) + (quality * 0.3) + (task_vol * 0.3)
        reliability = (attendance * 0.6) + (deadlines * 4)
        behavior = (soft_skills * 10) + (collab * 10)
        growth = (learning * 10) + (leadership * 5)

        complexity_bonus = (complexity - 3) * 5
        capacity_bonus = 5 if projects > 5 else 0

        final_score = (
            (performance + complexity_bonus) * 0.4
            + reliability * 0.2
            + behavior * 0.2
            + growth * 0.2
            + capacity_bonus
        )

        final_score = max(0, min(100, final_score))

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO evaluations (
            name, task_vol, quality, collab, learning, soft_skills,
            attendance, kpi, leadership, deadlines, complexity,
            projects, final_score
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, task_vol, quality, collab, learning, soft_skills,
            attendance, kpi, leadership, deadlines,
            complexity, projects, final_score
        ))

        conn.commit()
        conn.close()

        st.sidebar.success(f"{name} saved successfully!")

# -----------------------------
# MAIN TABLE
# -----------------------------
st.subheader("📊 Employee Knowledge Base")

conn = get_db_connection()
df = pd.read_sql_query("SELECT * FROM evaluations", conn)
conn.close()

if not df.empty:

    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("🔍 AI Diagnosis")

    selected_emp = st.selectbox(
        "Select Employee:",
        df["name"]
    )

    emp = df[df["name"] == selected_emp].iloc[0]

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Final Score", round(emp["final_score"], 2))

    with col2:
        st.write("### Findings")

        if emp["final_score"] > 90:
            st.success("⭐ Top Performer")

        if emp["attendance"] < 70:
            st.warning("⚠️ Attendance Risk")

        if emp["learning"] > 7:
            st.info("📚 Fast Learner")

        if emp["projects"] > 6:
            st.info("📁 Handles High Workload")

        if emp["quality"] < 60:
            st.error("❌ Quality Needs Improvement")

    # DELETE BUTTON
    st.markdown("---")

    if st.button(f"Delete {selected_emp}"):

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM evaluations WHERE id = ?",
            (int(emp["id"]),)
        )

        conn.commit()
        conn.close()

        st.success("Deleted Successfully")
        st.rerun()

else:
    st.info("No records found. Add new employee from sidebar.")

# -----------------------------
# CHATBOT SECTION
# -----------------------------
st.markdown("---")
st.subheader("💬 HR Chatbot")

intents = {
    "hello": [
        "Hello 👋",
        "Hi there!",
        "Hey!"
    ],
    "score": [
        "Final score is based on KPI, Quality, Behavior, Growth & Reliability."
    ],
    "promotion": [
        "Employees above 90 score are ideal for promotion."
    ],
    "thanks": [
        "You're welcome 😊"
    ]
}

def get_response(msg):
    msg = msg.lower()

    for key in intents:
        if key in msg:
            return random.choice(intents[key])

    return "Please ask about score, promotion or hello."

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Ask HR Bot...")

if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    response = get_response(prompt)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    with st.chat_message("assistant"):
        st.markdown(response)