import json
import httpx
import base64
import asyncio
import threading
import sys
import time
from playwright.async_api import async_playwright
from flask import Flask, request, json
from client import DolphinClient
from extenv.paths import CAPTCHA_HTML
from extenv.logger import MainLogger

log = MainLogger()


class Utility:
    def __init__(self) -> None:
        pass

    @staticmethod
    def _get_version():

        version = str(
            httpx.get(
                "https://js.hcaptcha.com/1/api.js?reportapi=https%3A%2F%2Fdiscord.com&custom=False"
            )
            .text.split("v1/")[1]
            .split("/")[0]
        )
        log.info(f"Version requested. Version: {version}")
        return version

    def check_site_config(self):
        headers = {
            "accept": "application/json",
            "accept-language": "se-se,se;q=0.7",
            "content-length": "0",
            "content-type": "text/plain",
            "origin": "https://newassets.hcaptcha.com",
            "referer": "https://newassets.hcaptcha.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
            f"Chrome/110.0.0.0 Safari/537.36",
        }
        log.info("Site configuration checked.")
        while True:
            try:
                response = httpx.post(
                    "https://hcaptcha.com/checksiteconfig",
                    params={
                        "v": self._get_version(),
                        "host": "discord.com",
                        "sitekey": "4c672d35-0701-42b2-88c3-78380b0db560",
                        "sc": "1",
                        "swa": "1",
                    },
                    headers=headers,
                    timeout=None,
                )

                return response.json()["c"]["req"]
            except Exception as exe:
                log.error(f"An exception was encountered. Arguments:{str(exe.args)}")
                pass

    @staticmethod
    def _add_padding(base64_string):
        unpadded_length = len(base64_string.rstrip("="))
        padded_length = 4 * ((unpadded_length + 3) // 4)
        padding = "=" * (padded_length - unpadded_length)
        result = base64_string + padding
        log.info(f"Padding has been requested. Padding:{result}")
        return result

    def _get_hcaptcha_version(self):
        site_config = self.check_site_config()
        padding_added = self._add_padding(site_config.split(".")[1])
        decoded = base64.b64decode(padding_added).decode()
        version_json = json.loads(decoded)
        version_url = version_json["l"]
        hcaptcha_version = version_url.split("https://newassets.hcaptcha.com/c/")[1]
        log.info(
            f"H-Captcha version information has been asked. Version: {hcaptcha_version}"
        )
        return hcaptcha_version

    def _ehsw_request(self):
        log.info("EHSW Request has been made to the H-Captcha.")
        return httpx.get(
            f"https://newassets.hcaptcha.com/i/{self._get_hcaptcha_version}/e",
            headers={
                "authority": "newassets.hcaptcha.com",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                "*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "fr-BE,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                "sec-ch-ua": '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/108.0.0.0 Safari/537.36",
            },
            timeout=None,
        )

    def _get_e_hcaptcha_request(self):
        result_e_cap = self._ehsw_request()
        log.info(f"H-Captcha request has been asked: {result_e_cap}")
        return result_e_cap


server = Flask(__name__)


class Worker:
    self = None
    solved = 0
    locked = 0
    lock = threading.Lock()
    loop = asyncio.new_event_loop()
    dolphin = DolphinClient(
        auth_token="YOUR_AUTH_TOKEN_HERE"
    )


class Browser:
    def __init__(self) -> None:
        self.currentBrowser = None
        self.page = None
        self.browser = None
        Worker.self = self

    def start_browser_process(self):
        try:
            self.currentBrowser = Worker.dolphin.create_browser_profile()
            Worker.dolphin.update_browser(self.currentBrowser)
            Worker.lock.acquire()
            Worker.loop.run_until_complete(self._browser_process())
            Worker.loop.run_until_complete(self._goto_discord())
            Worker.loop.run_until_complete(self._setup_iframe())
            Worker.lock.release()
            Worker.dolphin.delete_browser(self.currentBrowser)
            time.sleep(45)
        except Exception as exe:
            log.info(f"Failed to start browser. Arguments:{str(exe.args)}")

    async def _browser_process(self) -> None:
        self._playwright = await async_playwright().start()

        _browser_info_ = Worker.dolphin.start_browser(self.currentBrowser)

        log.warning(
            f"Browser id: {self.currentBrowser} - port: " + str(_browser_info_["port"])
        )

        __temp_browser__ = await self._playwright.chromium.connect_over_cdp(
            f'ws://127.0.0.1:{_browser_info_["port"]}{_browser_info_["wsEndpoint"]}'
        )

        self._browser = __temp_browser__.contexts[0]
        self._page = self._browser.pages[0]

        await self._page.route(
            "https://discord.com/",
            lambda route: route.fulfill(
                status=200,
                body=CAPTCHA_HTML.open("r")
                .read()
                .replace("SITEKEYHERE", "4c672d35-0701-42b2-88c3-78380b0db560"),
            ),
        )

    @server.route("/hsw", methods=["POST"])
    def _get_hsw_request(self):
        content = request.get_json()
        log.info(f"Content Requested in server-route:{content}")
        with Worker.lock:
            hsw = Worker.loop.run_until_complete(
                Worker.self.frame.evaluate("hsw('" + content["req"] + "')")
            )
        log.warning(f"Solved HSW request: {hsw}")
        Worker.solved += 1
        return hsw

    async def _setup_iframe(self) -> None:
        found = False

        iframe1 = await self._page.wait_for_selector(
            "xpath=/html/body/center/h1/div/iframe"
        )
        iframe1 = await iframe1.content_frame()
        button = await iframe1.wait_for_selector(
            "xpath=/html/body/div/div[1]/div[1]/div/div/div[1]"
        )
        example_req = Utility().check_site_config()

        await button.click()

        while not found:
            await self._page.wait_for_timeout(1000)
            for frame in self._page.frames:
                try:
                    await frame.evaluate(f"hsw('{example_req}')")
                    found = True
                    Worker.self.frame = frame
                except Exception as exe:
                    log.error(f"An exception has been encountered: {str(exe.args)}")
        await self._close_old_browser()

        log.critical("Successfully Connected Browser")

    async def _goto_discord(self) -> None:
        await self._page.goto("https://discord.com/", timeout=120000)
        log.info("Current root changed to: https://discord.com/")
        await self._page.wait_for_load_state("domcontentloaded")

    async def _close_old_browser(self) -> None:
        try:
            self.oldB = self.browser
            self.oldPa = self.page
        except Exception as exe:
            log.error(
                f"While closing the old browsers, an exception has been encountered. Arguments: {exe.args}"
            )
            pass

        self.playwright = self._playwright
        self.browser = self._browser
        self.page = self._page

        try:
            await self.oldPa.close()
            await self.oldB.close()
            log.info("Closing browser successful.")
        except Exception as exe:
            log.error(
                f"While closing the old browsers, an exception has been encountered. Arguments: {exe.args}"
            )
            pass


threading.Thread(
    target=lambda: server.run(
        host="0.0.0.0",
        port=int(sys.argv[1]),
        debug=False,
        use_reloader=False,
        threaded=True,
    )
).start()
browser_client = Browser()
try:
    browser_client.start_browser_process()
except Exception as e:
    log.error(
        f"While starting a browser, an exception has been encountered: {str(e.args)}"
    )
    browser_client.start_browser_process()
