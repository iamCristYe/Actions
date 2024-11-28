import requests

import json
import time
import os
from telegram import Bot


# 发送压缩文件到Telegram
async def send_file_to_telegram():
    end = int(os.environ["end"])
    telegram_token = os.environ["bot_token"]  # 替换为你的Telegram bot token
    telegram_chat_id = os.environ["chat_id"]  # 替换为你的频道或群组ID
    bot = Bot(token=telegram_token)
    archive_path = os.path.join(".", f"line-{end}.txt")
    await bot.send_document(chat_id=telegram_chat_id, document=open(archive_path, "rb"))


def send_telegram_message(token, channel_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": channel_id,  # Channel ID with "@" (e.g., "@your_channel_id")
        "text": message,
    }
    response = requests.post(url, data=payload)
    return response.json()


async def main():
    start = int(os.environ["start"])
    end = int(os.environ["end"])
    for code in range(start, end, 1):
        # Define the URL of the image
        url = f"https://music.line.me/api2/tracks/mt00000000207{hex(code).split('x')[-1]}.v1"
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
                            with open(f"line-{end}.txt", "a") as f:
                                f.write(url + "\n")
                                print(url)
                                break
                        if result["response"]["result"]["trackTotalCount"] == 0:
                            with open(f"line-{end}.txt", "a") as f:
                                f.write(url + " trackTotalCount 0" "\n")
                                print(url)
                                break
                        artistName = result["response"]["result"]["tracks"][0][
                            "artists"
                        ][0]["artistName"]

                        print(artistName)
                        with open(f"line-{end}.txt", "a") as f:
                            f.write(url + "\t" + artistName + "\n")
                        if "坂" in "artistName":
                            send_telegram_message(
                                os.environ["bot_token"],
                                os.environ["chat_id"],
                                url,
                            )
                    else:
                        with open(f"line-{end}.txt", "a") as f:
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


import asyncio

if __name__ == "__main__":
    asyncio.run(main())
