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
add an admin
update = "UPDATE SESSION_INFO SET admin = (%s) WHERE user_id=220;"
alter = "ALTER TABLE session_info ADD COLUMN promo_code VARCHAR(100);"
alter = "ALTER TABLE session_info ADD UNIQUE promo_code;"
alter = "ALTER TABLE session_info ADD COLUMN eeg_participation_request INT;"
alter = "ALTER TABLE session_info ADD COLUMN language VARCHAR(100);"

update = "UPDATE SESSION_INFO SET user_name = (%s) WHERE user_id=997;"

update = "UPDATE SESSION_INFO SET duplicate_id = (%s) WHERE user_id=(%s);"
alter = "ALTER TABLE rec_system ADD COLUMN date_collected TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"
alter = "ALTER TABLE session_info ADD COLUMN eeg_participation_request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"
alter = "ALTER TABLE session_info ALTER COLUMN eeg_participation_request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"

'ALTER TABLE REMINDER ADD COLUMN user_id INT'

select = """
SELECT tt.*
FROM EMAILS tt
INNER JOIN
    (SELECT USER_ID, MAX(TIME_EXEC) AS MaxDateTime
    FROM EMAILS
    GROUP BY USER_ID) groupedtt
ON tt.USER_ID = groupedtt.USER_ID
AND tt.TIME_EXEC = groupedtt.MaxDateTime
"""
