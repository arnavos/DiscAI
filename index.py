import logging

import tls_client
import base64
import json
import time
import random
import websocket
import datetime
import os
import threading
from colorama import Fore
from solvers.solveres import Solver
from extenv.logger import MainLogger
from extenv.paths import CONFIG, RESULT_FOLDER, PROXYLIST, USERNAMES

log = MainLogger()

names = USERNAMES.open("r", encoding="utf-8").read().splitlines()
proxies = PROXYLIST.open("r", encoding="utf-8").read().splitlines()
config = json.loads(CONFIG.open("r").read())

locked = 0
unlocked = 0
total = 0


def update_title():
    global total, locked, unlocked
    gen_started_as = time.time()
    while True:
        try:
            delta = datetime.timedelta(seconds=round(time.time() - gen_started_as))
            result = ""
            if delta.days > 0:
                result += f"{delta.days}d "
            if delta.seconds // 3600 > 0:
                result += f"{delta.seconds // 3600}h "
            if delta.seconds // 60 % 60 > 0:
                result += f"{delta.seconds // 60 % 60}m "
            if delta.seconds % 60 > 0 or result == "":
                result += f"{delta.seconds % 60}s"
        except Exception as exe:
            log.error(
                f"An exception has been encountered while Updating title. {str(exe.args)}"
            )
            pass
        time.sleep(1)


