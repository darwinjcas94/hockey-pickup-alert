import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://tri-valley-ice-dublin.sportngin.com/register/form/200070745"

DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]

SAVE_FILE = "known_dates.json"


def send_discord_message(message):
    data = {"content": message}

    requests.post(DISCORD_WEBHOOK, json=data)


def extract_dates(html):
    soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text("\n")

    lines = [line.strip() for line in text.splitlines()]

    possible_dates = []

    for line in lines:
        if any(month in line for month in [
            "January", "February", "March", "April",
            "May", "June", "July", "August",
            "September", "October", "November", "December"
        ]):
            if len(line) < 100:
                possible_dates.append(line)

    return list(dict.fromkeys(possible_dates))


def load_known_dates():
    if not os.path.exists(SAVE_FILE):
        return []

    with open(SAVE_FILE, "r") as f:
        return json.load(f)


def save_known_dates(dates):
    with open(SAVE_FILE, "w") as f:
        json.dump(dates, f, indent=2)


def main():
    response = requests.get(URL)

    if response.status_code != 200:
        print("Failed to load page")
        return

    current_dates = extract_dates(response.text)

    known_dates = load_known_dates()

    new_dates = [d for d in current_dates if d not in known_dates]

    if known_dates and new_dates:
        message = "🚨 New Tri-Valley pickup dates posted!\n\n"

        for d in new_dates:
            message += f"• {d}\n"

        message += f"\n{URL}"

        send_discord_message(message)

        print("New dates found!")
    else:
        print("No new dates")

    save_known_dates(current_dates)


if __name__ == "__main__":
    main()