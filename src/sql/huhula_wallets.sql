CREATE DATABASE if not exists wallets;

CREATE USER walletman WITH PASSWORD 'xxxxxxxxx';

ALTER USER walletman WITH PASSWORD 'xxxxxxxxx';

GRANT select, insert, update, delete ON TABLE wallets.ethereum TO walletman;

select * from wallets.ethereum;

-- drop table wallets.ethereum;

CREATE TABLE wallets.ethereum(
  id UUID PRIMARY KEY default gen_random_uuid(),
  inserted_at TIMESTAMP not null DEFAULT now(),
  eth_updated_at TIMESTAMP null,
  utc_json string
);

