from flask import Flask, jsonify, request
from datetime import datetime
from service import RewardService
from data import *

app = Flask(__name__)

RewardDao.initialize_db()

@app.route("/add", methods=["POST"])
def add_reward():
    input = request.get_json(force=True)

    if input['payer'].isspace(): 
        return build_response(400, "Bad request empty payer name")
    if not is_valid_date(input['timestamp'], "%Y-%m-%dT%H:%M:%SZ"):
        return build_response(400, "Bad request improper date format")
    
    try:
        reward = Reward(input['payer'], input['points'], input['timestamp'], 1)
        RewardService.add_reward(reward)
    except Exception as exception:
        return build_response(500, f"exception occured while adding reward {exception}")

    return build_response(200, "Successfuly added the reward")

def is_valid_date(date_string, format):
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False
    
@app.route("/spend", methods=["POST"])
def spend_rewards():
    input = request.get_json(force=True)
    response = RewardService.spend_rewards(input["points"])
    if response[0] == "Not Enough":
        return build_response(400, "user doesn’t have enough points")
    return build_response(200, response)


@app.route("/balance", methods=["GET"])
def balance():
    try:
        balance = RewardService.get_balance()
    except Exception as exception:
        return build_response(500, "Exception occured {}".format(exception))
    return build_response(200, balance)


def build_response(status_code, response):
    response = app.make_response(response)
    response.status_code = status_code
    return response

if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=False)
