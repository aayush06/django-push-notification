from uuid import uuid4
import csv
from django.http import JsonResponse
from myapp import celery_app
from myapp import settings
from pusher import Pusher

@celery_app.task
def file_download_task(data, user_id, host):
        no_of_files = len(data)
        d = []
        for i in range(no_of_files):
                file_name = str(i)+'.csv'
                file_path = str(settings.STATIC_ROOT)+ file_name
                myfile = open(file_path, 'w+')
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                if i == 0:
                        heading = ["employee_name", "address"]
                else:
                        heading = ["org_name","org_address","org_owner","org_type"]
                wr.writerow(heading)
                for j in data[i]:
                        wr.writerow(j.values())
                d.append('http://'+host+'/static/'+file_name)
        print(d)
        pusher = Pusher(app_id="690177",key="d8672e8e8ba4f85cd510",secret="c343542380b9410015da",cluster="ap2")
        channel="download_channel"
        event_data = {"files_path":d}
        pusher.trigger([channel,],"download_event",event_data)