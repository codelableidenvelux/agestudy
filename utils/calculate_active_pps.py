def calculate_active_participants1():
    select = f"SELECT time_exec,user_id FROM task_completed"
    tasks_times = db.execute(select,("",), 1)
    pps = [element[1] for element in tasks_times]
    all_participants = np.unique(pps)
    # get date 6 months ago
    active_participants = [];
    date_6_months_ago = datetime.now() - timedelta(weeks=26)
    for pp in all_participants:
      tasks = [element[0] for element in tasks_times if element[1] == int(pp)]
      months_executed_tasks = list(np.unique([trunc_datetime(element) for element in tasks]))
      if any([date > date_6_months_ago for date in months_executed_tasks]):
          active_participants.append(int(pp))
    return len(active_participants)

def trunc_datetime(someDate):
    return someDate.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

def calculate_active_participants():
    date_6_months_ago = datetime.now() - timedelta(weeks=26)
    date_str = date_6_months_ago.strftime("%Y-%m-%d")
    select = f"SELECT user_id FROM task_completed WHERE time_exec >= '{date_str}'"
    tasks_times = db.execute(select,("",), 1)
    all_participants = np.unique(tasks_times)
    return len(all_participants)
