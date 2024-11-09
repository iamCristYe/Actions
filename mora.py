import requests

# https://cf.mora.jp/contents/package/0000/00000196/0035/166/917/0035166917.130.jpg
# https://cf.mora.jp/contents/package/0000/00000361/0028/463/167/0028463167.130.jpg
# https://cf.mora.jp/contents/package/0000/00000196/0025/241/396/0025241396.130.jpg 09 Nov 2023 08:11:28 GMT

import time
import os
from telegram import Bot

# 发送压缩文件到Telegram


async def send_file_to_telegram():
    telegram_token = os.environ["bot_token"]  # 替换为你的Telegram bot token
    telegram_chat_id = os.environ["chat_id"]  # 替换为你的频道或群组ID
    bot = Bot(token=telegram_token)
    archive_path = os.path.join(".", "mora.txt")
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
    for code1 in range(590, 605, 1):
        for code2 in range(0, 1000):
            # Define the URL of the image
            url = f"https://cf.mora.jp/contents/package/0000/00000361/0036/{code1:03d}/{code2:03d}/0036{code1:03d}{code2:03d}.130.jpg"
            print(f"Trying URL: {url}")

            # Retry mechanism in case of connection issues
            while True:
                try:
                    # Send a GET request to the URL
                    response = requests.get(url)
                    last_modified = response.headers.get("Last-Modified")
                    with open("mora.txt", "a") as f:
                        f.write(url + "\n" + last_modified + "\n")
                    # Check if the request was successful (status code 200)
                    if response.status_code == 200 and len(response.content) > 6 * 1024:
                        # Save the content to a file
                        # with open(f"0036{code1:03d}{code2:03d}.jpg", "wb") as file:
                        #     file.write(response.content)
                        # print(
                        #     f"Image saved successfully as 0036{code1:03d}{code2:03d}.jpg"
                        # )
                        send_telegram_message(
                            os.environ["bot_token"],
                            os.environ["chat_id"],
                            url,
                        )
                        break  # Exit the retry loop if successful
                    else:
                        print(
                            "Failed to retrieve the image. Status code:",
                            response.status_code,
                        )
                        break  # Exit the loop if image not found or another HTTP error

                except:
                    print("Connection lost. Retrying in 10 seconds...")
                    time.sleep(10)  # Wait 10 seconds before retrying

            # time.sleep(1)  # Pause between different URLs
        await send_file_to_telegram()


import asyncio

if __name__ == "__main__":
    asyncio.run(main())
