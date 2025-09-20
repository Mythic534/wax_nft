import time
from src.wax_class import WaxNFT
from src.wax_tools import get_lowest_listing

RATE_LIMIT_SECONDS = 5
API_REFRESH_SECONDS = 40
ERROR_RETRY_SECONDS = 30

# ======Configuration======
wax_increment = 1
min_price = 750
nft_id = "1099967985055"
# =========================


nft = WaxNFT(nft_id)
nft.fetch_details()
template_id = nft.template_id

if nft.sale_id is None:
    lowest_listing = get_lowest_listing(template_id)
    start_price = lowest_listing.get("price") - wax_increment

    if start_price < min_price:
        raise ValueError("Starting price is below minimum price")
    
    nft.sell(start_price)
    time.sleep(API_REFRESH_SECONDS)

err = 0  # Track number of consecutive errors
while True:

    try:
        lowest_listing = get_lowest_listing(template_id)
        if lowest_listing.get("asset_id") == nft_id:
            time.sleep(RATE_LIMIT_SECONDS)
            err = 0
            continue

        new_price = lowest_listing.get("price") - wax_increment
        if new_price < min_price:
            print("Minimum price reached")
            break
        
        nft.update_offer(new_price)
        time.sleep(API_REFRESH_SECONDS)

    except Exception as e:
        err += 1
        backoff_multiplier = 2**(err-1)
        print(f"{e}. Retrying in {backoff_multiplier * ERROR_RETRY_SECONDS}s..")
        time.sleep(backoff_multiplier * ERROR_RETRY_SECONDS)