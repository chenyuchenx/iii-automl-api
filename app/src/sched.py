from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from config import configs as p
import app.database as db, app.logs as log, random, app.src as utils, pandas as pd

MongoDB     = db.MongoDB()
scheduler   = BackgroundScheduler()
sched       = BackgroundScheduler()

def __init__():
    log.sys_log.info(f"[ASP] Task scheduler up: {datetime.utcnow()}")
    pass