from data import RewardDao


class RewardService:
    @classmethod
    def add_reward(cls, reward):
        RewardDao.save(reward)

    @classmethod
    def spend_rewards(cls, points):
        total_points = RewardDao.get_total_points()
        print("total poinst ", total_points)
        if total_points == None or total_points < points:
            return {"spend_summary" : None, "status": "Not Enough"}

        spend_summary = RewardDao.update_active_records(points) 
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