class Discord:
    def __init__(self) -> None:
        self.fingerprint = None
        self.token = None
        # noinspection PyTypeChecker
        self.session = tls_client.Session(
            client_identifier="chrome118", random_tls_extension_order=True
        )

        self.session.headers = {
            "Host": "discord.com",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
            "Accept": "/",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/json",
            "X-Discord-Locale": "en-US",
            "X-Debug-Options": "bugReporterEnabled",
            "Origin": "https://discord.com/",
            "Alt-Used": "discord.com",
            "Connection": "keep-alive",
            "Referer": "https://discord.com/register",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "dnt": "1",
            "TE": "trailers",
            "X-Track": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKExpbnV4OyBBbmRyb2lkIDYuMDsgTmV4dXMgNSBCdWlsZC9NUkE1OE4pIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS8xMjEuMC4wLjAgTW9iaWxlIFNhZmFyaS81MzcuMzYiLCJicm93c2VyX3ZlcnNpb24iOiIxMjEuMC4wLjAiLCJvc192ZXJzaW9uIjoiNi4wIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6Imh0dHBzOi8vZGlzY29yZC5jb20vIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiZGlzY29yZC5jb20iLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjo5OTk5LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==",
        }

        self.prop = {
            "os": "Windows",
            "browser": "Chrome",
            "device": "",
            "system_locale": "fr-FR",
            "browser_user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "browser_version": "118.0.0",
            "os_version": "10",
            "referrer": "",
            "referring_domain": "",
            "referrer_current": "",
            "referring_domain_current": "",
            "release_channel": "stable",
            "client_event_source": None,
            "design_id": 0,
        }
        self.super = base64.b64encode(
            json.dumps(self.prop, separators=(",", ":")).encode()
        ).decode()

        self.proxy = "http://" + random.choice(proxies).replace(
            "sessionid", str(random.randint(1327390889, 1399999999))
        )
        self.session.proxies = {"http": self.proxy, "https": self.proxy}

    def get_finger_print(self) -> str:
        return self.session.get("https://discord.com/api/v9/experiments").json()[
            "fingerprint"
        ]

    def create_account(self, captcha_key, invite_link) -> str:
        payload = {
            "consent": True,
            "captcha_key": captcha_key,
            "fingerprint": self.fingerprint,
            "username": random.choice(names),
        }
        if invite_link != "" or invite_link != "":
            payload["invite"] = invite_link
        response = self.session.post(
            "https://discord.com/api/v9/auth/register", json=payload
        ).json()
        if "token" in response:
            return response["token"]
        elif "retry_after" in response:
            # time.sleep(response["retry_after"])
            raise Exception(f'Rate Limited For {response["retry_after"]}s')
        else:
            raise Exception(str(response))

    def is_locked(self) -> bool:
        return (
            "You need to verify your account in order to perform this action."
            in self.session.get(
                "https://discord.com/api/v9/users/@me/affinities/users",
            ).text
        )

    def generate(self, invite_code) -> None:
        global total, locked, unlocked
        self.fingerprint = self.get_finger_print()
        print("FINGERPRINT:", self.fingerprint)
        self.session.headers.update(
            {"origin": "https://discord.com", "x-fingerprint": self.fingerprint}
        )

        started_solving = time.time()
        captcha_key = None
        while captcha_key is None:
            solver = Solver(
                session=self.session,
                site_key="4c672d35-0701-42b2-88c3-78380b0db560",
                site_url="discord.com",
            )
            captcha_key = solver.solve_captcha()
        log.info(
            f"{Fore.LIGHTBLACK_EX}[SOLVED..] -> {Fore.LIGHTWHITE_EX}{captcha_key[:42]} | {round(time.time() - started_solving)}sec"
        )

        self.token = self.create_account(captcha_key, invite_code)

        self.session.headers.update(
            {
                "authorization": self.token,
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "referer": "https://discord.com/channels/@me",
                "x-debug-options": "bugReporterEnabled",
                "x-discord-locale": "fr",
                "x-track": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKExpbnV4OyBBbmRyb2lkIDYuMDsgTmV4dXMgNSBCdWlsZC9NUkE1OE4pIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS8xMjEuMC4wLjAgTW9iaWxlIFNhZmFyaS81MzcuMzYiLCJicm93c2VyX3ZlcnNpb24iOiIxMjEuMC4wLjAiLCJvc192ZXJzaW9uIjoiNi4wIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6Imh0dHBzOi8vZGlzY29yZC5jb20vIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiZGlzY29yZC5jb20iLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjo5OTk5LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==",
            }
        )
        # self.session.headers.pop("x-track")
        self.session.headers.pop("origin")

        self.session.proxies = {"http": None, "https": None}

        # noinspection PyArgumentList
        ws = websocket.WebSocket()
        ws.connect("wss://gateway.discord.gg/?v=9")
        ws.send(
            json.dumps(
                {
                    "op": 2,
                    "d": {
                        "token": self.token,
                        "capabilities": 4093,
                        "properties": self.prop,
                        "presence": {
                            "status": "online",
                            "since": 0,
                            "activities": [],
                            "afk": False,
                        },
                        "compress": False,
                        "client_state": {
                            "guild_versions": {},
                            "highest_last_message_id": "0",
                            "read_state_version": 0,
                            "user_guild_settings_version": -1,
                            "user_settings_version": -1,
                            "private_channels_version": "0",
                            "api_code_version": 0,
                        },
                    },
                }
            )
        )
        ws.send(
            json.dumps(
                {
                    "op": 4,
                    "d": {
                        "guild_id": None,
                        "channel_id": None,
                        "self_mute": True,
                        "self_deaf": False,
                        "self_video": False,
                    },
                }
            )
        )

        unlocked += 1
        path_new_token = os.path.join(RESULT_FOLDER, invite)
        open(path_new_token, "a").write(f"{self.token}\n")
        log.info(
            f"{Fore.LIGHTGREEN_EX}[TOKEN.] -> {Fore.LIGHTWHITE_EX}{self.token[:32]}..."
        )
        ws.close()


def generate(invite_code):
    global total, locked, unlocked
    while True:
        try:
            discord = Discord()
            discord.generate(invite_code)
        except Exception as e:
            log.error(
                f"While operating on the generative hyper purge, an exception has occurred. Exception: {str(e)}"
            )
            pass


if __name__ == "__main__":
    os.system("cls")
    threads = input("Threads->")
    invite = input("Invite-Code->")
    if invite == "":
        invite = None
    for i in range(int(threads)):
        threading.Thread(target=generate, args=[invite]).start()
    threading.Thread(target=update_title).start()
