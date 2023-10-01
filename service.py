from data import RewardDao


class RewardService:
    @classmethod
    def add_reward(cls, reward):
        RewardDao.save(reward)

    @classmethod
    def spend_rewards(cls, points):
        total_points = RewardDao.get_total_points()
        if total_points == None or total_points < points:
            return ("Not Enough")

        return RewardDao.update_active_records() 

    @classmethod
    def get_balance(cls):
        transaction_history = RewardDao.retrieve()
        balance = {}
        for record in transaction_history:
            payer, points, active = record
            if active == 0:
                oints = 0
            if balance.get(payer) == None:
                balance[payer] = points
            else:
                balance[payer] = balance[payer] + points
        return balance
