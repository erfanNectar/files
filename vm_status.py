
import psutil
import time
import os
import math
import random
import json
import subprocess
import re
from paho.mqtt import client as mqtt_client


# mqtt auth
broker = '15.185.85.107'
port = 1883
topic = "nectar/Tridium/aws-virtual-device/data"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'vm-status'
password = 'VMStatus'

def connect_mqtt():

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client,data):
    msg_count = 0
    msg = f"{json.dumps(data)}"
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")
    time.sleep(1)



def convert_size_p(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0"
#    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return s

data = {}
data['reason'] = 'CHANGE_OF_VALUE'
data['time'] = int(time.time()*1000.0)
data['id'] = '2137317c-4bed-4f40-b865-ac8d079a98fc'

points = []

# cpu
pointData = {}
pointData["data"] = psutil.cpu_percent(interval=1)
pointData["pointName"]="CPU"
pointData["status"] = "{ok}"
points.append(pointData)

# cpu per core
temp_core = 1
for cores in psutil.cpu_percent(interval=1,percpu=1):
    pointData = {}
    pointData["data"] = psutil.cpu_percent(interval=1)
    pointData["pointName"]="CPU Core "+str(temp_core)
    temp_core = temp_core +1
    pointData["status"] = "{ok}"
    points.append(pointData)


# cpu core count
pointData = {}
pointData["data"] = os.cpu_count()
pointData["pointName"]="CPU Core Count"
pointData["status"] = "{ok}"
points.append(pointData)

# ram
pointData = {}
pointData["data"] = psutil.virtual_memory().percent
pointData["pointName"]="Ram Used Percent"
pointData["status"] = "{ok}"
points.append(pointData)

# ram used
pointData = {}
pointData["data"] = convert_size(psutil.virtual_memory().used)
pointData["pointName"]="Ram Used"
pointData["status"] = "{ok}"
points.append(pointData)

# total ram
pointData = {}
pointData["data"] = convert_size(psutil.virtual_memory().total)
pointData["pointName"]="Total Ram"
pointData["status"] = "{ok}"
points.append(pointData)


# disk internal
pointData = {}
pointData["data"] = convert_size(psutil.disk_usage("/").used)
pointData["pointName"]="Internal Hard Disk Used"
pointData["status"] = "{ok}"
points.append(pointData)

# disk internal total
pointData = {}
pointData["data"] = convert_size(psutil.disk_usage("/").total)
pointData["pointName"]="Internal Hard Disk Total"
pointData["status"] = "{ok}"
points.append(pointData)


# disk internal percent
pointData = {}
pointData["data"] = psutil.disk_usage("/").percent
pointData["pointName"]="Internal Hard Disk Used Percent"
pointData["status"] = "{ok}"
points.append(pointData)


# disk External
pointData = {}
pointData["data"] = convert_size(psutil.disk_usage("/nectar").used)
pointData["pointName"]="External Hard Disk Used"
pointData["status"] = "{ok}"
points.append(pointData)

# disk External total
pointData = {}
pointData["data"] = convert_size(psutil.disk_usage("/nectar").total)
pointData["pointName"]="External Hard Disk Total"
pointData["status"] = "{ok}"
points.append(pointData)


# disk External percent
pointData = {}
pointData["data"] = psutil.disk_usage("/nectar").percent
pointData["pointName"]="External Hard Disk Used Percent"
pointData["status"] = "{ok}"
points.append(pointData)

# swap
pointData = {}
pointData["data"] = psutil.swap_memory().percent
pointData["pointName"]="Swap Memory"
pointData["status"] = "{ok}"
points.append(pointData)

# disk alarm
alarmFlag = False
regx1 = re.compile('([0-9]*[0-9]*[0-9])%')
with open("/nectar/software/installation/taskscheduler/path.txt", "w+") as outfile:
  subprocess.call("df -h", shell=True, stdout=outfile)
time.sleep(1)
infile = r"/nectar/software/installation/taskscheduler/path.txt"
with open(infile,"r") as f:
    f = f.readlines()
for lines in f:
    if re.findall(regx1,lines)!=[]:
        if int(re.findall(regx1,lines)[0]) >= 80:
            alarmFlag = True


pointData = {}
pointData["data"] = alarmFlag
pointData["pointName"]="Hard Disk Over Utilization Alarm"
pointData["status"] = "{ok}"
points.append(pointData)

# -------test-------
# regx1 = re.compile('[0-9]*[0-9]*[0-9]\.[0-9]')
# regx2 = re.compile('[0-9]*[1-9]')
# with open("/nectar/software/installation/taskscheduler/path2.txt", "w+") as outfile:
#   subprocess.call("top | head -n 12", shell=True, stdout=outfile)
# top_cpu = []
# pid_data = {}
# infile = r"/nectar/software/installation/taskscheduler/path2.txt"
# with open(infile,"r") as f:
#     f = f.readlines()
# for lines in f[-5:]:
#     pid_data = {}
#     if re.findall(regx1,lines)!=[]:
#         pid_data['cpu_usage'] = re.findall(regx1,lines)[0]
#         pid_data['pid'] = re.findall(regx2,lines)[0]
#         top_cpu.append(pid_data)

# for data_p in top_cpu:
#     # print(data_p['pid'])
#     try :
#         hc = {}
#         hc["pid"] = data_p['pid']
#         hc["name"] = psutil.Process(int(data_p['pid'])).name()
#         hc["cpu_usage"] = data_p['cpu_usage']
#         hc["ram_usage_p"] = convert_size_p(psutil.Process(int(data_p['pid'])).memory_info().rss)
#         hc["status"] = psutil.Process(int(data_p['pid'])).status()
#     except:
#         hc = {}
#         hc["pid"] = data_p['pid']
#         hc["name"] = "no data"
#         hc["cpu_usage"] = data_p['cpu_usage']
#         hc["ram_usage_p"] = "no data"
#         hc["status"] = "killed"

#     pointData = {}
#     pointData["data"] = "pid : "+str(hc["pid"])+" = name : "+hc["name"]+" = cpu_usage : "+str(hc["cpu_usage"])+" = ram_usage : "+str(hc["ram_usage_p"])+" = status : "+hc["status"]
#     pointData["pointName"]="Top CPU Used "+str(top_cpu.index(data_p)+1)
#     pointData["status"] = "{ok}"
#     points.append(pointData)


# ---------------------
# process printing

processArray = []
for process in psutil.pids():
    processData ={}
    processData["pid"] = psutil.Process(process).pid
    processData["name"] = psutil.Process(process).name()
    processData["cpu_usage"] = psutil.Process(process).cpu_percent(interval=None)
    processData["ram_usage"] = psutil.Process(process).memory_info().rss
    processData["ram_usage_p"] = convert_size_p(psutil.Process(process).memory_info().rss)
    processData["status"] = psutil.Process(process).status()
    processArray.append(processData)

processArray.sort(key=lambda x: x["cpu_usage"],reverse=True)
highCPU =  processArray[:5]
processArray.sort(key=lambda x: x["ram_usage"],reverse=True)
highMemory = processArray[:5]

for hc in highCPU:
    pointData = {}
    pointData["data"] = "pid : "+str(hc["pid"])+" = name : "+hc["name"]+" = cpu_usage : "+str(hc["cpu_usage"])+" = ram_usage : "+str(hc["ram_usage_p"])+" = status : "+hc["status"]
    pointData["pointName"]="Top CPU Used "+str(highCPU.index(hc)+1)
    pointData["status"] = "{ok}"
    points.append(pointData)

for hm in highMemory:
    pointData = {}
    pointData["data"] = "pid : "+str(hm["pid"])+" = name : "+hm["name"]+" = cpu_usage : "+str(hm["cpu_usage"])+" = ram_usage : "+str(hm["ram_usage_p"])+" = status : "+hm["status"]
    pointData["pointName"]="Top Ram Used "+str(highMemory.index(hm)+1)
    pointData["status"] = "{ok}"
    points.append(pointData)

data["points"] = points
# print(data)

client = connect_mqtt()
client.loop_start()
publish(client,data)
