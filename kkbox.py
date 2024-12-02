import requests

import json
import time
import os
from telegram import Bot
from github import Github
from github import Auth


# 发送压缩文件到Telegram
async def send_file_to_telegram():
    with open("kkbox.json") as f:
        data = json.load(f)
        start = int(data["last"] / 1000) * 1000 - 1
    telegram_token = os.environ["bot_token"]  # 替换为你的Telegram bot token
    telegram_chat_id = os.environ["chat_id"]  # 替换为你的频道或群组ID
    bot = Bot(token=telegram_token)
    archive_path = os.path.join(".", f"kkbox-{start}.txt")
    await bot.send_document(chat_id=telegram_chat_id, document=open(archive_path, "rb"))


def send_telegram_image(token, channel_id, url, message):
    while True:
        try:
            url = f"https://api.telegram.org/bot{token}/sendPhoto"
            payload = {
                "chat_id": channel_id,  # Channel ID with "@" (e.g., "@your_channel_id")
                "photo": url,
                "caption": message,
            }
            response = requests.post(url, data=payload)
            time.sleep(30)
            return response.json()
        except:
            time.sleep(30)


async def main():
    data = {}
    need_update = False
    with open("kkbox.json") as f:
        data = json.load(f)
        if data["running"]:
            return
        start = int(data["last"] / 1000) * 1000 - 1
        data["running"] = True
        with open("kkbox.json", "w") as f:
            json.dump(data, f)

        # using an access token
        auth = Auth.Token(os.environ["github_token"])

        # First create a Github instance:
        # Public Web Github
        g = Github(auth=auth)

        # Then play with your Github objects:
        repo = g.get_user().get_repo("cron")
        contents = repo.get_contents("kkbox.json")

        with open("kkbox.json", "r") as f:
            repo.update_file("kkbox.json", f"kkbox s {start}", f.read(), contents.sha)

        # To close connections after use
        g.close()

    for code in range(start, start + 5005, 1):
        # Define the URL of the image
        url = f"https://i.kfs.io/album/global/{code},1v1/fit/500x500.jpg"
        # https://i.kfs.io/artist/global/407071,0v36/fit/500x500.jpg
        print(code, url)
        # Send a GET request to the URL

        # Retry mechanism in case of connection issues
        while True:
            try:
                response = requests.get(url)
                last_modified = response.headers.get("last-modified")

                time.sleep(1)
                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    if len(response.content) > 6 * 1024:
                        print(last_modified)
                        # Save the content to a file
                        # with open(f"img/{code}.jpg", "wb") as file:
                        #     file.write(response.content)
                        with open(f"kkbox-{start}.txt", "a") as f:
                            f.write(url + "\t" + last_modified + "\n")
                        send_telegram_image(
                            os.environ["bot_token"],
                            os.environ["chat_id"],
                            url,
                            url + "\n" + last_modified,
                        )
                        need_update = True
                        print("Image saved successfully.")
                    else:
                        with open(f"kkbox-{start}.txt", "a") as f:
                            f.write(url + "\n")
                        print("File < 6KB")
                    break
                else:
                    print(
                        "Failed to retrieve the image. Status code:",
                        response.status_code,
                    )
                    break

            except Exception as e:
                print(e)
                print("Connection lost. Retrying in 10 seconds...")
                time.sleep(10)  # Wait 10 seconds before retrying

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
        contents = repo.get_contents("kkbox.json")

        data["last"] = start + 5005
        data["running"] = False

        with open("kkbox.json", "r") as f:
            repo.update_file("kkbox.json", f"kkbox e {start}", f.read(), contents.sha)

        # To close connections after use
        g.close()


import asyncio

if __name__ == "__main__":
    asyncio.run(main())
