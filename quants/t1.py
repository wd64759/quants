from sqlalchemy import create_engine
from config_loader import cf as config

dbURL = config.get('MYSQL_DB', 'conn')
engine = create_engine(dbURL, encoding='utf-8', connect_args={'auth_plugin': 'mysql_native_password'})
sample = engine.execute("select * from tickers limit 10").fetchall()
# print(sample.fetchall())

findBest = lambda x: max(zip([t[8] for t in x], x))
stock = findBest(sample)
print(stock)