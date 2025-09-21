# The WaxNFT Project

The `WaxNFT` class and tools provided by the project are intended to vastly simplify the process for setting up bots and scripts for the Wax blockchain in Python.

## Setup Instructions

### Prerequisites

Ensure you have the following installed:

1. **Node.js** - Download and install from [Node.js official site](https://nodejs.org/).
2. **Python** - Ensure Python is installed and available on your system.

### Environment Configuration

1. Create a `.env` file in the root directory of the project.
2. Add the following content to the `.env` file, replacing `<YOUR_PRIVATE_KEY>` with your actual active wallet key:

   ```env
   PRIVATE_KEY=<YOUR_PRIVATE_KEY>
   API_ENDPOINT=<VALID_WAX_ENDPOINT>

   # If using market_bot alerts:
   EMAIL_SENDER=<EMAIL_ACCOUNT>
   EMAIL_RECIPIENT=<EMAIL_ACCOUNT>
   EMAIL_PASSWORD=<EMAIL_PASSWORD>
   ```

### Installing Dependencies

Run the following commands to install project dependencies:

```bash
npm install
pip install -r requirements.txt
```

## Functionality Overview

Provided examples include a market bot which can be configured to buy NFTs, and a selling bot which can manage multiple listings simultaneously. Below is an overview of some of the fundamental operations.

### 1. Transfer NFT

Transfer an NFT to a specified Wax account. Memo optional.

```python
nft = WaxNFT(1099895475693)
nft.transfer("5wme4.wam", "hello world")
```

### 2. Buy NFT

Buy an NFT using the specified Wax account.

```python
nft.buy("lean4lan.gm")
```

### 3. Sell NFT

Sell an NFT for a specified amount of Wax.

```python
nft.sell(1.5)
```

### 4. Fetch NFT Details

Fetch detailed information about an NFT and print it to the terminal. Additional, more lightweight methods are available.

```python
nft.fetch_details(callback=print)
```

#### Example Output

```json
{
    "owner": "lean4lan.gm",
    "template_id": "260676",
    "template_name": "Farmer Coin",
    "price": null,
    "sale_id": null,
    "previous_owner": "5wme4.wam"
}
```

### 5. Access NFT Attributes

Retrieve attributes of an NFT directly from the class instance:

- `nft.nft_id` -> `str`
- `nft.owner` -> `str`
- `nft.template_id` -> `str`
- `nft.template_name` -> `str`
- `nft.price` -> `float`
- `nft.sale_id` -> `str`
- `nft.previous_owner` -> `str`

Example usage:

```python
if nft.price < 20:
    nft.buy("lean4lan.gm")
```

### 6. View NFTs by User

Using functions in wax_tools.py, query the wax API for filtered information about a user's collection. Store and display results neatly.

```python
nft_ids = get_collection_by_templates("5wme4.wam", ["350147", "408663"])  # -> list
nft_ids = get_collection_by_category("lean4lan.gm", "active")             # -> list
```