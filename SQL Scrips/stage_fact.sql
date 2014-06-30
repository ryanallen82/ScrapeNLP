CREATE TABLE Stage_FACT 
(
Thread_ID varchar(20) NOT NULL,
ID varchar(20) NOT NULL,
msg varchar(max) NOT NULL,
sender_id varchar(20) NOT NULL,
created_at datetime NOT NULL,
source varchar(20) NOT NULL
)