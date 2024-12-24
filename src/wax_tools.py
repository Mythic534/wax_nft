import requests


def get_collection_by_templates(account, template_ids):

    combined_nft_ids = []
    api = "https://wax.api.atomicassets.io/"

    for template_id in template_ids:
        
        endpoint = f"atomicassets/v1/assets?owner={account}&template_id={template_id}&page=1&limit=100&order=desc"
        url = api + endpoint

        response = requests.get(url)
        data = response.json()

        nft_ids = [nft["asset_id"] for nft in data["data"]]
        combined_nft_ids.extend(nft_ids)

    if combined_nft_ids:

        for i, nft in enumerate(combined_nft_ids, start=1):
            print(f"{i}) {nft}")

        return combined_nft_ids
    
    else:
        print("Nothing found..")


def get_collection_by_category(account, schema_name):

    combined_nft_ids = []
    api = "https://wax.api.atomicassets.io/"
        
    endpoint = f"atomicassets/v1/assets?owner={account}&schema_name={schema_name}&page=1&limit=100&order=desc"
    url = api + endpoint

    response = requests.get(url)
    data = response.json()

    nft_ids = [nft["asset_id"] for nft in data["data"]]
    combined_nft_ids.extend(nft_ids)

    if combined_nft_ids:

        for i, nft in enumerate(combined_nft_ids, start=1):
            print(f"{i}) {nft}")

        return combined_nft_ids
    
    else:
        print("Nothing found..")


"""Examples"""

#get_collection_by_templates("lean4lan.gm", ["350147", "408663"])
#get_collection_by_category("lean4lan.gm", "active")