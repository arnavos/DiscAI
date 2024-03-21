import threading
import os
from extenv.paths import SERVER_RELOAD


def start(port):
    os.system(f"python {SERVER_RELOAD} {port}")


for i in ["1337"]:
    threading.Thread(target=start, args=[i]).start()
