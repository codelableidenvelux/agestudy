CREATE TABLE SESSION_INFO (
  user_id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY(START WITH 1 INCREMENT BY 1),
  user_name VARCHAR(255) NOT NULL UNIQUE,
  email VARCHAR(1000) NOT NULL,
  gender INT NOT NULL,
  collect_possible INT NOT NULL,
  for_money INT NOT NULL,
  user_type INT NOT NULL,
  birthyear DATE NOT NULL,
  pas_hash VARCHAR(255) NOT NULL,
  participation_id VARCHAR(255),
  consent INT,
  time_sign_up TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  admin INT,
  credits_participant INT,
  promo_code VARCHAR(100),
  duplicate_id INT,
  language VARCHAR(100),
  eeg_participation_request INT,
  eeg_participation_request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  phone_type INT
);


CREATE TABLE TASKS (
  task_id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY(START WITH 1 INCREMENT BY 1),
  task_link VARCHAR(255),
  dutch_link VARCHAR(255),
  task_name VARCHAR (100) NOT NULL,
  frequency DECIMAL(4,3) NOT NULL,
  price DECIMAL(5,3) NOT NULL,
  youtube_link VARCHAR(255)
);

CREATE TABLE REMINDER (
  email_adress VARCHAR(1000),
  user_id INT,
  time_exec TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE EMAILS (
  user_id INT,
  time_exec TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  email_sent INT
);

CREATE TABLE rec_system(
  user_id INT NOT NULL,
  time_exec TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  promo_code VARCHAR(100) NOT NULL,
  f_promo_code VARCHAR(100) NOT NULL,
  collect INT,
  date_collected TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE RESET_PASSWORD(
  user_id INT NOT NULL,
  time_exec TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expiry_time TIMESTAMP NOT NULL,
  hash VARCHAR(255) NOT NULL,
  reset_id VARCHAR(255) NOT NULL UNIQUE
);


CREATE TABLE BB_BOARD(
  time_insert TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  user_id INT NOT NULL,
  msg VARCHAR(500) NOT NULL,
  msg_title VARCHAR(500)
  participation_id VARCHAR(255),
  show_msg INT,
  FOREIGN KEY (user_id)
    REFERENCES SESSION_INFO(user_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE
);


CREATE TABLE TASK_COMPLETED(
  time_exec TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  user_id INT NOT NULL,
  task_id INT NOT NULL,
  collect INT NOT NULL,
  date_collected TIMESTAMP,
  next_collection TIMESTAMP,
  FOREIGN KEY (user_id)
    REFERENCES SESSION_INFO(user_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE,
  FOREIGN KEY (task_id)
    REFERENCES TASKS(task_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE

);

CREATE TABLE TRACKED_TASK (
  time_exec TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  user_id INT NOT NULL,
  task_id INT NOT NULL,
  FOREIGN KEY (user_id)
    REFERENCES SESSION_INFO(user_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE,
  FOREIGN KEY (task_id)
    REFERENCES TASKS(task_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE,
  status INT NOT NULL
);
