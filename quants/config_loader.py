import configparser
import os

root_dir = os.path.dirname(os.path.abspath('.'))
config_file = os.path.join(root_dir, 'quants', 'config.ini')
cf=configparser.ConfigParser()
cf.read(config_file)

if __name__ == '__main__':
    print(config_file)
    print(cf.get('STOCK_SERVER', 'token'))