def calculate_money(id):
    """
    Calculate the total amount of money the user has earned since last payment collection
    """
select = f"SELECT * FROM TASK_COMPLETED WHERE USER_ID = (%s) AND COLLECT NOT IN ( 0 )"
completed_tasks = db.execute(select, (id,), 1)
select_all_tasks = f"SELECT * FROM TASK_COMPLETED WHERE USER_ID = (%s)"
all_tasks = db.execute(select_all_tasks, (id,), 1)
can_collect_task_this_month = True
months_dict = {}
for task in completed_tasks:
    tmp = int(str(task[0].month)+str(task[0].year))
    if tmp in months_dict:
        months_dict[tmp].append(task)
    else:
        months_dict[tmp] = [task]
money_earned = 0
money_earned_tasks = 0
for month in months_dict:
    for i in months_dict[month]:
        task_id = i[2]
        money = db.execute(f"SELECT PRICE FROM TASKS WHERE TASK_ID=(%s)", (task_id,), 1)
        if i[2] == 4 or i[2] == 5:
            money_earned = money_earned + float(money[0]["price"])
        else:
            money_earned_tasks = money_earned_tasks + float(money[0]["price"])
    if money_earned_tasks <= (80-8)/(12*3) and can_collect_task_this_month:
        money_earned = money_earned + money_earned_tasks
    elif  money_earned_tasks > (80-8)/(12*3) and money_earned_tasks < 72 and can_collect_task_this_month:
        money_earned = money_earned + 2
    money_earned_tasks = 0
    print(money_earned)
return round(money_earned, 2)

def calculate_rec_system_payment(f_promo_code):
    """
    This function calculates the reward/payment for referring friends to the study
    It takes the f_promo_code which is the promo code from the user that is logged in
    The user whose dashboard the payment will appear on.
    """
    total_payment = 0
    successful_completion = 0
    select = "SELECT * FROM rec_system where f_promo_code=(%s) AND COLLECT NOT IN ( 0 )"
    recomended = db.execute(select, (f_promo_code,), 1)
    for i in recomended:
      select = "SELECT user_id,time_sign_up FROM SESSION_INFO WHERE promo_code=(%s)"
      user_info = db.execute(select, (i["promo_code"],), 1)
      today = datetime.now()
      one_year_after_sign_up = user_info[0]["time_sign_up"] + timedelta(weeks = 52)
      if one_year_after_sign_up < today:
        select = "SELECT * FROM TASK_COMPLETED WHERE user_id=(%s)"
        executed_tasks = db.execute(select, (user_info[0]["user_id"],), 1)
        if len(executed_tasks) >= 6:
            total_payment = total_payment + 5
            successful_completion = successful_completion + 1
    return (len(recomended),total_payment, successful_completion)
