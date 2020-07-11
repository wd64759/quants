-- add indexes 
create index trdt_idx on tickers(trade_date)
alter table tickers add primary key (ts_code, trade_date)