CREATE DATABASE if not exists huhula;

CREATE USER huhulaman WITH PASSWORD 'sEBx9gjgzfo';

ALTER USER huhulaman WITH PASSWORD 'xxxxxxxxx';


GRANT select, insert, update, delete ON TABLE huhula.users, huhula.spots, huhula.occupy, huhula.parked, huhula.bill TO huhulaman;

select  userhash from huhula.users limit 2000;

-- delete from huhula.users where userhash like '%test%' limit 50;

-- delete from huhula.users where userhash = '';

-- delete from spots where informer_id in (
-- select id from huhula.users where userhash = '') ;

-- drop TABLE huhula.users;

CREATE TABLE huhula.users(
  id UUID PRIMARY KEY default gen_random_uuid(),
  inserted_at TIMESTAMP not null DEFAULT now(),
  userhash string not null,
  chain_date timestamp,
  balance double precision default 0, 
  unique INDEX (userhash)
);  

-- alter table huhula.users add column chain_date;

-- alter table huhula.users add column balance double precision default 0 ;

select * from huhula.users limit 10;

CREATE TABLE huhula.users(
  id UUID PRIMARY KEY default gen_random_uuid(),
  inserted_at TIMESTAMP not null DEFAULT now(),
  userhash string not null,
  unique INDEX (userhash)
);  


alter table huhula.users add column wallet_balance double precision not null default 0;
alter table huhula.users add column chain_date TIMESTAMP;


drop table huhula.bill;

CREATE TABLE huhula.bill(
  id UUID PRIMARY KEY default gen_random_uuid(),
  inserted_at TIMESTAMP not null DEFAULT now(),
  updated_at TIMESTAMP not null DEFAULT now(),
  user_id UUID references huhula.users not null,
  for_date date not null,
  informed_qty int not null default 0,
  occupied_qty int not null default 0,
  gift double precision not null default 0,
  penalty double precision not null default 0,
  chain_date TIMESTAMP,
  unique INDEX (user_id,for_date)
);  

alter table huhula.bill drop column credit;

update huhula.bill set updated_at=now(), informed_qty=informed_qty+2, occupied_qty=occupied_qty+0, credit=cast((cast((informed_qty+2)*0.1 as double precision)+gift) as double precision), debit=cast((cast((occupied_qty+0) as double precision)+penalty) as double precision) where user_id='d8437a22-14b0-4e72-9672-2c3eb6664c2e' and for_date=cast('2018-07-31 08:43:36.093000' as date)


alter table huhula.bill add column gift double precision not null default 0;
alter table huhula.bill add column penalty double precision not null default 0;

update huhula.bill set gift = 20 where id = '1467a542-f6f6-4530-8876-1774e41149aa';

CREATE VIEW huhula.bill_payable
  AS 
  select user_id, for_date, informed_qty, occupied_qty, gift, penalty, credit, debit, credit - debit as balance from
  (SELECT user_id, for_date, informed_qty, occupied_qty, gift, penalty, cast(informed_qty*0.1 as double precision)+gift as credit, cast(occupied_qty as double precision)+penalty as debit 
  FROM huhula.bill where chain_date is null);

  select * from huhula.bill_payable;
  

select * from huhula.bill;
select * from huhula.occupy order by inserted_at desc limit 10;


alter table huhula.users add column roles string[] default array[];  

-- alter table huhula.users drop column roles;  

select * from huhula.users where userhash in ('113989703630504660150','117684205293445461401');

update huhula.users set roles = array['vendor'] where userhash in ('113989703630504660150','117684205293445461401');


insert into huhula.users(userhash) values('patient zero');
insert into huhula.users(userhash) values('strix');
insert into huhula.users(userhash) values('owl');
insert into huhula.users(userhash) values('olga');
insert into huhula.users(userhash) values('daniel');
insert into huhula.users(userhash) values('Ivan');
insert into huhula.users(userhash) values('Igor');
insert into huhula.users(userhash) values('Vladimir');
-- drop TABLE huhula.spots;
/*
CREATE TABLE huhula.spots(
  id UUID PRIMARY KEY default gen_random_uuid(),
  informer_id UUID references users not null,
  inserted_at TIMESTAMPTZ not null DEFAULT now(),
  informed_at int not null,
  taken_at TIMESTAMP null,
  taker_id UUID references users null,
  azimuth decimal(8,5) not null,
  altitude decimal(19,15) not null,
  longitude decimal(19,15) not null,
  latitude decimal(19,15) not null,
  spot int not null,
  compaint string null
  client_at int not null
);
*/

