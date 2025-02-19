import time
import sys

from src.wax_class import WaxNFT
from src.wax_tools import get_collection_by_templates, get_collection_by_category

account = "lean4lan.gm"
template_ids = ["350147", "408663"]  # Active card Mining pack, Active card War pack
rate_limit_seconds = 2

def wait(seconds=rate_limit_seconds):
    time.sleep(seconds)


while True:
    print("\nFetching packs:", flush=True)
    packs = get_collection_by_templates(account, template_ids, display="count")

    if not packs:
        wait()
        continue

    senders = []
    new_actives = []

    # Store senders and open packs
    for pack_id in packs:
        nft = WaxNFT(pack_id)
        sender = nft.fetch_previous_owner()

        try:
            nft.transfer("battleminers", "pack_opening")
            senders.append(sender)
        except:
            print("Transfer unsuccessful.. continuing")
            pass

        wait()

    total_actives = len(senders)
    attempts = 0
    max_attempts = 20

    wait_time = 6
    print("\n" * 2)
    for i in range(wait_time, 0, -1):
        sys.stdout.write(f"\rWaiting for packs.. {i - 1}s ")
        sys.stdout.flush()
        wait(1)

    print()
    # Iterate through received actives until they all arrive or max attempts reached
    while attempts < max_attempts:
        actives = get_collection_by_category(account, "active", display="none")
        
        sys.stdout.write(f"\rFetching actives: Attempt {attempts + 1}/{max_attempts} | {len(actives)} / {total_actives} ")
        sys.stdout.flush()

        if len(actives) == total_actives:
            break

        attempts += 1
        wait()

    print()
    current_progress = 0

    for active_id in actives:
        nft = WaxNFT(active_id)
        try:
            source = nft.fetch_previous_owner()
        except Exception as e:
            print(f"Error fetching previous owner for {active_id}: {e}", flush=True)
            wait()
            continue

        wait(0.1)  # Adjust to avoid rate-limiting for large sets of data

        # Only match freshly minted actives to senders, otherwise
        # sending an already existing active to the account would break it
        if source == "battleminers" and active_id not in new_actives:
            new_actives.append(active_id)

        current_progress += 1
        progress_display = f" {current_progress} / {total_actives} "
        sys.stdout.write(f"\rMapping actives to senders: {progress_display}")
        sys.stdout.flush()

    print()
    # Return NFTs to senders before resetting the loop
    for sender, active in zip(senders, new_actives):
        while True:
            try:
                nft = WaxNFT(active)
                nft.transfer(sender)
                wait(0.5)
                break
            except Exception as e:
                print(f"Error transferring {active} to {sender}: {e}", flush=True)
                wait()