from data import RewardDao
import sqlite3


class RewardService:
    @classmethod
    def add_reward(cls, reward):
        RewardDao.save(reward)

    @classmethod
    def spend_rewards(cls, points_to_spend):
        total_points = RewardDao.get_total_points()
        if total_points == None or total_points < points_to_spend:
            return {"spend_summary" : None, "status": "Not Enough"}

        connection = sqlite3.connect('database.db')
        transaction_history = RewardDao.retrieve_active_records(connection)
        current_points = 0
        spend_summary = {}
        for record in transaction_history:
            rowid, payer, points = record
            current_points = current_points + points
            if current_points <= points_to_spend:
                RewardService().__update_spend_summary(spend_summary, payer, points)
                RewardDao.update_status(0, rowid, connection)
            else:
                points_to_deduct = points - (current_points - points_to_spend)
                RewardService().__update_spend_summary(spend_summary, payer, points_to_deduct)
                RewardDao.update_points(current_points - points_to_spend, rowid, connection)

            if current_points >= points_to_spend:
                break
        connection.commit()
        connection.close()
        return {"spend_summary": spend_summary, "status": "Success"}

    @classmethod
    def get_balance(cls):
        transaction_history = RewardDao.retrieve()
        balance = {}
        for record in transaction_history:
            payer, points, active = record
            if active == 0:
                points = 0
            if balance.get(payer) == None:
                balance[payer] = points
            else:
                balance[payer] = balance[payer] + points
        return balance

    def __update_spend_summary(self, rewards_to_use, payer, points_to_deduct) -> None:
        print("rewards summary {}", rewards_to_use)
        if rewards_to_use.get(payer) == None:
            rewards_to_use[payer] = -points_to_deduct
        else:
            rewards_to_use[payer] = rewards_to_use[payer] - points_to_deduct