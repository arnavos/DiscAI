import string
import random
import requests
import tls_client
from extenv.logger import MainLogger


log = MainLogger()


class DolphinClient:
    """
    A class with methods to interact with a browser automation API,
    including starting, creating, updating, and deleting browser profiles.

    :param auth_token: The `auth_token` parameter is a string that represents the authentication token
    required for accessing the API endpoints. This token is used to authenticate and authorize the user
    to perform various actions like creating, updating, or deleting browser profiles. It is passed to
    the class constructor during initialization to establish a valid session with
    :type auth_token: str
    """

    BASE_URL = "https://api.dolphin-anty-ru.online/"

    def __init__(self, auth_token: str) -> None:
        self.token = auth_token
        self.resolutions = [
            "1280x720",
            "1280x800",
            "1280x1024",
            "1366x768",
            "1440x900",
            "1536x864",
            "1600x900",
        ]
        self.session = tls_client.Session(
            client_identifier="chrome_117", random_tls_extension_order=True
        )
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.token,
            }
        )
        pass

    def start_browser(self, profile_id: str):
        """
        This function starts a browser with a specified profile ID for automation purposes.

        :param profile_id: The `profile_id` parameter is a string that represents the unique identifier of a
        browser profile. It is used to specify which browser profile should be started for automation
        :type profile_id: str
        :return: The code snippet is making a GET request to start a browser with a specific profile ID and
        automation parameter set to 1. It then returns the value of the "automation" key from the JSON
        response.
        """
        log.info("Browser starting triggered.")
        resp = self.session.get(
            f"http://localhost:3001/v1.0/browser_profiles/{profile_id}/start?automation=1"
        ).json()
        return resp["automation"]

    def _get_fingerprint(self):
        """
        This function sends a request to retrieve fingerprints with specific parameters from a given URL.
        :return: The `_get_fingerprint` method returns a JSON response from a GET request to a specific URL
        with the provided parameters. The parameters include platform, browser type, browser version, type,
        and screen resolution.
        """
        log.info("Fingerprints asked.")
        params = {
            "platform": "windows",
            "browser_type": "anty",
            "browser_version": "117",
            "type": "fingerprint",
            "screen": "1600x900",
        }
        return self.session.get(
            f"{self.BASE_URL}/fingerprints/fingerprint", params=params
        ).json()

    def create_browser_profile(self):
        """
        The `_create_browser_profile` function generates a browser profile with specific characteristics and
        returns the generated browser profile ID.
        :return: The function `_create_browser_profile` is returning the "browserProfileId" from the JSON
        response obtained after making a POST request to the specified URL with the given payload data.
        """
        log.info("Browser Profile has been created.")
        browser_version = random.randint(100, 118)
        payload = {
            "name": "Discord",
            "useragent[mode]": "manual",
            "mainWebsite": "google",
            "useragent[value]": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/{browser_version}.0.0.0 Safari/537.36",
            "platform": "windows",
            "webrtc[mode]": "altered",
            "canvas[mode]": "noise",
            "webgl[mode]": "noise",
            "locale[mode]": "auto",
            "cpu[mode]": "noise",
            "memory[mode]": "noise",
            "browserType": "anty",
            "webglInfo[mode]": "noise",
            "geolocation[mode]": "auto",
            "doNotTrack": 1,
        }

        response = self.session.post(
            f"{self.BASE_URL}/browser_profiles", json=payload
        ).json()
        return response["browserProfileId"]

    def update_browser(self, profile_id: str):
        """
        The `_update_browser` function generates random browser profile data and sends a PATCH request to
        update the browser profile with the specified `profile_id`.

        :param profile_id: The `profile_id` parameter in the `_update_browser` method is used to identify
        the specific browser profile that needs to be updated with the new information provided in the
        `payload` dictionary. This ID is used to make a PATCH request to the API endpoint for updating the
        browser profile with the new data
        :type profile_id: str
        """
        log.info("Browser Update has been called and triggered.")
        browser_version = random.randint(100, 118)
        fingerprint = self._get_fingerprint()

        payload = {
            "name": "".join(random.choice(string.ascii_letters) for _ in range(10)),
            "tags": [],
            "browserType": "anty",
            "mainWebsite": "google",
            "useragent": {
                "mode": "manual",
                "value": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                f" Chrome/{browser_version}.0.0.0 Safari/537.36",
            },
            "webrtc": {
                "mode": "altered",
                "ipAddress": None,
            },
            "canvas": {
                "mode": "noise",
            },
            "webgl": {
                "mode": "noise",
            },
            "webglInfo": {
                "mode": "manual",
                "vendor": fingerprint["webgl"]["unmaskedVendor"],
                "renderer": fingerprint["webgl"]["unmaskedRenderer"],
                "webgl2Maximum": fingerprint["webgl2Maximum"],
            },
            "clientRect": {
                "mode": "noise",
            },
            "notes": {
                "content": "null",
                "color": "blue",
                "style": "text",
                "icon": "null",
            },
            "timezone": {
                "mode": "auto",
                "value": None,
            },
            "locale": {
                "mode": "auto",
                "value": None,
            },
            "proxy": None,  # http://thunderimwvzdrv36R-res-ANY:getohjahvalq83B@gw.thunderproxies.net:5959
            "statusId": 0,
            "geolocation": {
                "mode": "auto",
                "latitude": None,
                "longitude": None,
                "accuracy": None,
            },
            "cpu": {
                "mode": "manual",
                "value": random.choice(["2", "4", "6", "8", "10", "12", "16"]),
            },
            "memory": {
                "mode": "manual",
                "value": random.choice(["4", "8"]),
            },
            "screen": {"mode": "real", "resolution": random.choice(self.resolutions)},
            "audio": {
                "mode": "real",
            },
            "mediaDevices": {
                "mode": "manual",
                "audioInputs": random.randint(1, 3),
                "videoInputs": random.randint(1, 3),
                "audioOutputs": random.randint(1, 3),
            },
            "ports": {"mode": "protect", "blacklist": "3389,5900,5800,7070,6568,5938"},
            "doNotTrack": True,
            "args": [],
            "platformVersion": "10.0.0",
            "uaFullVersion": f"{browser_version}.0.5615.49",
            "login": "",
            "password": "",
            "appCodeName": "Mozilla",
            "platformName": "MacIntel",
            "connectionDownlink": 10,
            "connectionEffectiveType": "4g",
            "connectionRtt": 100,
            "connectionSaveData": 0,
            "cpuArchitecture": "amd64",
            "osVersion": "10",
            "vendorSub": "",
            "productSub": "20030107",
            "vendor": "Google Inc.",
            "product": "Gecko",
        }

        self.session.patch(
            f"{self.BASE_URL}/browser_profiles/{profile_id}",
            json=payload,
        )

    def delete_browser(self, profile_id: str):
        """
        The `_delete_browser` function deletes a browser profile using a DELETE request with error handling
        for different status codes.

        :param profile_id: The `profile_id` parameter in the `_delete_browser` method is a string that
        represents the unique identifier of the browser profile that you want to delete. This method sends a
        DELETE request to the specified URL to delete the browser profile associated with the provided
        `profile_id`
        :type profile_id: str
        """
        log.info(f"Deleting the browser profile {profile_id}")
        url = f"{self.BASE_URL}/browser_profiles/{profile_id}?forceDelete=1"

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.token,
            }

            response = requests.delete(url, headers=headers)

            if response.status_code == 204:
                log.info(f"Successfully deleted browser profile with ID {profile_id}")
            elif response.status_code == 200:
                log.info(f"Received a 200 status code. Response body: {response.text}")
            elif response.status_code == 404:
                log.warning(
                    f"Browser profile with ID {profile_id} not found. It may have already been deleted."
                )
            elif response.status_code == 403:
                log.error(
                    f"Access Denied. You don't have permission to delete the profile with ID {profile_id}."
                )
            else:
                log.error(
                    f"Failed to delete browser profile with ID {profile_id}. Status code: {response.status_code}"
                )
        except requests.exceptions.RequestException as e:
            log.error(f"An error occurred while sending the delete request: {e}")
