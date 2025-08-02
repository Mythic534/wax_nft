import requests
import os
from dotenv import load_dotenv
from src.api_session import api_get

def get_collection_by_templates(account: str, template_ids: list, display: str="none"):
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

    for template_id in template_ids:
        
        path = f"atomicassets/v1/assets?owner={account}&template_id={template_id}&page=1&limit=100&order=desc"
        response = api_get(path)
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


def get_collection_by_category(account, schema_name, display="none"):
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
        
    path = f"atomicassets/v1/assets?owner={account}&schema_name={schema_name}&page=1&limit=100&order=desc"
    response = api_get(path)
    data = response.json()

    nft_ids = [nft["asset_id"] for nft in data["data"]]
    combined_nft_ids.extend(nft_ids)

    if not combined_nft_ids:
        return []

    if display == "full":
        print("\n".join(f"{i+1}) {nft}" for i, nft in enumerate(combined_nft_ids)), flush=True)
    
    if display == "count":
        print(f"{len(combined_nft_ids)} NFTs found", flush=True)
    
    return combined_nft_ids


def get_lowest_listing(template_id):
    """
    Fetches the lowest-priced listing for the given template.

    Returns:
        dict: Collected NFT info or empty dict if none found.
    """
    
    path = f"atomicmarket/v2/sales"
    params = {
        "template_id": template_id,
        "limit": "1",
        "order": "asc",
        "page": "1",
        "sort": "price",
        "state": "1",
        "symbol": "WAX"
    }
    response = api_get(path, params=params)
    data = response.json().get("data")

    if data:
        asset_id = data[0].get("assets")[0].get("asset_id")
        sale_id = data[0].get("sale_id")
        price = data[0].get("price").get("amount")
        price = float(price) / 10**8

    else:
        return {}

    details = {
        "asset_id": asset_id,
        "sale_id": sale_id,
        "price": price
    }

    return details


def group_transactions(nft_ids: list, recepients: list, group_size: int = 50):
    """
    Groups NFTs by recipient into sub-lists of a specified maximum size.

    Parameters:
    nft_ids (list): A list of NFT IDs.
    recepients (list): A list of recipient addresses corresponding to each NFT ID.
    group_size (int): The maximum number of NFTs per sub-list (default is 50).

    Returns:
    dict: A dictionary where each key is a recipient address and the value is a list of sub-lists,
          each containing up to 'group_size' NFT IDs.
    """

    if len(nft_ids) != len(recepients):
        raise ValueError("nft_ids and recepients lists must be of equal length")
    
    transactions = {}
    for nft, recepient in zip(nft_ids, recepients):

        if recepient not in transactions:
            transactions[recepient] = [[]]
        
        last_group = transactions[recepient][-1]
        
        if len(last_group) < group_size:
            last_group.append(nft)
        else:
            transactions[recepient].append([nft])
    
    return transactions