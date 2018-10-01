CREATE DATABASE if not exists wallets;

CREATE USER walletman WITH PASSWORD 'xxxxxxxxx';

ALTER USER walletman WITH PASSWORD 'xxxxxxxxx';

GRANT select, insert ON TABLE wallets.ethereum TO walletman;

select utc_filename, utc_json from wallets.ethereum where id =?;

select * from wallets.ethereum 

select * from huhula.bill;
update huhula.bill set chain_date = null;

-- show tables from wallets;
-- select * from  huhula.users;

-- update huhula.users set wid = null, account = null;

-- drop table wallets.ethereum;

CREATE TABLE wallets.ethereum(
  id UUID PRIMARY KEY default gen_random_uuid(),
  inserted_at TIMESTAMP not null DEFAULT now(),
  utc_filename string,
  utc_json string
);

alter table wallets.ethereum drop column   chain_updated_at;


