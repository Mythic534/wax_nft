import time

from src.wax_class import WaxNFT
from src.wax_tools import get_collection_by_templates, get_collection_by_category

account = "lean4lan.gm"
template_ids = ["350147", "408663"]  # Active card Mining pack, Active card War pack
rate_limit_seconds = 2


def wait():
    time.sleep(rate_limit_seconds)


while True:
    print("\nFetching packs:")
    packs = get_collection_by_templates(account, template_ids)

    if not packs:
        wait()
        continue

    senders = []
    new_actives = []

    # Store senders and open packs
    for pack_id in packs:
        nft = WaxNFT(pack_id)
        sender = nft.fetch_previous_owner()
        senders.append(sender)

        nft.transfer("battleminers", "pack_opening")
        wait()

    # Iterate through received actives until they all arrive
    while True:
        print("\nFetching actives:")

        actives = get_collection_by_category(account, "active")
        if not actives:
            wait()
            continue

        for active_id in actives:
            nft = WaxNFT(active_id)
            source = nft.fetch_previous_owner()
            active_id

            # Only match freshly minted actives to senders, otherwise
            # sending an already existing active to the account would break it
            if source == "battleminers" and active_id not in new_actives:
                new_actives.append(active_id)

        print(f"Debug - senders: {senders}")
        print(f"Debug - actives: {new_actives}")
        
        if len(new_actives) == len(senders):
            break

        wait()

    # Return NFTs to senders before resetting the loop
    for sender, active in zip(senders, new_actives):
        while True:
            try:
                nft = WaxNFT(active)
                nft.transfer(sender)
                wait()
                break
            except:
                print("Retrying transfer..")
                wait()