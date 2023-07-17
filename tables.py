def build_tables(cur):
    cur.execute(
        """CREATE TABLE IF NOT EXISTS Event(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name VARCHAR,
          range VARCHAR, 
          ts VARCHAR, 
          pt INTEGER)""")

    cur.execute(
        """CREATE TABLE IF NOT EXISTS Parameter(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name VARCHAR,
          value_type VARCHAR)""")

    cur.execute(
        """CREATE TABLE IF NOT EXISTS EventData(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          value_numeric NUMERIC,
          value_char VARCHAR,
          parameter_id INTEGER,
          event_id INTEGER,
          FOREIGN KEY (parameter_id) REFERENCES Parameter (id),
          FOREIGN KEY (event_id) REFERENCES Event (id));
      """)
