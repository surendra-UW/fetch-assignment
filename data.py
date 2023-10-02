import sqlite3

class Reward:

    def __init__(self, payer, points, timestamp, active):
        self.payer = payer
        self.points = points
        self.timestamp = timestamp
        self.active = active

    def __dict__(self):
        return {
            'payer': self.payer,
            'points': self.points,
            'timestamp': self.timestamp
        }
    
class RewardDao:

    @classmethod
    def save(cls, reward) -> None:
        with sqlite3.connect("database.db") as connection:
            c = connection.cursor()
            c.execute(
                "INSERT INTO rewards (payer, points, timestamp, active) VALUES (?,?,?,?)",
                    (reward.payer, reward.points, reward.timestamp, reward.active)
                )
            connection.commit()

    @classmethod
    def retrieve(cls):
        with sqlite3.connect("database.db") as connection:
            c = connection.cursor()
            c.execute("SELECT payer, points, active FROM rewards ORDER BY timestamp ASC")
            transaction_history = c.fetchall()

        return transaction_history
    
    @classmethod
    def retrieve_active_records(cls, connection):
        with sqlite3.connect("database.db") as connection:
            c = connection.cursor()
            c.execute("SELECT rowid, payer, points FROM rewards WHERE active = ? ORDER BY timestamp ASC", (1,))
            transaction_history = c.fetchall()
        return transaction_history

    @classmethod
    def update_points(cls, points, rowid, connection):
        c = connection.cursor()
        c.execute('UPDATE rewards SET points = ? WHERE rowid = ?', (points, rowid))

    @classmethod
    def update_status(cls, active, rowid, connection):
        c = connection.cursor()
        c.execute(
                        "UPDATE rewards SET active = ? WHERE rowid = ?", (0, rowid)
                    )

    @classmethod
    def initialize_db(cls):
        with sqlite3.connect("database.db") as connection:
            c = connection.cursor()

        # Create a table if it doesn't exist
            c.execute(
            """CREATE TABLE IF NOT EXISTS rewards (rowid INTEGER PRIMARY KEY, payer TEXT NOT NULL,
            points INTEGER NOT NULL, timestamp TEXT NOT NULL, active INTEGER NOT NULL)"""
            )
            c.execute(
            """CREATE INDEX IF NOT EXISTS IDX_REWARDS_TIMESTAMP ON
                rewards(timestamp) """
            )

    @classmethod
    def get_total_points(cls):
        with sqlite3.connect("database.db") as connection:
            c = connection.cursor()
            c.execute("SELECT SUM(points) FROM rewards WHERE active = ?", (1,))
            return c.fetchone()[0]
