"""
Manage multiple undercutting bots simultaneously, setup via config.yaml.
Activity recorded in post_lower.log.
"""

import time
import yaml
import threading
import logging

from src.wax_class import WaxNFT
from src.wax_tools import get_lowest_listing

# ---------------- Logging Setup ----------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(nft_template)s] %(message)s",
    handlers=[
        logging.FileHandler("./bots/post_lower/post_lower.log"),
        logging.StreamHandler()
    ]
)

def get_logger(template_name: str):
    """Return a LoggerAdapter that injects nft_id into log records."""

    logger = logging.getLogger("post_lower")
    return logging.LoggerAdapter(logger, {"nft_template": template_name})


# ---------------- Bot Logic --------------------------

def initialise_nft(nft_id: str, min_price: float, wax_increment: float, api_refresh_seconds: int) -> WaxNFT:
    """Initialise NFT object and ensure it is listed at a valid starting price."""

    nft = WaxNFT(nft_id)
    nft.fetch_details()
    template_id = nft.template_id
    logger = get_logger(nft.template_name)

    if nft.sale_id is None:
        lowest_listing = get_lowest_listing(template_id)
        start_price = lowest_listing.get("price") - wax_increment

        if start_price < min_price:
            logger.warning(f"Starting price {start_price} below minimum {min_price}, listing witheld.")
            raise ValueError("Starting price is below minimum price")

        nft.sell(start_price)
        logger.info(f"NFT listed for sale at {start_price} WAX")

        time.sleep(api_refresh_seconds)

    return nft


def adjust_price_loop(
    nft: WaxNFT,
    min_price: float,
    wax_increment: float,
    rate_limit_seconds: int,
    api_refresh_seconds: int,
    error_retry_seconds: int,
):
    """Main loop for monitoring and adjusting NFT price with exponential backoff on errors."""

    logger = get_logger(nft.template_name)
    template_id = nft.template_id
    err_count = 0  # Track number of consecutive errors

    while True:

        try:
            lowest_listing = get_lowest_listing(template_id)

            # If already the lowest listing
            if lowest_listing.get("asset_id") == nft.nft_id:
                time.sleep(rate_limit_seconds)
                err_count = 0
                continue

            # Undercut by increment
            new_price = lowest_listing.get("price") - wax_increment
            if new_price < min_price:
                logger.info(f"Minimum price reached: {new_price} WAX < {min_price} WAX")
                break

            nft.update_offer(new_price)
            logger.info(f"Price updated to {new_price} WAX")
            time.sleep(api_refresh_seconds)
            err_count = 0  # Reset error counter on success

        except Exception as e:
            err_count += 1
            backoff = (2 ** (err_count - 1)) * error_retry_seconds
            logger.error(f"{e}. Retrying in {backoff}s..")
            time.sleep(backoff)


def run_price_bot(
    nft_id: WaxNFT,
    min_price: float,
    wax_increment: float,
    rate_limit_seconds: int,
    api_refresh_seconds: int,
    error_retry_seconds: int,
):
    
    nft = initialise_nft(nft_id, min_price, wax_increment, api_refresh_seconds)
    adjust_price_loop(nft, min_price, wax_increment, rate_limit_seconds, api_refresh_seconds, error_retry_seconds)


def run_from_config(config_path):
    """Run the bot(s) using parameters from config.yaml."""

    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    # Global settings
    rate_limit_seconds = cfg["rate_limit_seconds"]
    refresh = cfg["api_refresh_seconds"]
    retry = cfg["error_retry_seconds"]

    for nft_cfg in cfg.get("nfts", []):
        t = threading.Thread(
            target=run_price_bot,
            args=(
                nft_cfg["nft_id"],
                nft_cfg["min_price"],
                nft_cfg["wax_increment"],
                rate_limit_seconds,
                refresh,
                retry,
            ),
            daemon=True
        )
        t.start()
        time.sleep(1)  # Stagger requests

    while True:
        time.sleep(60)  # We keep the main thread running and use daemons, this allows for easy shutdown via keyboard interrupt


if __name__ == "__main__":
    run_from_config("./bots/post_lower/config.yaml")