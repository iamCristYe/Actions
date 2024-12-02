import requests

import json
import time
import os
from telegram import Bot
import subprocess
from github import Github
from github import Auth


# 发送压缩文件到Telegram
async def send_file_to_telegram():
    with open("line.json") as f:
        data = json.load(f)
        start = int(data["last"] / 1000) * 1000 - 1
    telegram_token = os.environ["bot_token"]  # 替换为你的Telegram bot token
    telegram_chat_id = os.environ["chat_id"]  # 替换为你的频道或群组ID
    bot = Bot(token=telegram_token)
    archive_path = os.path.join(".", f"line-{start}.txt")
    await bot.send_document(chat_id=telegram_chat_id, document=open(archive_path, "rb"))


def send_telegram_message(token, channel_id, message):
    while True:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": channel_id,  # Channel ID with "@" (e.g., "@your_channel_id")
                "text": message,
            }
            response = requests.post(url, data=payload)
            time.sleep(30)
            return response.json()
        except:
            time.sleep(30)


async def main():
    data = {}
    need_update = False
    with open("line.json") as f:
        data = json.load(f)
        if data["running"]:
            return
        start = int(data["last"] / 1000) * 1000 - 1
        data["running"] = True
        with open("line.json", "w") as f:
            json.dump(data, f)

        # using an access token
        auth = Auth.Token(os.environ["github_token"])

        # First create a Github instance:
        # Public Web Github
        g = Github(auth=auth)

        # Then play with your Github objects:
        repo = g.get_user().get_repo("cron")
        contents = repo.get_contents("line.json")

        with open("line.json", "r") as f:
            repo.update_file("line.json", f"line s {start}", f.read(), contents.sha)

        # To close connections after use
        g.close()

    for code in range(start, start + 5005, 1):
        # Define the URL of the image
        # https://music.line.me/webapp/new-songs
        url = f"https://music.line.me/api2/tracks/mt0000000020{hex(code).split('x')[-1]}.v1"
        # https://i.kfs.io/artist/global/407071,0v36/fit/500x500.jpg
        print(code, url)
        # Send a GET request to the URL

        # Retry mechanism in case of connection issues
        while True:
            try:
                response = requests.get(url)

                time.sleep(1)
                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    if len(response.content):
                        print(response.content.decode("utf-8"))
                        result = json.loads(response.content.decode("utf-8"))
                        print(result)
                        if "response" not in result:
                            with open(f"line-{start}.txt", "a") as f:
                                f.write(url + "\n")
                                print(url)
                                break
                        if result["response"]["result"]["trackTotalCount"] == 0:
                            with open(f"line-{start}.txt", "a") as f:
                                f.write(url + " trackTotalCount 0" "\n")
                                print(url)
                                break
                        artistName = result["response"]["result"]["tracks"][0][
                            "artists"
                        ][0]["artistName"]
                        need_update = True

                        print(artistName)
                        with open(f"line-{start}.txt", "a") as f:
                            f.write(url + "\t" + artistName + "\n")
                        if "坂" in artistName:
                            send_telegram_message(
                                os.environ["bot_token"],
                                os.environ["chat_id"],
                                url,
                            )
                    else:
                        with open(f"line-{start}.txt", "a") as f:
                            f.write(url + "\n")
                        print(url)
                    break
                else:
                    print(
                        "Failed to retrieve. Status code:",
                        response.status_code,
                    )
                    break

            except Exception as e:
                print(e)
                print("Connection lost. Retrying in 10 seconds...")
                time.sleep(10)  # Wait 10 seconds before retrying
                break

        if code % 1000 == 0:
            while True:
                try:
                    await send_file_to_telegram()
                    break
                except:
                    print("send_file_to_telegram failed. Retrying in 10 seconds...")
                    time.sleep(10)  # Wait 10 seconds before retrying

    if need_update:
        # using an access token
        auth = Auth.Token(os.environ["github_token"])

        # First create a Github instance:
        # Public Web Github
        g = Github(auth=auth)

        # Then play with your Github objects:
        repo = g.get_user().get_repo("cron")
        contents = repo.get_contents("line.json")

        data["last"] = start + 5005
        data["running"] = False

        with open("line.json", "r") as f:
            repo.update_file("line.json", f"line e {start}", f.read(), contents.sha)

        # To close connections after use
        g.close()


import asyncio

if __name__ == "__main__":
    asyncio.run(main())
