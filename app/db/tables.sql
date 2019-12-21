CREATE TABLE SESSION_INFO (
  user_id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY(START WITH 0,
  INCREMENT BY 1),
  user_name VARCHAR(255) NOT NULL,
  participation_code VARCHAR(255),
  email VARCHAR(255),
  gender INT NOT NULL,
  birthyear DATE,
  pas_hash VARCHAR(255),
  pas_salt VARCHAR(255),
  user_type INT
);
