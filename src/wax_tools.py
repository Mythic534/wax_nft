import requests


def get_collection(account, template_ids):

    combined_nft_ids = []
    api = "https://wax.api.atomicassets.io"

    for template_id in template_ids:
        
        endpoint = f"/atomicassets/v1/assets?owner={account}&template_id={template_id}&page=1&limit=100&order=desc"
        url = api + endpoint

        response = requests.get(url)
        data = response.json()

        nft_ids = [nft["asset_id"] for nft in data["data"]]
        combined_nft_ids.extend(nft_ids)

    if combined_nft_ids:

        print("NFTs returned:")
        for i, nft in enumerate(combined_nft_ids, start=1):
            print(f"{i}) {nft}")

        return combined_nft_ids
    
    else:
        print("Nothing found..")


"""Examples"""

#get_collection("lean4lan.gm", ["350147", "408663"])