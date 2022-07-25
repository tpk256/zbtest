import json
import subprocess
import asyncio
import logging
import sys
from remote_tv import remote_tv


# LIST TODO:
#  1) TODO изменить проверку на наличие девайса(для любого девайса) через уникальный адрес vender и id
#  2) TODO сделать сборку данных по WEBSOCKETS
#  3) TODO Ликвидировать блокирующую функцию
#  4) лучше чекать по vendor и id


# TEMPLATE COMMANDS
#########################
check_item = r"powershell .\PS\check_camera.ps1 {}"
request_for_send = r'zabbix_sender -z {zabbix} -p {port} -s "Tele" -k {key} -o {value}'
#########################


# SET UP LOGGER
#################################
logInfo = logging.getLogger("INFO")
logInfo.setLevel(logging.INFO)
logError = logging.getLogger("ERR")
logError.setLevel(logging.ERROR)
th = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(message)s")
th.setFormatter(formatter)
logInfo.addHandler(th)
logError.addHandler(th)
###############################


def send_info_tv(text: str):
    subprocess.run(request_for_send.format(zabbix=ip_zabbix, port=port_zabbix, key='info', value=text), shell=True)


with open("config.json") as conf:
    config: dict = json.load(conf)


async def ping_tv() -> bool:
    """
    Устанавливаем websocket соединение с TV
    """
    # try:
    #     async with connect(f"ws://{config['ip_tv']}:3000", open_timeout=2) as tv:
    #         return tv.open
    # except asyncio.exceptions.TimeoutError:
    #     return False

    data = None
    try:
        data = remote_tv(timeout=4)

    except:
        ...
    if data is None:
        return False
    logInfo.info(f"Data from TV {data}.\n")
    send_info_tv(data)
    return True


async def send_data(statusDevices: list[bool]) -> bool:
    """
    :return: True если данные отправились,иначе False
    """
    keys = ["PINGTV", "STATECAMERA", "STATETV", "STATEAPP"]

    values = map(int, statusDevices)

    for key, value in zip(keys, values):
        code = subprocess.run(request_for_send.format(key=key, value=value), capture_output=True, shell=True)
        await asyncio.sleep(0.3)
        logInfo.info(f"msg({key}): {code.stdout}; code - {code.returncode}")
        if code.returncode != 0:
            return False
    return True


async def check_camera() -> bool:
    """
        Проверка на отвал девайсa.
        :return: True если всё отлично,иначе False
    """
    #  TODO
    TEMP = "RealSense(TM)"
    camera = subprocess.run(check_item.format(TEMP), capture_output=True, shell=True)
    return camera.stdout == str(True)


async def check_tv() -> bool:
    """
        Проверка на отвал девайсa.
        :return: True если всё отлично,иначе False
    """

    TEMP = "LG TV"
    tv = subprocess.run(check_item.format(TEMP), capture_output=True, shell=True)
    return tv.stdout == str(True)


async def get_app_status(name="slide.exe") -> bool:
    """
    Проверка на активность приложения
    :param name: Тут указываем имя процесса для проверки (РЕГИСТРО ЗАВИСИМЫЙ)
    :return: True если процесс запущен,иначе False
    """
    req = f'powershell .\PS\isrun_app.ps1 {name}'
    answer = subprocess.run(req, shell=True, capture_output=True).stdout
    return answer == str(True)


async def main():
    global ip_zabbix, port_zabbix
    ip_zabbix, port_zabbix = config["server_zabbix"]

    name_app = config["name_app"]
    print(name_app)

    logInfo.info(msg="Start script!")
    while True:

        data_send = await asyncio.gather(ping_tv(), check_camera(), check_tv(), get_app_status(name_app))
        try:
            logInfo.info(msg=f"PING_TV:{data_send[0]}; STATE_CAMERA:{data_send[1]}; STATE_TV:{data_send[2]}; STATE_APP: {data_send[3]}.\n")

            state_send = await asyncio.wait_for(send_data(data_send), timeout=2.)
            if state_send:
                logInfo.info(msg="Successful send a message.\n")
            else:
                logError.error(msg="Error send a message!\n")
        except asyncio.exceptions.TimeoutError:
            await asyncio.sleep(5)
            continue

        await asyncio.sleep(60)

asyncio.run(main())




