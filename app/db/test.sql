INSERT INTO SESSION_INFO (
user_name, participation_code, email, gender, birthyear, pas_hash, pas_salt, user_type )
VALUES (
'user_name', 'participation_code' , 'email' , 1 ,'1908-09-20' ,'pashash' ,
'passalt',2);

"""
INSERT INTO TASKS (task_link, task_name, frequency, price) VALUES ('https://www.psytoolkit.org/cgi-bin/psy2.6.1/survey?s=VG5Kv', 'corsi', 0.025, 1.75)
INSERT INTO TASKS (task_link, task_name, frequency, price) VALUES ('https://www.psytoolkit.org/cgi-bin/psy2.6.1/survey?s=YGgzj', 'n_back', 0.025, 1.75)
INSERT INTO TASKS (task_link, task_name, frequency, price) VALUES ('https://www.psytoolkit.org/cgi-bin/psy2.6.1/survey?s=tYMyx', 'task_switching', 0.025, 1.75)
INSERT INTO TASKS (task_link, task_name, frequency, price) VALUES ('https://www.psytoolkit.org/cgi-bin/psy2.6.1/survey?s=LnHTW', 'sf_36', 0.5, 1.75)
INSERT INTO TASKS (task_link, task_name, frequency, price) VALUES ('https://www.psytoolkit.org/cgi-bin/psy2.6.1/survey?s=am8BU', 'phone_survey',5, 1.75)
INSERT INTO tasks(task_link, dutch_link, task_name, frequency, price) VALUES ('https://www.psytoolkit.org/cgi-bin/psy2.7.0/survey?s=mGJpj', 'https://www.psytoolkit.org/cgi-bin/psy2.7.0/survey?s=LDWBB', 'rt', 0.025, 1.75);
INSERT INTO tasks(task_link, dutch_link, task_name, frequency, price) VALUES ('https://www.psytoolkit.org/cgi-bin/psy2.7.0/survey?s=UdGC9', 'https://www.psytoolkit.org/cgi-bin/psy2.7.0/survey?s=qTtLL', 'rt_long', 0.025, 1.75);
"""

INSERT INTO TASK_COMPLETED (user_id, task_id) VALUES (1, 0)
