###################
# Получение mac tv и запись в config.json.
# Выполняется только при установке!
# №1
###################


import json
from getmac import get_mac_address
with open("config.json") as f:
    config: dict = json.load(f)

ip_tv = config.get("ip_tv")

if not ip_tv:
    ip_tv = input("Введите ip tv: \t")

mac_tv = get_mac_address(ip=ip_tv).replace(":", "-").upper()

config['mac_address_tv'] = mac_tv

with open("config.json", "w") as f:
    json.dump(config, f)
