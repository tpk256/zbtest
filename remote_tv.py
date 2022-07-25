# №2 Запись api-key для общения с TV
import sys
import json
from pywebostv.discovery import *
from pywebostv.connection import WebOSClient
from pywebostv.controls import *
from websockets.exceptions import WebSocketException




def remote_tv(timeout: int = 60) -> str:
    client = WebOSClient(config['ip_tv'])
    some_data = ''
    try:
        client.connect()
        for status in client.register(config, timeout=timeout):
            if status == WebOSClient.PROMPTED:
                print("Примите регистрацию!")
            elif status == WebOSClient.REGISTERED:
                print("Успешная регистрация!")
    except Exception as exp:
        print("Не получилось подключиться к Tv")
        raise

    return some_data
    #  TODO functional add MORE


if __name__ == "__main__":
    with open("config.json") as f:
        config: dict = json.load(f)

    client_key = config.get("client_key")
    if not client_key:
        store = {}
        client = WebOSClient(config['ip_tv'])
        try:
            client.connect()
            print("Подтвердите сопряжение на телевизоре")
            for status in client.register(store):
                if status == WebOSClient.PROMPTED:
                    print("Примите регистрацию!")
                elif status == WebOSClient.REGISTERED:
                    print("Успешная регистрация!")
                    config["client_key"] = store["client_key"]
                    with open("config.json", "w") as f:
                        json.dump(config, f)
        except Exception as exp:
            print("Не получилось подключиться к Tv")

    else:
        for _ in range(5):
            try:
                client = WebOSClient(config['ip_tv'])
                client.connect()
                for status in client.register(config):
                    ...
                system = SystemControl(client)
                system.power_off()
                break
            except:
                continue



