create table messages (
    id integer primary key,
    channel_id integer NOT NULL,
    user_id integer NOT NULL,
    time_stamp varchar(100),
    msg varchar(200),
    foreign key(channel_id) references channels(id),
    foreign key(user_id) references users(id)    
);

insert into messages (id,channel_id,user_id,time_stamp,msg) values (
    1,1,1,"time1","msg hello school from geetesh"
);

select * from users;
select * from channels;
select * from messages;

delete from messages where time_stamp = "Sat Aug 17 08:14:39 2019" and user_id = (select id from users where username = "Harish") and msg = "hi school this is geetesh ahuja" and channel_id = (select id from channels where channel_name = "School")

select (select username from users where id = messages.user_id) as username,
channel_name,msg,time_stamp from messages 
join channels on messages.channel_id = channels.id where messages.channel_id = 1;


select id from channels where channel_name = "School";

DELETE from users;
DELETE from channels;
DELETE from messages;



