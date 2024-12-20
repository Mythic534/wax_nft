import time

from src.wax_class import WaxNFT
from src.wax_tools import get_collection

account = "lean4lan.gm"
template_ids = ["350147", "408663"]  # Active card Mining pack, Active card War pack


while True:
    
    packs = get_collection(account, template_ids)

    if packs:
        for pack_id in packs:
            nft = WaxNFT(pack_id)
            nft.transfer("battleminers", "pack_opening")
            time.sleep(2)

    time.sleep(2)

