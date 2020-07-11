import configparser
import os

root_dir = os.path.dirname(os.path.abspath('.'))
config_file = os.path.join(root_dir, 'quants', 'config.ini')
if not os.path.isfile(config_file):
    config_file = 'D:\code\quants\quants\config.ini'
    
cf=configparser.ConfigParser()
cf.read(config_file)

def main():
    print(config_file)
    print(cf.get('STOCK_SERVER', 'token'))

if __name__ == '__main__':
    main()    