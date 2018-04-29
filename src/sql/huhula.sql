CREATE DATABASE if not exists huhula;

-- drop TABLE huhula.users;

CREATE TABLE huhula.users(
  id UUID PRIMARY KEY default gen_random_uuid(),
  inserted_at TIMESTAMP not null DEFAULT now(),
  userhash string not null,
  unique INDEX (userhash)
);  

insert into huhula.users(userhash) values('patient zero');
-- drop TABLE huhula.spots;

CREATE TABLE huhula.spots(
  id UUID PRIMARY KEY default gen_random_uuid(),
  informer_id UUID references users not null,
  inserted_at TIMESTAMP not null DEFAULT now(),
  informed_at int not null,
  taken_at TIMESTAMP null,
  taker_id UUID references users null,
  azimuth decimal(8,5) not null,
  altitude decimal(19,15) not null,
  longitude decimal(19,15) not null,
  latitude decimal(19,15) not null,
  spots JSONB
);

insert into huhula.spots(informer_id,informed_at,azimuth,altitude,longitude,latitude,spots) values('e732e330-ad88-4e28-bd94-70e0cedb9952',12345,123.45678,1.23,3.45,6.78,'[0,2,3]');

-- drop TABLE huhula.complaints;

CREATE TABLE huhula.complaints(
  id UUID PRIMARY KEY default gen_random_uuid(),
  inserted_at TIMESTAMP not null DEFAULT now(),
  submitter_id UUID references users not null,
  spot_id UUID references spots not null,
  description string not null
);

    
