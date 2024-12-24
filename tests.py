from src.wax_class import WaxNFT
from src.wax_tools import get_collection_by_category, get_collection_by_templates  # Tools for fetching NFTs from individual user accounts

nft = WaxNFT(1099895475693)

"Transfer NFT to 5wme4.wam"
# nft.transfer("5wme4.wam")

"Buy NFT using the account lean4lan.gm"
nft.buy("lean4lan.gm")

"Sell NFT for 1.5 wax"
# nft.sell(1.5)

"Fetches information about the NFT, stores it in the class and prints to the terminal, more lightweight methods available"
# nft.fetch_details(callback=print)
"""
output: {
    "owner": "lean4lan.gm",
    "template_id": "260676",
    "template_name": "Farmer Coin",
    "price": null,
    "sale_id": null,
    "previous_owner": "5wme4.wam"
}
"""

"Any of the following attributes can fetched from the class"
# nft.nft_id -> str
# nft.owner -> str 
# nft.template_id -> str 
# nft.template_name -> str 
# nft.price -> float
# nft.sale_id -> str
# nft.previous_owner -> str

# if nft.price < 20:
#   nft.buy("lean4lan.gm")