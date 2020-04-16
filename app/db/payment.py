from postgresql import Db
from datetime import datetime, timedelta
db = Db("")
def calculate_payment(id):
    """
    Calculate the total amount of money the user has earned since last payment collection
    """
    # get the completed tasks where the user has not completed payment
    select = f"SELECT * FROM TASK_COMPLETED WHERE USER_ID = (%s) AND COLLECT NOT IN ( 0 )"
    completed_tasks = db.execute(select, (id,), 1)

    # Select all the tasks (even if the payment has been collected already)
    select_all_tasks = f"SELECT * FROM TASK_COMPLETED WHERE USER_ID = (%s)"
    all_tasks = db.execute(select_all_tasks, (id,), 1)

    # Assume that payment for task can be collected (because they have not collected payment this month yet)
    can_collect_task_this_month = True
    # go over all the tasks
    for i in all_tasks:
        print(i)
        # check if a task (not a survey) has been performed this month AND check if payment has alread been collected this month
        # If this is true, since payment for tasks can only be collected once a month set can_collect_task_this_month to false
        print(i[-1])
        print(type(i[-1]))
        if type(i[-1]) is datetime:
            print(i[-1])
            print("yes")
            if (i[2] != 4 or i[2] != 5) and i[-1].month == datetime.now().month:
                can_collect_task_this_month = False


    # seperate each task per month
    months_dict = {}
    for task in completed_tasks:
        if task[0].month in months_dict:
            months_dict[task[0].month].append(task)
        else:
            months_dict[task[0].month] = [task]
    # this is the total amount earned
    money_earned = 0
    # this is the amount only for the tasks
    money_earned_tasks = 0

    # Go over every month in the dictionary
    for month in months_dict:
        # Go over every value in that month
        for i in months_dict[month]:
            # select task_id
            task_id = i[2]
            # get the price for that task
            money = db.execute(f"SELECT PRICE FROM TASKS WHERE TASK_ID=(%s)", (task_id,), 1)
            print(money)
            print(task_id)

            # check if its a survey if it is then the user automatically gets paid the price of the survey
            if i[2] == 4 or i[2] == 5:
                money_earned = money_earned + float(money[0]["price"])
            # if it is a task then
            else:
                # calculate the ammount earned for tasks
                money_earned_tasks = money_earned_tasks + float(money[0]["price"])
                print(money_earned_tasks)
                # Check if its smaller than the max value per month add it to the total amount earned
                if money_earned_tasks < (80-(10.5+1.75))/(12*3) and can_collect_task_this_month:
                    money_earned = money_earned + money_earned_tasks
        # set the amount for the tasks to 0 every month as not to go over the total value
        money_earned_tasks = 0
        # round to 2 decimals
    return round(money_earned, 2)
if __name__ == '__main__':
    total = calculate_payment(108)
    print(f"total: {total}")
