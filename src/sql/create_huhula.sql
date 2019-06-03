
--CREATE USER huhulaman WITH PASSWORD 'sEBx9gjgzfo';

--ALTER USER huhulaman WITH PASSWORD 'xxxxxxxxx';


--GRANT select, insert, update, delete ON TABLE huhula.users, huhula.spots, huhula.occupy, huhula.parked, huhula.bill, huhula.reference TO huhulaman;

--GRANT select ON TABLE huhula.bill_payable TO huhulaman;

create database huhula;

CREATE TABLE huhula.users(
  id UUID PRIMARY KEY default gen_random_uuid(),
  inserted_at TIMESTAMP not null DEFAULT now(),
  userhash string not null,
  chain_date timestamp,
  balance double precision default 0,
  account string, 
  wid UUID, -- reference to wallets 
  unique INDEX (userhash)
);  

-- alter table huhula.users add column wid UUID;
-- alter table huhula.users add column account string;


-- alter table huhula.users add column chain_date;

-- alter table huhula.users add column balance double precision default 0 ;

--CREATE TABLE huhula.users(
--  id UUID PRIMARY KEY default gen_random_uuid(),
--  inserted_at TIMESTAMP not null DEFAULT now(),
--  userhash string not null,
--  unique INDEX (userhash)
--);  
--

alter table huhula.users add column wallet_balance double precision not null default 0;
-- alter table huhula.users add column chain_date TIMESTAMP;


-- drop table if exists huhula.bill;

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

alter table huhula.bill add column gas_cost double precision;

-- alter table huhula.bill add column gift double precision not null default 0;
-- alter table huhula.bill add column penalty double precision not null default 0;

CREATE VIEW huhula.bill_payable
  AS 
  select user_id, for_date, informed_qty, occupied_qty, gift, penalty, credit, debit, credit - debit as balance from
  (SELECT user_id, for_date, informed_qty, occupied_qty, gift, penalty, cast(informed_qty*0.1 as double precision)+gift as credit, cast(occupied_qty as double precision)+penalty as debit 
  FROM huhula.bill where chain_date is null);

alter table huhula.users add column roles string[] default array[];  

-- alter table huhula.users drop column roles;  

-- drop TABLE huhula.spots;

-- drop TABLE huhula.spotsfloat;

CREATE TABLE huhula.spots(
  id UUID PRIMARY KEY default gen_random_uuid(),
  informer_id UUID references huhula.users not null,
  inserted_at TIMESTAMPTZ not null DEFAULT now(),
  informed_at int not null,
  azimuth float not null,
  altitude float not null,
  longitude float not null,
  latitude float not null,
  client_at int not null,
  quantity int default 0,
  orig_quantity int default 0,
  mode int default 0,  -- 0 for manual 1 for auto reporting 
  direction int[] default null  -- (-1 - for multiplcae spot with undefined directions
);

-- alter table huhula.spots add column orig_quantity int default 0;

-- select * from huhula.spots order by inserted_at desc limit 10;

CREATE TABLE huhula.occupy(
  id UUID PRIMARY KEY default gen_random_uuid(),
  spot_id UUID references huhula.spots not null,
  inserted_at TIMESTAMPTZ not null DEFAULT now(),
  taken_at TIMESTAMP null,
  taker_id UUID references huhula.users null,
  client_at int not null
);


-- drop TABLE huhula.parked;

CREATE TABLE huhula.parked(
  id UUID PRIMARY KEY default gen_random_uuid(),
  informer_id UUID references huhula.users not null,
  inserted_at TIMESTAMPTZ not null DEFAULT now(),
  informed_at int not null,
  azimuth float not null,
  altitude float not null,
  longitude float not null,
  latitude float not null,
  client_at int not null
);

-- drop view huhula.recentspots;

CREATE TABLE huhula.reference(
  id UUID PRIMARY KEY default gen_random_uuid(),
  sender_id UUID references huhula.users not null,
  receiver_id UUID references huhula.users,
  inserted_at TIMESTAMPTZ not null DEFAULT now(),
  updated_at TIMESTAMPTZ,
  from_url string
);


CREATE TABLE huhula.referral(
  id UUID PRIMARY KEY default gen_random_uuid(),
  sender_id UUID references huhula.users not null,
  inserted_at TIMESTAMPTZ not null DEFAULT now()
);

CREATE TABLE huhula.link(
  id UUID PRIMARY KEY default gen_random_uuid(),
  referral_id UUID references huhula.referral not null,
  to_hash string not null,
  inserted_at TIMESTAMPTZ not null DEFAULT now(),
  updated_at TIMESTAMPTZ not null DEFAULT now()
);


