CREATE TABLE SESSION_INFO (
  user_id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY(START WITH 0,
  INCREMENT BY 1),
  user_name VARCHAR(255) NOT NULL UNIQUE,
  email VARCHAR(1000) UNIQUE,
  participation_code VARCHAR(255),
  gender INT NOT NULL,
  collect_possible INT,
  for_money INT,
  user_type INT NOT NULL,
  birthyear DATE,
  pas_hash VARCHAR(255)
);
