import json
import subprocess
import os
import requests

class WaxNFT:

    def __init__(self, nft_id, owner=None, template_id=None, template_name=None, price=None, sale_id=None):
        self.nft_id = str(nft_id)
        self.owner = owner
        self.template_id = template_id
        self.template_name = template_name
        self.price = price
        self.sale_id = sale_id
        self.previous_owner = None

    
    "--------------UTILITY METHODS--------------"

    
    def fetch_owner(self):
        """Ensures that self.owner is fetched and available."""

        if not self.owner:
            url = f"https://wax.api.atomicassets.io/atomicassets/v1/assets/{self.nft_id}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json().get("data")
                if data:
                    self.owner = data.get("owner")

                else:
                    raise ValueError(f"NFT {self.nft_id} not found.")
            else:
                raise ValueError(f"Failed to fetch owner for NFT {self.nft_id}. HTTP Status: {response.status_code}")
        
        return self.owner

    
    "--------------INFORMATION METHODS--------------"


    def fetch_nft_details(self, callback=None):
        """Fetches ALL the details of the NFT and updates the object properties."""

        url = f"https://wax.api.atomicassets.io/atomicassets/v1/assets/{self.nft_id}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json().get("data")
            if data:
                self.owner = data.get("owner", self.owner)
                self.template_id = data.get("template", {}).get("template_id", self.template_id)
                self.template_name = data.get("template", {}).get("immutable_data", {}).get("name", self.template_name)
                
                self.fetch_market_details()
                self.fetch_previous_owner()

                details = {
                    "owner": self.owner,
                    "template_id": self.template_id,
                    "template_name": self.template_name,
                    "price": self.price,
                    "sale_id": self.sale_id,
                    "previous_owner": self.previous_owner,
                }
            
                if callback:
                    callback(details)

                return details

            else:
                raise ValueError(f"NFT {self.nft_id} not found.")
        else:
            raise ValueError(f"Failed to fetch details for NFT {self.nft_id}. HTTP Status: {response.status_code}")
        

    def fetch_market_details(self):
        """Fetches the sale price and sale ID for the NFT if it is listed on the marketplace."""

        url = f"https://wax.api.atomicassets.io/atomicmarket/v1/sales?asset_id={self.nft_id}&state=1"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json().get("data")

            if data:
                sale = data[0]
                price = sale.get("listing_price", None)
                sale_id = int(sale.get("sale_id", None))
                if price:
                    price = float(price) / 10**8

                self.price = price
                self.sale_id = sale_id
                return {"price": price, "sale_id": sale_id}

        return {"price": None, "sale_id": None}
    

    def fetch_previous_owner(self):
        """Fetches the previous owner of the NFT by inspecting the last transfer"""

        self.fetch_owner()

        url = f"https://wax.api.atomicassets.io/atomicmarket/v1/transfers?asset_id={self.nft_id}&limit=1"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json().get("data")

            # Ensure chain API is up to date by checking that the current owner is the recipient of the last transfer
            if data and data[0].get("recipient_name") == self.owner:
                self.previous_owner = data[0].get("sender_name")

                return self.previous_owner
            
            else:
                raise ValueError(f"NFT {self.nft_id} previous owner not found.")
        else:
            raise ValueError(f"Failed to fetch previous owner for NFT {self.nft_id}. HTTP Status: {response.status_code}")
            
    
    "--------------TRANSACTION METHODS--------------"


    def _send_transaction(self, actions):
        """Runs transfer.js to execute transaction"""

        # Ensure actions.json is written to the same directory as this file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        actions_path = os.path.join(script_dir, "actions.json")
        transfer_js_path = os.path.join(script_dir, "transfer.js")

        # Write actions to actions.json
        try:
            with open(actions_path, "w") as f:
                json.dump(actions, f, indent=4)

            # Call transfer.js
            result = subprocess.run(
                ["node", transfer_js_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(f"JavaScript error: {result.stderr.strip()}")
            print("tx_id:", result.stdout.strip())

        except Exception as e:
            raise RuntimeError(f"Error during transaction: {e}")
    

    def transfer(self, new_owner, memo=""):
        """Transfers the NFT to a new owner"""

        if not self.owner:
            self.fetch_owner()

        action = {
            "account": "atomicassets",
            "name": "transfer",
            "authorization": [{"actor": self.owner, "permission": "active"}],
            "data": {
                "from": self.owner,
                "to": new_owner,
                "asset_ids": [self.nft_id],
                "memo": memo,
            },
        }
        self._send_transaction([action])
        self.owner = new_owner
        print(f"NFT {self.nft_id} transferred to {new_owner}")


    def sell(self, price):
        """Lists the NFT for sale on the atomicmarket"""

        if not self.owner:
            self.fetch_owner()

        action_createoffer = {
            "account": "atomicassets",
            "name": "createoffer",
            "authorization": [{"actor": self.owner, "permission": "active"}],
            "data": {
                "memo": "sale",
                "sender_asset_ids": [self.nft_id],
                "recipient": "atomicmarket",
                "recipient_asset_ids": [],
                "sender": self.owner,
            },
        }

        action_announcesale = {
            "account": "atomicmarket",
            "name": "announcesale",
            "authorization": [{"actor": self.owner, "permission": "active"}],
            "data": {
                "seller": self.owner,
                "asset_ids": [self.nft_id],
                "listing_price": f"{price:.8f} WAX",
                "settlement_symbol": "8,WAX",
                "maker_marketplace": "",
            },
        }

        self._send_transaction([action_announcesale, action_createoffer])

        self.price = price
        print(f"NFT {self.nft_id} listed for sale at {price} WAX")


    def buy(self, buyer):
        """Buys the NFT listed for sale"""

        if self.sale_id or self.price is None:
            self.fetch_market_details()

        action_assertsale = {
            "account": "atomicmarket",
            "name": "assertsale",
            "authorization": [{"actor": buyer, "permission": "active"}],
            "data": {
                "asset_ids_to_assert": [self.nft_id],
                "sale_id": self.sale_id,
                "listing_price_to_assert": f"{self.price:.8f} WAX",
                "settlement_symbol_to_assert": "8,WAX",
            },
        }

        action_transfer = {
            "account": "eosio.token",
            "name": "transfer",
            "authorization": [{"actor": buyer, "permission": "active"}],
            "data": {
                "from": buyer,
                "to": "atomicmarket",
                "quantity": f"{self.price:.8f} WAX",
                "memo": "deposit",
            },
        }

        action_purchasesale = {
            "account": "atomicmarket",
            "name": "purchasesale",
            "authorization": [{"actor": buyer, "permission": "active"}],
            "data": {
                "buyer": buyer,
                "intended_delphi_median": 0,
                "sale_id": self.sale_id,
                "taker_marketplace": "",
            },
        }

        self._send_transaction([action_assertsale, action_transfer, action_purchasesale])
        print(f"NFT {self.nft_id} bought for {self.price} WAX")