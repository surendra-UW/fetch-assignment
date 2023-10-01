from flask import Flask, jsonify, request
import sqlite3
from reward import Reward

app = Flask(__name__)
transaction_history = []

connection = sqlite3.connect("database.db")
c = connection.cursor()

# Create a table if it doesn't exist
c.execute(
    """CREATE TABLE IF NOT EXISTS rewards 
             (rowid INTEGER PRIMARY KEY, payer TEXT NOT NULL, points INTEGER NOT NULL, timestamp TEXT NOT NULL, active INTEGER NOT NULL)"""
)
c.execute(
    """CREATE INDEX IF NOT EXISTS IDX_REWARDS_TIMESTAMP ON
                rewards(timestamp) """
)
connection.close()


@app.route("/add", methods=["POST"])
def add_reward_points():
    input = request.get_json(force=True)
    reward = (input["payer"], input["points"], input["timestamp"], 1)
    connection = sqlite3.connect("database.db")
    c = connection.cursor()
    c.execute(
        "INSERT INTO rewards (payer, points, timestamp, active) VALUES (?,?,?,?)",
        reward,
    )
    connection.commit()
    connection.close()
    return build_response(200, "Successfuly added the reward")


@app.route("/spend", methods=["POST"])
def spend_reward_points():
    input = request.get_json(force=True)
    connection = sqlite3.connect("database.db")
    c = connection.cursor()
    c.execute('SELECT SUM(points) FROM rewards WHERE active = ?', (1,))
    total_points = c.fetchone()[0]

    if total_points < input["points"]:
        return build_response(400, "User doesn't have enough points to redeem")

    current_points = 0
    rewards_to_use = {}
    c.execute("SELECT rowid, payer, points FROM rewards WHERE active = ? ORDER BY timestamp ASC", (1,))
    transaction_history = c.fetchall()
    for record in transaction_history:
        rowid, payer, points = record
        print("rowid {} pauyer {} points {}".format(rowid, payer, points))
        current_points = current_points + points
        if current_points <= input["points"]:
            deduct_points(rewards_to_use, payer, points)
            c.execute('UPDATE rewards SET active = ? WHERE rowid = ?', (0, rowid,))
        else:
            points_to_deduct = points - (current_points - input["points"])
            deduct_points(rewards_to_use, payer, points_to_deduct)
            c.execute('UPDATE rewards SET points = ? WHERE rowid = ?', (current_points - input["points"], rowid,))
            
        if current_points >= input["points"]:
            break

    for record in transaction_history:
        rowid, payer, points = record
        print("rowid {} pauyer {} points {}".format(rowid, payer, points))
    connection.commit()
    connection.close()
    return build_response(200, rewards_to_use)


@app.route("/balance", methods=["GET"])
def get_balance():
    balance = {}
    connection = sqlite3.connect("database.db")
    c = connection.cursor()
    c.execute("SELECT payer, points, active FROM rewards ORDER BY timestamp ASC")
    transaction_history = c.fetchall()
    connection.close()

    for record in transaction_history:
        payer, points, active = record
        if active == 0:
            points = 0
        if balance.get(payer) == None:
            balance[payer] = points
        else:
            balance[payer] = balance[payer] + points

    return build_response(200, balance)


def build_response(status_code, response):
    response = app.make_response(response)
    response.status_code = status_code
    return response


def deduct_points(rewards_to_use, payer, points_to_deduct) -> None:
    if rewards_to_use.get(payer) == None:
        rewards_to_use[payer] = -points_to_deduct
    else:
        rewards_to_use[payer] = rewards_to_use[payer] - points_to_deduct


if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=False)
