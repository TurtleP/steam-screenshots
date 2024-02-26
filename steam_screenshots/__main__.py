import shutil
import requests
import json

from argparse import ArgumentParser
from pathlib import Path
from datetime import datetime
from pathvalidate import sanitize_filepath

APP_DETAILS = "http://store.steampowered.com/api/appdetails?appids={APP_ID}"
APPS = dict()


def load_app_data() -> dict:
    if not Path("app_data.json").exists():
        return dict()

    with open("app_data.json", "r") as f:
        return json.load(f)


def __main__(args=None):
    parser = ArgumentParser()

    parser.add_argument("dir", help="Steam screenshots directory")

    args = parser.parse_args(args)

    APPS = load_app_data()

    for file in Path(args.dir).glob("*.png"):
        timestamp = datetime.fromtimestamp(file.stat().st_mtime)

        app_id = file.name.split("_")[0]

        if not APPS.get(app_id):
            # find the app name
            response = requests.get(APP_DETAILS.format(APP_ID=app_id))

            if response.status_code != 200:
                print(f"Failed to get app details for {app_id}")
                continue

            data = response.json()

            # store the app name for future use
            app_name = data[app_id]["data"]["name"]
            APPS[app_id] = sanitize_filepath(app_name)

        # create the app directory if it doesn't exist
        (Path(args.dir) / APPS[app_id]).mkdir(exist_ok=True)

        # move the file to the app directory
        filename = f"{timestamp.strftime("%Y-%m-%d_%H-%M-%S")}{file.suffix}"
        shutil.move(str(file), str(Path(args.dir) / APPS[app_id] / filename))

        # save the app data
        with open("app_data.json", "w") as f:
            json.dump(APPS, f)


if __name__ == "__main__":
    __main__()
