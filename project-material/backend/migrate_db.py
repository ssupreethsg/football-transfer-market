import sqlite3

def migrate():
    conn = sqlite3.connect('sql_app.db')
    c = conn.cursor()
    c.execute('PRAGMA table_info(players)')
    existing = [r[1] for r in c.fetchall()]
    new_cols = [
        ('position', 'VARCHAR DEFAULT "MID"'),
        ('appearances', 'INTEGER DEFAULT 0'),
        ('clean_sheets', 'INTEGER DEFAULT 0'),
        ('saves', 'INTEGER DEFAULT 0'),
        ('goals_conceded', 'INTEGER DEFAULT 0')
    ]
    for col_name, col_def in new_cols:
        if col_name not in existing:
            c.execute(f'ALTER TABLE players ADD COLUMN {col_name} {col_def}')
            print(f'Added column: {col_name}')
        else:
            print(f'Column {col_name} already exists')
    conn.commit()
    conn.close()
    print("Database migration completed successfully.")

if __name__ == '__main__':
    migrate()
