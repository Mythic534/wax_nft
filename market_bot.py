import time
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import traceback
import os
from dotenv import load_dotenv

from src.wax_class import WaxNFT, WaxAccount
from src.wax_tools import get_lowest_listing

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("market_bot.log"),
        logging.StreamHandler()
    ]
)

load_dotenv()
email_sender = os.getenv("EMAIL_SENDER")
email_recipient = os.getenv("EMAIL_RECIPIENT")
sender_password = os.getenv("EMAIL_PASSWORD")

account = "lean4lan.gm"
RATE_LIMIT_SECONDS = 0.5
BALANCE_REFRESH_INTERVAL_SECONDS = 60

template_id = "783873"  # NBM Spin and Win
target_price = 14


def main():

    buyer = WaxAccount(account)
    buyer.fetch_details()
    wax_balance = buyer.wax_balance
    logging.info(f"Starting balance: {wax_balance:.2f} WAX")

    last_balance_update = time.time()
    last_error_logged = False  # Prevent error spam to the log
    low_balance_notified = False

    while True:

        now = time.time()
        if now - last_balance_update > BALANCE_REFRESH_INTERVAL_SECONDS:
            wax_balance = check_balance(wax_balance, low_balance_notified)
            last_balance_update = time.time()

        try:
            if wax_balance < target_price:
                if not low_balance_notified:
                    warning_msg = f"Balance {wax_balance:.2f} WAX below target price {target_price:.2f}. Pausing operation."
                    logging.warning(warning_msg)
                    notification(
                        warning_msg,
                        email_sender,
                        email_recipient,
                        sender_password
                    )
                    low_balance_notified = True

                wait(60)  # Wait here if balance too low to buy
                wax_balance = check_balance(wax_balance, low_balance_notified)
                last_balance_update = time.time()
                continue

            listing_details = get_lowest_listing(template_id)

            if listing_details and listing_details["price"] <= target_price:
                nft = WaxNFT(
                    nft_id=listing_details["asset_id"],
                    price=listing_details["price"],
                    sale_id=listing_details["sale_id"]
                )

                nft.buy(account)
                logging.info(f"Purchased NFT: {listing_details}")

                wax_balance -= listing_details["price"]
                logging.info(f"Remaining balance: {wax_balance:.2f} WAX")

            last_error_logged = False

        except Exception as e:
            error_message = str(e)

            if "No sale with this sale_id exists" in error_message:  # Handle API lag
                pass

            else:
                if not last_error_logged:
                    detailed_trace = traceback.format_exc()
                    logging.error("An error occurred:\n" + detailed_trace)

                    last_error_logged = True
                    error_warning = f"Market bot encountered an error:\n\n{error_message}"
                    notification(
                        error_warning,
                        email_sender,
                        email_recipient,
                        sender_password
                    )

        wait()


def notification(message, email_sender, email_recipient, sender_password):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Bot Alert"
    msg['From'] = email_sender
    msg['To'] = email_recipient

    part1 = MIMEText(message, 'plain', 'utf-8')
    msg.attach(part1)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(email_sender, sender_password)
            server.sendmail(email_sender, email_recipient, msg.as_string())
    except:
        pass  # Will fail in case of internet outage


def check_balance(wax_balance, low_balance_notified):

    buyer = WaxAccount(account)
    buyer.fetch_details()
    if buyer.wax_balance != wax_balance:
        wax_balance = buyer.wax_balance
        if not low_balance_notified:
            logging.info(f"Balance updated: {wax_balance:.2f} WAX")
        
    return wax_balance


def wait(seconds=RATE_LIMIT_SECONDS):
    time.sleep(seconds)


if __name__ == "__main__":
    main()