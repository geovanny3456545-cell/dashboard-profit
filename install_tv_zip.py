import requests
import zipfile
import io
import os
import subprocess
import sys

def install_tvdatafeed_from_zip():
    url = "https://github.com/rongardF/tvdatafeed/archive/refs/heads/main.zip"
    print(f"Downloading {url}...")
    try:
        r = requests.get(url)
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            z.extractall("/tmp/tvdatafeed_src")
        
        src_path = "/tmp/tvdatafeed_src/tvdatafeed-main"
        print(f"Installing from {src_path}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", src_path])
        print("Success!")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    install_tvdatafeed_from_zip()
