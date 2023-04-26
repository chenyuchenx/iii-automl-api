import logging, os

sys_log = logging.getLogger('root')
sys_log.setLevel(level=logging.DEBUG)

def log_init():

    os.makedirs('logs', exist_ok=True)
    fh = logging.FileHandler(filename='logs/logs.log', encoding='utf-8')
    formatter = logging.Formatter("%(asctime)s - %(module)s - %(funcName)s - line:%(lineno)d - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    fh.setLevel(level=logging.INFO)
    sys_log.addHandler(fh)