-- drop TABLE huhula.spotsfloat;

CREATE TABLE huhula.spots(
  id UUID PRIMARY KEY default gen_random_uuid(),
  informer_id UUID references users not null,
  inserted_at TIMESTAMPTZ not null DEFAULT now(),
  informed_at int not null,
  azimuth float not null,
  altitude float not null,
  longitude float not null,
  latitude float not null,
  client_at int not null,
  quantity int default 0,
  orig_quantity default 0,
  mode int default 0  -- 0 for manual 1 for auto reporting 
  direction int[] default null  (-1 - for multiplcae spot with undefined directions
);

alter table huhula.spots add column orig_quantity int default 0;
update huhula.spots set orig_quantity = array_length(direction,1) ;

update huhula.spots set quantity = 9 where id='68635939-de9e-42c7-8092-a7405b91e5f4'

select * from huhula.spots order by inserted_at desc limit 10;

CREATE TABLE huhula.occupy(
  id UUID PRIMARY KEY default gen_random_uuid(),
  spot_id UUID references spots not null,
  inserted_at TIMESTAMPTZ not null DEFAULT now(),
  taken_at TIMESTAMP null,
  taker_id UUID references users null,
  client_at int not null
);


show create table huhula.occupy;

select * from huhula.occupy order by inserted_at desc limit 20;

-- drop TABLE huhula.parked;

CREATE TABLE huhula.parked(
  id UUID PRIMARY KEY default gen_random_uuid(),
  informer_id UUID references users not null,
  inserted_at TIMESTAMPTZ not null DEFAULT now(),
  informed_at int not null,
  azimuth float not null,
  altitude float not null,
  longitude float not null,
  latitude float not null,
  client_at int not null
);

select * from huhula.parked;

select * from huhula.spots_decimal;

insert into huhula.spots
select id, informer_id, inserted_at, informed_at, taken_at, taker_id, cast(azimuth as float) as azimuth, 
  cast(altitude as float) as altitude,
  cast(longitude as float) as longitude,
  cast(latitude as float) as latitude,
  spot,
  compaint,
  client_at from huhula.spotsfloat;

select * from huhula.spots ;

insert into huhula.spots(informer_id,informed_at,azimuth,altitude,longitude,latitude,spot) values('e732e330-ad88-4e28-bd94-70e0cedb9952',12345,123.45678,1.23,3.45,6.78,2);

-- drop view huhula.recentspots;

-- CREATE VIEW huhula.recentspots (id, spot, age, dist, latitude, longitude) AS 
	select id, spot, age, sqrt(df*df + dl*dl) * 6371e3 as dist, latitude, longitude from (
		select sp.id, sp.spot, age(sp.inserted_at) as age, (cast(longitude as float)*pi()/180 - -117.718043230000000*pi()/180) * cos((latitude*pi()/180 + 33.57830762*pi()/180)/2) as dl,
		(latitude*pi()/180 - 33.579969720000000*pi()/180) as df, latitude, longitude from huhula.spots as sp   
		where taker_id is null -- and age(sp.inserted_at) < INTERVAL '2d2h1m1s1ms1us6ns'
		order by age(sp.inserted_at) 
  		) order by  age, sqrt(df*df + dl*dl) * 6371e3 
  		limit 10

select * from huhula.recentspots order by age ;

select sqrt(df*df + dl*dl) * 6371e3 as dm, latitude, longitude  from (
select (cast(longitude as float)*pi()/180 - -117.72369671*pi()/180) * cos((cast(latitude as float)*pi()/180 + 33.57830762*pi()/180)/2) as dl,

(cast(latitude as float)*pi()/180 - 33.57830762*pi()/180) as df, latitude, longitude from spots

) 
-- where round(latitude,4) = 33.5783 and round(longitude,4)=-117.7237
order by  sqrt(df*df + dl*dl) * 6371e3 

select * from users;

select u.userhash, s.inserted_at, latitude, longitude from spots s
inner join users u on (s.informer_id = u.id)
order by inserted_at desc ;

    
