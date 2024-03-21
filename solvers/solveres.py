import tls_client
import json
import requests
import time
import random
import base64
import numpy
import httpx
import re
from typing import Optional
from datetime import datetime
from .hcap import __config__, NewChallenge
from extenv.logger import MainLogger
from colorama import Fore
from extenv.paths import CONFIG

log = MainLogger()

hcaptchaApiVersion = (
    requests.get(
        "https://hcaptcha.com/1/api.js?render=explicit&onload=hcaptchaOnLoad",
        headers={
            "authority": "newassets.hcaptcha.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "fr-BE,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "sec-ch-ua": '"Google Chrome";v="117", "Not(A:Brand";v="8", "Chromium";v="117"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        },
    )
    .text.split('assetUrl:"https://newassets.hcaptcha.com/captcha/v1/')[1]
    .split("/")[0]
)

config = json.loads(CONFIG.open("r").read())


class Solver:
    def __init__(
        self,
        session: tls_client.Session,
        site_key: Optional[str],
        site_url: Optional[str],
        rq_data: Optional[str] = None,
    ) -> None:
        self.proofData = None
        self.solution = None
        self.tasklist = None
        self.captchaKey = None
        self.questionx = None
        self.question = None
        self.prediction = None
        self.hsw = None
        self.captcha = None
        self.debug = False
        self.session = session
        self.oldHeaders = self.session.headers
        self.session.headers = {
            "authority": "hcaptcha.com",
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "text/plain",
            "origin": "https://newassets.hcaptcha.com",
            "referer": "https://newassets.hcaptcha.com/",
            "sec-ch-ua": '"Chromium";v="117", "Google Chrome";v="117", "Not:A-Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        }

        self.siteKey = site_key
        self.siteUrl = site_url

        self.log(f"Solving Captcha, SiteKey: {self.siteKey} | SiteUrl: {self.siteUrl}")
        self.log(f"Hcaptcha Api Version: {hcaptchaApiVersion}")

        self.hsw: str
        self.captchaKey: str
        self.question: str

        self.proofData: dict
        self.tasklist: dict
        self.solution: dict
        self.rqData: str = rq_data
        self.sed = False

    def log(self, txt: str) -> None:
        if self.debug:
            print(txt)

    def get_hsw(self) -> str:
        if self.sed:
            return requests.post(
                f"http://127.0.0.1:{random.choice(['1337'])}/hsw",
                json={"req": self.proofData["req"]},
            ).text
        else:
            self.sed = True
            return requests.post(
                f"http://127.0.0.1:{random.choice(['1337'])}/hsw",
                json={"req": self.proofData["req"]},
            ).text

    @staticmethod
    def mouse_movement(size: int = 50):
        x_movements = numpy.random.randint(15, 450, size=size)
        y_movements = numpy.random.randint(15, 450, size=size)
        times = numpy.round(time.time(), decimals=0)
        times_list = [times] * len(x_movements)
        movement = numpy.column_stack((x_movements, y_movements, times_list))
        return movement.tolist()

    def check_site_config(self) -> dict:
        return self.session.post(
            "https://hcaptcha.com/checksiteconfig",
            params={
                "v": hcaptchaApiVersion,
                "host": self.siteUrl,
                "sitekey": self.siteKey,
                "sc": "1",
                "swa": "1",
            },
        ).json()

    def get_captcha(self) -> dict:
        self.session.headers["content-type"] = "application/x-www-form-urlencoded"
        payload = {
            "v": hcaptchaApiVersion,
            "sitekey": self.siteKey,
            "host": self.siteUrl,
            "hl": "en",
            "motionData": '{"st":1683111091801,"mm":mmdata,"mm-mp":11.272727272727273,"md":[[21,36,1683111092835]],"md-mp":0,"mu":[[21,36,1683111092922]],"mu-mp":0,"v":1,"topLevel":{"st":1683111091490,"sc":{"availWidth":1440,"availHeight":786,"width":1440,"height":900,"colorDepth":30,"pixelDepth":30,"availLeft":0,"availTop":0,"onchange":null,"isExtended":true},"nv":{"vendorSub":"","productSub":"20030107","vendor":"Google Inc.","maxTouchPoints":0,"scheduling":{},"userActivation":{},"doNotTrack":null,"geolocation":{},"connection":{},"pdfViewerEnabled":true,"webkitTemporaryStorage":{},"hardwareConcurrency":4,"cookieEnabled":true,"appCodeName":"Mozilla","appName":"Netscape","appVersion":"5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36","platform":"MacIntel","product":"Gecko","userAgent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36","language":"en-US","languages":["en-US","en"],"onLine":true,"webdriver":false,"bluetooth":{},"clipboard":{},"credentials":{},"keyboard":{},"managed":{},"mediaDevices":{},"storage":{},"serviceWorker":{},"virtualKeyboard":{},"wakeLock":{},"deviceMemory":8,"ink":{},"hid":{},"locks":{},"mediaCapabilities":{},"mediaSession":{},"permissions":{},"presentation":{},"serial":{},"usb":{},"windowControlsOverlay":{},"xr":{},"userAgentData":{"brands":[{"brand":"Chromium","version":"112"},{"brand":"Google Chrome","version":"112"},{"brand":"Not:A-Brand","version":"99"}],"mobile":false,"platform":"macOS"},"plugins":["internal-pdf-viewer","internal-pdf-viewer","internal-pdf-viewer","internal-pdf-viewer","internal-pdf-viewer"]},"dr":"","inv":false,"exec":false,"wn":[[867,782,2,1683111091491]],"wn-mp":0,"xy":[[0,0,1,1683111091491]],"xy-mp":0,"mm":[[846,608,1683111092417],[731,602,1683111092434],[563,600,1683111092457],[471,598,1683111092473],[389,585,1683111092490],[273,553,1683111092513],[213,534,1683111092529]],"mm-mp":7.5625},"session":[],"widgetList":["0qlt5b9onyt"],"widgetId":"0qlt5b9onyt","href":"https://discord.com/","prev":{"escaped":false,"passed":false,"expiredChallenge":false,"expiredResponse":false}}'.replace(
                "16831110", str(round(datetime.now().timestamp()))[:8]
            ).replace(
                "mmdata", str(self.mouse_movement())
            ),
            "pdc": json.dumps(
                {
                    "s": int(time.time() * 1000),
                    "n": 0,
                    "p": 1,
                    "gcs": random.randint(100, 300),
                }
            ),
            "n": self.hsw,
            "c": json.dumps(self.proofData),
            "pst": False,
        }
        if self.rqData is not None:
            payload["rqdata"] = self.rqData
        resp = self.session.post(
            f"https://hcaptcha.com/getcaptcha/{self.siteKey}", data=payload
        ).json()

        return resp

    def solve(self) -> dict:
        if self.captcha["request_type"] == "image_label_binary":

            if self.questionx not in __config__["all_prompts"]:
                imgb64 = {
                    str(i): base64.b64encode(
                        requests.get(
                            str(img["datapoint_uri"]), headers=self.session.headers
                        ).content
                    ).decode("utf-8")
                    for i, img in enumerate(self.tasklist)
                }

                task = requests.post(
                    "https://pro.nocaptchaai.com/solve",
                    headers={
                        "Content-type": "application/json",
                        "apikey": config["no-captcha-ai-key"],
                    },
                    json={
                        "images": imgb64,
                        "target": self.question,
                        "method": "hcaptcha_base64",
                        "sitekey": self.siteKey,
                        "site": self.siteUrl,
                    },
                )
                self.prediction = task.json()["solution"]
            else:
                images = []
                for i in self.tasklist:
                    images.append(httpx.get(i["datapoint_uri"]).content)

                challenger = NewChallenge()
                self.prediction = challenger.classify(
                    prompt=self.questionx, images=images
                )

            log.info(
                f"Answers found {Fore.LIGHTBLUE_EX}|{Fore.RESET} {self.questionx.upper()} {Fore.LIGHTBLUE_EX}{self.prediction}{Fore.RESET}"
            )
            resp = [i in self.prediction for i in range(len(self.tasklist))]
            return {
                task["task_key"]: str(resp).lower()
                for task, resp in zip(self.tasklist, resp)
            }
        elif self.captcha["request_type"] == "image_label_area_select":
            entity_type = list(self.captcha["requester_restricted_answer_set"])[0]

            imgb64 = {
                str(i): base64.b64encode(
                    requests.get(
                        str(img["datapoint_uri"]), headers=self.session.headers
                    ).content
                ).decode("utf-8")
                for i, img in enumerate(self.tasklist)
            }

            task = requests.post(
                "https://pro.nocaptchaai.com/solve",
                headers={
                    "Content-type": "application/json",
                    "apikey": config["no-captcha-ai-key"],
                },
                json={
                    "images": imgb64,
                    "target": self.question,
                    "type": "bbox",
                    "method": "hcaptcha_base64",
                    "sitekey": self.siteKey,
                    "site": self.siteUrl,
                },
            )

            self.prediction = task.json()["answers"]

            log.info(
                f"Answers found {Fore.LIGHTBLUE_EX}|{Fore.RESET} BBOX {Fore.LIGHTBLUE_EX}{self.prediction}{Fore.RESET}"
            )
            result = {}
            for i in range(len(self.tasklist)):
                k = self.tasklist[i]["task_key"]
                c = {
                    "entity_name": 0,
                    "entity_type": entity_type,
                    "entity_coords": self.prediction[i],
                }
                result[k] = result.get(k, []) + [c]

            return result
        elif self.captcha["request_type"] == "image_label_multiple_choice":
            imgb64 = {
                str(i): base64.b64encode(
                    requests.get(
                        str(img["datapoint_uri"]), headers=self.session.headers
                    ).content
                ).decode("utf-8")
                for i, img in enumerate(self.tasklist)
            }

            task = requests.post(
                "https://pro.nocaptchaai.com/solve",
                headers={
                    "Content-type": "application/json",
                    "apikey": config["no-captcha-ai-key"],
                },
                json={
                    "images": imgb64,
                    "target": self.question,
                    "type": "multi",
                    "method": "hcaptcha_base64",
                    "sitekey": self.siteKey,
                    "site": self.siteUrl,
                },
            )
            self.prediction = task.json()["answers"]

        else:
            print("Invalid Captcha Type :fire:")
            print(self.captcha)

    def post_captcha(self) -> dict:
        self.session.headers.update(
            {"accept": "*/*", "content-type": "application/json;charset=UTF-8"}
        )

        return self.session.post(
            f"https://hcaptcha.com/checkcaptcha/{self.siteKey}/{self.captchaKey}",
            json={
                "v": hcaptchaApiVersion,
                "job_mode": self.captcha["request_type"],
                "answers": self.solution,
                "serverdomain": self.siteUrl,
                "sitekey": self.siteKey,
                "motionData": '{"st":1683111093679,"dct":1683111093679,"mm":mmdata,"mm-mp":15.702205882352935,"md":md_data__,"md-mp":831.75,"mu":[[69,192,1683111095062],[84,190,1683111095835],[175,329,1683111096395],[88,469,1683111096710],[362,573,1683111098388]],"mu-mp":831.5,"topLevel":{"st":1683111091490,"sc":{"availWidth":1440,"availHeight":786,"width":1440,"height":900,"colorDepth":30,"pixelDepth":30,"availLeft":0,"availTop":0,"onchange":null,"isExtended":true},"nv":{"vendorSub":"","productSub":"20030107","vendor":"Google Inc.","maxTouchPoints":0,"scheduling":{},"userActivation":{},"doNotTrack":null,"geolocation":{},"connection":{},"pdfViewerEnabled":true,"webkitTemporaryStorage":{},"hardwareConcurrency":4,"cookieEnabled":true,"appCodeName":"Mozilla","appName":"Netscape","appVersion":"5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36","platform":"MacIntel","product":"Gecko","userAgent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36","language":"en-US","languages":["en-US","en"],"onLine":true,"webdriver":false,"bluetooth":{},"clipboard":{},"credentials":{},"keyboard":{},"managed":{},"mediaDevices":{},"storage":{},"serviceWorker":{},"virtualKeyboard":{},"wakeLock":{},"deviceMemory":8,"ink":{},"hid":{},"locks":{},"mediaCapabilities":{},"mediaSession":{},"permissions":{},"presentation":{},"serial":{},"usb":{},"windowControlsOverlay":{},"xr":{},"userAgentData":{"brands":[{"brand":"Chromium","version":"112"},{"brand":"Google Chrome","version":"112"},{"brand":"Not:A-Brand","version":"99"}],"mobile":false,"platform":"macOS"},"plugins":["internal-pdf-viewer","internal-pdf-viewer","internal-pdf-viewer","internal-pdf-viewer","internal-pdf-viewer"]},"dr":"","inv":false,"exec":false,"wn":[[867,782,2,1683111091491]],"wn-mp":0,"xy":[[0,0,1,1683111091491]],"xy-mp":0,"mm":[[846,608,1683111092417],[731,602,1683111092434],[563,600,1683111092457],[471,598,1683111092473],[389,585,1683111092490],[273,553,1683111092513],[213,534,1683111092529],[60,489,1683111094195],[63,487,1683111094217],[68,486,1683111094234],[77,484,1683111094250],[96,482,1683111094274],[499,743,1683111097561],[512,752,1683111097577],[516,755,1683111097594],[516,756,1683111097634],[515,756,1683111097681],[511,752,1683111097697],[506,748,1683111097713],[503,745,1683111097729],[502,744,1683111097761],[501,744,1683111097801],[499,745,1683111097818],[496,749,1683111097841]],"mm-mp":112.99999999999996},"v":1}'.replace(
                    "1683111", str(round(datetime.now().timestamp()))[:7]
                )
                .replace("mmdata", str(self.mouse_movement()))
                .replace("md_data__", str(self.mouse_movement(size=5))),
                "n": self.hsw,
                "c": json.dumps(self.proofData),
            },
        ).json()

    @staticmethod
    def label_c(lab: str):
        if "containing" in lab:
            th = re.split(r"containing", lab)[-1][1:].strip()
            lab = th[2:].strip() if th.startswith("a") else th
        if "select all" in lab:
            lab = re.split(r"all (.*) images", lab)[1].strip()
        if "with" in lab:
            th = re.split(r"with", lab)[-1][1:].strip()
            lab = th
        return lab

    def solve_captcha(self) -> Optional[str]:
        self.proofData = self.check_site_config()
        if not self.proofData["pass"]:
            self.log("Failed Check Site Config")
            return None
        self.proofData = self.proofData["c"]
        self.log("Passed Check Site Config")

        time_started = time.time()

        self.hsw = self.get_hsw()
        self.captcha = self.get_captcha()
        if "generated_pass_UUID" in self.captcha:
            self.session.headers = self.oldHeaders
            self.log(f'Solved Captcha: {self.captcha["generated_pass_UUID"][:20]}')
            return self.captcha["generated_pass_UUID"]
        if "key" not in self.captcha:
            self.log(f"Failed Captcha: {self.captcha}")
            self.session.headers = self.oldHeaders
            return None
        self.question = self.captcha["requester_question"]["en"]
        self.questionx = self.label_c(self.question)
        self.captchaKey = self.captcha["key"]
        self.tasklist = self.captcha["tasklist"]
        self.proofData = self.captcha["c"]

        self.log(f"Solving: {self.question}")
        self.solution = self.solve()
        self.log(f"Solved: {self.prediction}")

        self.hsw = self.get_hsw()

        elapsed_time = time.time() - time_started
        self.log(f"Got Solution In {elapsed_time}s")
        if elapsed_time < 5:
            time_to_sleep = 5 - elapsed_time + random.uniform(0, 0.5)
            self.log(f"Waiting {round(time_to_sleep, 2)}s to not be under 5s")
            time.sleep(time_to_sleep)

        self.captchaKey = self.post_captcha()
        if "generated_pass_UUID" in self.captchaKey:
            self.session.headers = self.oldHeaders
            self.log(f'Solved Captcha: {self.captchaKey["generated_pass_UUID"][:20]}')
            return self.captchaKey["generated_pass_UUID"]
        self.session.headers = self.oldHeaders
        self.log(f"Failed Captcha: {self.captchaKey}")
        return None


if __name__ == "main":
    while True:
        started = time.time()
        # noinspection PyTypeChecker
        solver = Solver(
            session=tls_client.Session(
                client_identifier="chrome119", random_tls_extension_order=True
            ),
            site_key="4c672d35-0701-42b2-88c3-78380b0db560",
            site_url="discord.com",
        )
        response = solver.solve_captcha()
        print(response)
        print(f"Solved In {round(time.time() - started, 3)}s")
