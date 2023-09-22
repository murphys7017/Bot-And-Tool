import time
from apscheduler.schedulers.background import BackgroundScheduler
import requests





def bk(s):
    print(s)
    params={
                "message": s,

        }
    params["user_id"] = '815049548'
    params['message_type'] = 'private'
    response = requests.get('http://localhost:8882/send_msg', params=params)
scheduler = BackgroundScheduler()
scheduler.start()
job = scheduler.add_job(bk,args=['sssssssssss'],trigger='interval',seconds=5)

time.sleep(17)
job.remove()
