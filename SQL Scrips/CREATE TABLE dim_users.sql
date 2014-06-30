CREATE TABLE dim_users_stage 
(
sender_id varchar(20) NOT NULL,
state varchar(20),
active_date datetime,
name varchar(50),
timezone varchar(max),
email varchar(50)
)