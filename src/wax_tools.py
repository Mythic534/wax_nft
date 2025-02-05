import requests

def get_collection_by_templates(account: str, template_ids: list, display: str="full"):
    """
    Fetch NFT asset IDs for a given account and list of template IDs.

    Parameters:
        account (str): The WAX account name.
        template_ids (list): A list of template IDs to query.
        display (str): Output mode - "full" (detailed list), "count" (total count), "none" (silent).

    Returns:
        list: Collected NFT asset IDs or empty list if none found.
    """

    if isinstance(template_ids, (int, str)):  
        template_ids = [template_ids]

    combined_nft_ids = []
    api = "https://wax.api.atomicassets.io/"

    for template_id in template_ids:
        
        endpoint = f"atomicassets/v1/assets?owner={account}&template_id={template_id}&page=1&limit=100&order=desc"
        url = api + endpoint

        response = requests.get(url)
        data = response.json()

        nft_ids = [nft["asset_id"] for nft in data["data"]]
        combined_nft_ids.extend(nft_ids)

    if not combined_nft_ids:
        return []

    if display == "full":
        print("\n".join(f"{i+1}) {nft}" for i, nft in enumerate(combined_nft_ids)), flush=True)  # Single print call is more efficient here
    
    if display == "count":
        print(f"{len(combined_nft_ids)} NFTs found", flush=True)
    
    return combined_nft_ids


def get_collection_by_category(account, schema_name, display="full"):
    """
    Fetch NFT asset IDs for a given account and schema name.

    Parameters:
        account (str): The WAX account name.
        schema_name (str): The schema name to query.
        display (str): Output mode - "full" (detailed list), "count" (total count), "none" (silent).

    Returns:
        list: Collected NFT asset IDs or empty list if none found.
    """

    combined_nft_ids = []
    api = "https://wax.api.atomicassets.io/"
        
    endpoint = f"atomicassets/v1/assets?owner={account}&schema_name={schema_name}&page=1&limit=100&order=desc"
    url = api + endpoint

    response = requests.get(url)
    data = response.json()

    nft_ids = [nft["asset_id"] for nft in data["data"]]
    combined_nft_ids.extend(nft_ids)

    if not combined_nft_ids:
        return []

    if display == "full":
        print("\n".join(f"{i+1}) {nft}" for i, nft in enumerate(combined_nft_ids)), flush=True)  # Single print call is more efficient here
    
    if display == "count":
        print(f"{len(combined_nft_ids)} NFTs found", flush=True)
    
    return combined_nft_ids