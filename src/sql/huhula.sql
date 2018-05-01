CREATE DATABASE if not exists huhula;

-- drop TABLE huhula.users;

CREATE TABLE huhula.users(
  id UUID PRIMARY KEY default gen_random_uuid(),
  inserted_at TIMESTAMP not null DEFAULT now(),
  userhash string not null,
  unique INDEX (userhash)
);  

insert into huhula.users(userhash) values('patient zero');
insert into huhula.users(userhash) values('strix');
insert into huhula.users(userhash) values('owl');
insert into huhula.users(userhash) values('olga');
insert into huhula.users(userhash) values('daniel');
insert into huhula.users(userhash) values('Ivan');
insert into huhula.users(userhash) values('Igor');
insert into huhula.users(userhash) values('Vladimir');
-- drop TABLE huhula.spots;

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
);

alter table huhula.spots add column client_at int default 0;

insert into huhula.spots(informer_id,informed_at,azimuth,altitude,longitude,latitude,spot) values('e732e330-ad88-4e28-bd94-70e0cedb9952',12345,123.45678,1.23,3.45,6.78,2);

-- drop view huhula.recentspots;

CREATE VIEW huhula.recentspots (id, spot, age, dist, latitude, longitude) AS 
	select id, spot, age, sqrt(df*df + dl*dl) * 6371e3 as dist, latitude, longitude from (
		select sp.id, sp.spot, age(sp.inserted_at) as age, (cast(longitude as float)*pi()/180 - -117.72369671*pi()/180) * cos((cast(latitude as float)*pi()/180 + 33.57830762*pi()/180)/2) as dl,
		(cast(latitude as float)*pi()/180 - 33.57830762*pi()/180) as df, latitude, longitude from huhula.spots as sp   
		where taker_id is null -- and age(sp.inserted_at) < INTERVAL '2d2h1m1s1ms1us6ns'
		order by age(sp.inserted_at) 
  		) order by  sqrt(df*df + dl*dl) * 6371e3 
  		limit 10

select * from huhula.recentspots;

select sqrt(df*df + dl*dl) * 6371e3 as dm, latitude, longitude  from (
select (cast(longitude as float)*pi()/180 - -117.72369671*pi()/180) * cos((cast(latitude as float)*pi()/180 + 33.57830762*pi()/180)/2) as dl,

(cast(latitude as float)*pi()/180 - 33.57830762*pi()/180) as df, latitude, longitude from spots

) 
-- where round(latitude,4) = 33.5783 and round(longitude,4)=-117.7237
order by  sqrt(df*df + dl*dl) * 6371e3 
    
