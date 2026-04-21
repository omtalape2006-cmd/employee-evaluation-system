import sqlite3

conn = sqlite3.connect("hr_expert_system.db")
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

samples = [
    ('Amit Sharma', 95.0, 90.0, 5, 8, 5, 98.0, 92.0, 9, 10, 5, 6, 95.5),
    ('Rahul Verma', 40.0, 50.0, 2, 1, 2, 65.0, 45.0, 2, 4, 2, 2, 42.0),
    ('Sneha Patil', 75.0, 80.0, 4, 3, 4, 90.0, 78.0, 5, 8, 3, 4, 76.0)
]

cursor.executemany("""
INSERT INTO evaluations
(name, task_vol, quality, collab, learning, soft_skills,
attendance, kpi, leadership, deadlines, complexity, projects, final_score)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", samples)

conn.commit()
conn.close()

print("SQLite database created successfully.")