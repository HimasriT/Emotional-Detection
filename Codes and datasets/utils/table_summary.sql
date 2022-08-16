select 
'No of tweets' as label, 
sum(pos) as Positive,
sum(neg) as Negative,
sum(neu) as Neutral,
count(*) as Total
from tweets
where user_id in (select user_id from users)

union
select
"Average Number of Tweets per user" as label,
avg(pos) as Positive,
avg(neg) as Negative,
avg(neu) as Neutral,
avg(tot) as Total
from (
select sum(pos) as pos, sum(neg) as neg, sum(neu) as neu, sum(pos)+sum(neg)+sum(neu) as tot
from tweets
where user_id in (Select user_id from users)
group by user_id
)as tbl 

union

select
'Average Number of Tweets per day' as label,
avg(pos) as Positive,
avg(neg) as Negative,
avg(neu) as Neutral,
avg(tot) as Total
from (
select sum(pos) as pos, sum(neg) as neg, sum(neu) as neu, sum(pos)+sum(neg)+sum(neu) as tot
from tweets
where user_id in (Select user_id from users)
group by tdate
)as tbl

union
select
'Average Number of Tweets per week' as label,
avg(pos) as Positive,
avg(neg) as Negative,
avg(neu) as Neutral,
avg(tot) as Total
from (
select sum(pos) as pos, sum(neg) as neg, sum(neu) as neu, sum(pos)+sum(neg)+sum(neu) as tot
from tweets
where user_id in (Select user_id from users)
group by week(tdate),year(tdate)
)as tbl

union
select
'Average Number of Tweets per user per day' as label,
avg(pos) as Positive,
avg(neg) as Negative,
avg(neu) as Neutral,
avg(tot) as Total
from (
select sum(pos) as pos, sum(neg) as neg, sum(neu) as neu, sum(pos)+sum(neg)+sum(neu) as tot
from tweets
where user_id in (Select user_id from users)
group by user_id,tdate
)as tbl

union
select
'Average Number of Tweets per user per week' as label,
avg(pos) as Positive,
avg(neg) as Negative,
avg(neu) as Neutral,
avg(tot) as Total
from (
select sum(pos) as pos, sum(neg) as neg, sum(neu) as neu, sum(pos)+sum(neg)+sum(neu) as tot
from tweets
where user_id in (Select user_id from users)
group by user_id,week(tdate),year(tdate)
)as tbl