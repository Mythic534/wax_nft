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