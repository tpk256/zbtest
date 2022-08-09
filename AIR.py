from getmac import get_mac_address
from pywebostv.connection import WebOSClient
from pywebostv.controls import SystemControl
from wakeonlan import send_magic_packet
import argparse
import websockets
import json
import logging
import time
import asyncio
import subprocess
import sys


class Exc(Exception):
    """
        Затычка, а то в модуле вызван объект Exception(), а pip это не нравится, таки обошёл.
    """
    ...


class SetUp:
    """
        Actions at setup:
        1)get IP(TV)
        2)get MAC(TV) for wakeOnLan
        3)get Client_key(TV) for remote access to TV
    """

    def __init__(self):
        """
            Load config for record in it MAC(TV);IP(TV);Client_Key(TV);
        """
        with open("config.json") as f:
            self.config: dict = json.load(f)

    def get_ip_tv(self):
        """
            Get Ip tv
        """
        if self.config.get('ip_tv'):
            return
        while ip := input("Write please IP TV that it has in local network\t") + '\n':
            try:
                if all(0 <= number <= 255 for number in map(int, ip.split('.'))):
                    ans = input("Are you sure that ip is {} y/n or yes/no ?\t".format(ip))
                    if ans.lower() in ('yes', 'y'):
                        break
                else:
                    print("x.x.x.x where x may has value 0 <= x <= 255, so to correct your record")
            except ValueError:
                print("WRONG FORMAT! Right format - 255.255.255.255")

        ip = ip.strip()
        self.config['ip_tv'] = ip
        self.save_data()

    def get_mac_tv(self):
        """
            Get Mac tv.
        """
        if self.config.get('mac_address_tv'):
            return
        ans = input("Do you want write MAC(TV)(yes) or you prefer auto get(no)? yes/no or y/n\t")
        if ans.lower() in ("yes", "y"):
            mac = input("Write please mac:\t")
        else:
            mac = get_mac_address(ip=self.config['ip_tv'])
            if mac is None:
                print("Unfortunately, mac address didn't has get, so you need write manually.")
                mac = input("Write please mac:\t")
        self.config['mac_address_tv'] = mac.replace(":", "-").upper()
        self.save_data()
        
    def get_client_key(self):
        """
            Get client key (TV).
        """

        client = WebOSClient(self.config['ip_tv'])
        try:
            client.connect()
            for status in client.register(self.config, timeout=120):  # 120 seconds than you accept linking
                if status == WebOSClient.PROMPTED:
                    print("To accept linking on tv.")
                elif status == WebOSClient.REGISTERED:
                    print("Successful registration.")
                    self.save_data()
        except Exc:
            print("Access to tv was been denied, so you need write client_key manually or restart setUp.")
            
    def save_data(self):
        with open("config.json", "w") as f:
            json.dump(self.config, f)


