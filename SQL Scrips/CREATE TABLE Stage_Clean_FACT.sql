CREATE TABLE Stage_Clean_FACT 
(
Thread_ID varchar(20) NOT NULL,
ID varchar(20) NOT NULL,
Cat1 varchar(20),
Cat2 varchar(20),
msg varchar(max) NOT NULL,
sender_id varchar(20) NOT NULL,
created_at datetime NOT NULL,
source varchar(20) NOT NULL
)