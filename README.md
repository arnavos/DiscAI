# Discord Token Generator (AI)
![Discord](https://thebrandhopper.com/wp-content/uploads/2023/07/discord.jpg)
Works with Python 3.12x.
Generated under a virtual environment:
```python
> python --version
Python 3.12.2
```
### On Windows:
```cmd
git clone https://www.github.com/arnavos/Generator.git
cd Generator
python -m venv env
./env/Scripts/Activate.ps1
pip install -r requirements.txt
python index.py
```
After installing the module and before running it, you'd need an auth token along with a specific browser.
#### **Dolphin Anty Browser Auth Token**
![Basic](https://techzeel.net/wp-content/uploads/2024/01/dolphin-anty-browser.webp)

Follow these steps to get an auth token from Dolphin Anty browser:

1. Generate an API access token. Go to the Dolphin Anty panel.
2. Fill in the name, select expiration days, and click the button to create a token.
3. A popup will open where you can copy the token. Make sure you save your token, as you won't be able to see it again.
4. You should provide this access token in each request in the Authorization -> Bearer Token.

[Download Dolphin Anty Browser](https://dolphin-anty.com/en/download/)

Finally, Add your authentication credentials in: `./srv/reload.py` on `line 130` here:
```python
class Worker:
    self = None
    solved = 0
    locked = 0
    lock = threading.Lock()
    loop = asyncio.new_event_loop()
    dolphin = DolphinClient(
        auth_token="YOUR_AUTH_TOKEN_HERE"
    )
```

To run the server, use `start-server.py`.

To run the solver, use `index.py`
#### Follow up the `issues` and `project` for further updates if any.
### End