class Checker(SetUp):  # Inherit because same constructor
    """
        Part by script that will start every day.
    """
    A_D = {"capture_output": True,  # For every request params that const.(Can use functools.partial if you want it)
           "shell": True,
           "timeout": 5}
    TRAPPER_NAMES = ["PINGTV", "STATECAMERA", "STATETV", "STATEAPP"]
    CHECK_APP = r'powershell .\isrun_app.ps1 {}'
    CHECK_ITEM = r"powershell .\check_item.ps1 {}"
    CHECK_CAMERA = r"powershell .\check_camera.ps1"

    REQUEST_SEND = r'zabbix_sender -z {zabbix} -p {port} -s "{host}" -k {key} -o {value}'

    def __init__(self):
        SetUp.__init__(self)
        sd: logging.Logger
        self.info: logging.Logger  # Default values for loggers
        self.error: logging.Logger  # Default values for loggers
        self.server, self.port = self.config['server_zabbix']
        self.set_up_logger()

    @property
    def TvIsConnected(self) -> bool:
        """
            Bool value that mean connect TV to PC. +
            Check device(camera) with status 'OK' in device manager.
        """
        #  TODO change way get status TV

        tv = subprocess.run(Checker.CHECK_ITEM.format(self.config['tv']), **Checker.A_D)
        return tv.stdout.strip().decode() == str(True)

    @property
    def CameraIsConnected(self) -> bool:
        """
            Bool value that mean connect Camera to PC. +
            Check device(camera) with status 'OK' in device manager.
        """
        #  TODO change way get status camera

        camera = subprocess.run(Checker.CHECK_CAMERA, **Checker.A_D)
        return camera.stdout.strip().decode() == str(True)

    @property
    def AppIsOn(self) -> bool:
        """
            Bool value that mean state APP
            APP in process or NOT.
        """
        app = subprocess.run(Checker.CHECK_APP.format(self.config['name_app']), **Checker.A_D)
        return app.stdout.strip().decode() == str(True)

    def set_up_logger(self):
        """
            Here used two log level INFO&ERROR.
        """

        self.info = logging.getLogger("INFO")
        self.info.setLevel(logging.INFO)
        self.error = logging.getLogger("ERR")
        self.error.setLevel(logging.ERROR)
        th = logging.StreamHandler(stream=sys.stdout)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(message)s")
        th.setFormatter(formatter)
        self.info.addHandler(th)
        self.error.addHandler(th)

    async def ping_tv(self) -> bool:
        """
            Websocket connection check to TV for remote access and know about state TV ON/OFF.
        """
        try:
            async with websockets.connect(f"ws://{self.config['ip_tv']}:3000", open_timeout=4) as tv:
                return tv.open
        except asyncio.exceptions.TimeoutError:
            return False

    async def send_metrics(self, data: dict):
        """
            Send to zabbix server metrics.
        """
        self.info.info(f"Start send collected data to [{self.server}:{self.port}] ")
        for key, value in data.items():
            subprocess.run(Checker.REQUEST_SEND.format(zabbix=self.server,
                                                       port=self.port,
                                                       host=self.config['host'],
                                                       key=key,
                                                       value=int(value)), **Checker.A_D)

        self.info.info(f"Finish send collected data to [{self.server}:{self.port}] ")

    async def main(self):
        """
            Collect data and send data to zabbix server.
        """
        self.info.info(msg="Start script!")
        while True:
            self.info.info("Start collect data")
            answer = {name: False for name in Checker.CHECK_APP}
            answer['PINGTV'] = await self.ping_tv()
            answer['STATECAMERA'] = self.CameraIsConnected
            answer['STATETV'] = self.TvIsConnected
            answer['STATEAPP'] = self.AppIsOn
            self.info.info(f"Data: {answer}")
            self.info.info("Finish collect data")
            await self.send_metrics(answer)
            await asyncio.sleep(90)


class RemoteTv(SetUp):
    #  TODO Add additional functional
    def __init__(self):
        SetUp.__init__(self)
        self.WebOs = None

    def login(self):
        """
            Auth to tv.
        """
        self.WebOs = WebOSClient(self.config['ip_tv'])
        self.WebOs.connect()
        _ = [_ for _ in self.WebOs.register(self.config)]  # It doesn't matter for us because this simple process auth

    def turn_off(self):
        """
            Turn off tv.
        """
        system_tv = SystemControl(self.WebOs)
        system_tv.power_off()

    def turn_on(self):
        """
            Turn on tv with help magic packet WakeOnLan
        """

        send_magic_packet(self.config['mac_address_tv'],  # First param - MAC TV; Second param - IP_TV/Broadcast
                          ip_address=self.config['broadcast'])

        
def start_and_auth_tv() -> RemoteTv:
    """
        Return object RemoteTv that you can use for remote access.
    """
    ob = RemoteTv()
    ob.turn_on()
    time.sleep(20)
    ob.login()
    return ob

# TODO Create subcommand, example "Checker -host name_host"
choices = ["SetUp", "Checker", "RemoteTv"]
parser = argparse.ArgumentParser(description="3 mode: SetUp Checker RemoteTv")
parser.add_argument("mode", choices=choices)
# parser.add_argument("--option")  # option for future



if __name__ == "__main__":
    namespace = parser.parse_args()
    if namespace.mode == "SetUp":
        ob = SetUp()
        ob.get_ip_tv()
        ob.get_mac_tv()
        ob.get_client_key()
    elif namespace.mode == "Checker":
        start_and_auth_tv()
        checker = Checker()
        asyncio.run(checker.main())
    elif namespace.mode == "RemoteTv":
        ob = start_and_auth_tv()
        ob.turn_off()
        #  TODO add something

