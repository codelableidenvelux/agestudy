from db.postgresql import Db
db = Db("")
import csv
import numpy as np
from datetime import datetime,timedelta
from application import check_can_collect_payment
# Get participants that participate for payment and are not withdrawn
select = 'SELECT user_id FROM session_info WHERE consent IS NULL AND user_type = 1'
participating_participants = db.execute(select, ('',),1);
participating_participants = set(np.array(participating_participants).flatten())

# get participants that have performed atleast one task
select2 = 'SELECT user_id FROM TASK_COMPLETED WHERE user_id IS NOT NULL'
participants_task_executed = db.execute(select2, ('',),1);
participants_task_executed = set(np.array(participants_task_executed).flatten())

# get date 6 months ago
date_6_months_ago = datetime.now() - timedelta(weeks=26)

len(participating_participants)
len(participants_task_executed)
intersect = participants_task_executed.intersection(participating_participants)
inter = tuple(map(int, intersect))

participants_task_executed_active = []
participants_task_executed_inactive = []

for p in inter:
  select_time = f"SELECT time_exec FROM TASK_COMPLETED WHERE time_exec= (SELECT MAX(time_exec) FROM TASK_COMPLETED WHERE USER_ID = (%s));"
  last_task = db.execute(select_time,(int(p),), 1)
  can_collect = check_can_collect_payment(int(p))[0]
  # you did a task in the last six months
  if last_task[0][0] > date_6_months_ago and can_collect:
    participants_task_executed_active.append(int(p))
  elif can_collect:
    participants_task_executed_inactive.append(int(p))

# select emails and save in csv
# copy ID from participants_task_executed_active
select_active = 'SELECT email FROM session_info WHERE user_id IN (<IDs>)'
email_adresses_a = db.execute(select_active, ("",),1)
with open("active.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(email_adresses_a)

# copy ID from participants_task_executed_inactive
select_inactive = 'SELECT email FROM session_info WHERE user_id IN (<IDs>)'
email_adresses_i = db.execute(select_inactive, ("",),1)
with open("inactive.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(email_adresses_i)
