import json
import subprocess
import os
from src.api_session import api_get


class WaxTransaction:
    """Base class to handle Wax transactions."""

    def _send_transaction(self, actions):
        """Run transfer.js to execute transaction"""

        script_dir = os.path.dirname(os.path.abspath(__file__))
        actions_path = os.path.join(script_dir, "actions.json")
        transfer_js_path = os.path.join(script_dir, "transfer.js")

        # Write actions to actions.json
        try:
            with open(actions_path, "w") as f:
                json.dump(actions, f, indent=4)

            # Call transfer.js
            result = subprocess.run(
                ["node", "--no-warnings", transfer_js_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(f"JavaScript error: {result.stderr.strip()}")
            print("tx_id:", result.stdout.strip())

        except Exception as e:
            raise RuntimeError(f"Error during transaction: {e}")
        

class WaxNFT(WaxTransaction):
    """Handle NFT-specific operations."""

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
        """Ensure that self.owner is fetched and available."""

        if not self.owner:
            path = f"atomicassets/v1/assets/{self.nft_id}"
            response = api_get(path)

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


    def fetch_details(self, callback=None):
        """Fetch ALL the details of the NFT and update the object properties."""

        path = f"atomicassets/v1/assets/{self.nft_id}"
        response = api_get(path)

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
                    formatted_details = json.dumps(details, indent=4)
                    callback(formatted_details)

                return details

            else:
                raise ValueError(f"NFT {self.nft_id} not found.")
        else:
            raise ValueError(f"Failed to fetch details for NFT {self.nft_id}. HTTP Status: {response.status_code}")
        

    def fetch_market_details(self):
        """Fetch the sale price and sale ID for the NFT if it is listed on the marketplace."""

        path = f"atomicmarket/v1/sales?asset_id={self.nft_id}&state=1"
        response = api_get(path)

        if response.status_code == 200:
            data = response.json().get("data")

            if data:
                sale = data[0]
                price = sale.get("listing_price", None)
                sale_id = sale.get("sale_id", None)
                if price:
                    price = float(price) / 10**8

                self.price = price
                self.sale_id = sale_id
                return {"price": price, "sale_id": sale_id}

        return {"price": None, "sale_id": None}
    

    def fetch_previous_owner(self):
        """Fetch the previous owner of the NFT by inspecting the last transfer"""

        self.fetch_owner()

        path = f"atomicassets/v1/transfers?asset_id={self.nft_id}&limit=1"
        response = api_get(path)

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
    

    def transfer(self, recipient, memo=""):
        """Transfer the NFT to a new owner"""

        if not self.owner:
            self.fetch_owner()

        action = {
            "account": "atomicassets",
            "name": "transfer",
            "authorization": [{"actor": self.owner, "permission": "active"}],
            "data": {
                "from": self.owner,
                "to": recipient,
                "asset_ids": [self.nft_id],
                "memo": memo,
            },
        }
        self._send_transaction([action])
        self.owner = recipient
        print(f"NFT {self.nft_id} transferred to {recipient}")


    def sell(self, price):
        """List the NFT for sale on the atomicmarket"""

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

    
    def cancel_sale(self):
        """Cancels the sale of the NFT"""

        if not self.owner:
            self.fetch_owner()

        if not self.sale_id:
            self.fetch_market_details()
        
        action = {
            "account": "atomicmarket",
            "name": "cancelsale",
            "authorization": [{"actor": self.owner, "permission": "active"}],
            "data": {  	
                "sale_id": self.sale_id
            },
        }

        self._send_transaction([action])
        self.price = None
        self.sale_id = None
        print(f"Sale {self.sale_id} cancelled")


    def update_offer(self, new_price):
        """Updates the price of the NFT if it is already on sale"""

        if not self.owner:
            self.fetch_owner()

        if self.sale_id is None or self.price is None:
            self.fetch_market_details()

        old_price = self.price

        action_cancelsale = {
            "account": "atomicmarket",
            "name": "cancelsale",
            "authorization": [{"actor": self.owner, "permission": "active"}],
            "data": {  	
                "sale_id": self.sale_id
            },
        }

        action_announcesale = {
            "account": "atomicmarket",
            "name": "announcesale",
            "authorization": [{"actor": self.owner, "permission": "active"}],
            "data": {
                "seller": self.owner,
                "asset_ids": [self.nft_id],
                "listing_price": f"{new_price:.8f} WAX",
                "settlement_symbol": "8,WAX",
                "maker_marketplace": "",
            },
        }

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

        self._send_transaction([action_cancelsale, action_announcesale, action_createoffer])
        self.price = new_price
        self.sale_id = None
        print(f"Price updated from {old_price} WAX to {self.price} WAX")


    def buy(self, buyer):
        """Buys the NFT listed for sale"""

        if self.sale_id is None or self.price is None:
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


class WaxAccount(WaxTransaction):
    """Handle token-specific operations."""

    def __init__(self, account):
        self.account = account
        self.wax_balance = None
        self.cpu_staked = None
        self.net_staked = None


    "--------------INFORMATION METHODS--------------"


    def fetch_details(self, callback=None):
        """Fetch and display account information, update the object properties"""

        url = f"https://api.waxsweden.org/v2/state/get_account?limit=1&account={self.account}"  # Requires different endpoint
        response = api_get(url)

        if response.status_code == 200:
            data = response.json().get("account")

            if data:
                wax_balance = data.get("core_liquid_balance", self.wax_balance)
                cpu_staked = data.get("cpu_weight", self.cpu_staked)
                net_staked = data.get("net_weight", self.net_staked)

                self.wax_balance = float(wax_balance.split(" ")[0])
                self.cpu_staked = float(cpu_staked) / 10**8
                self.net_staked = float(net_staked) / 10**8

                details = {
                    "account": self.account,
                    "wax_balance": self.wax_balance,
                    "cpu_staked": self.cpu_staked,
                    "net_staked": self.net_staked,
                }

                if callback:
                    formatted_details = json.dumps(details, indent=4)
                    callback(formatted_details)
                    
                return details

            else:
                raise ValueError(f"Account {self.account} not found.")
        else:
            raise ValueError(f"Failed to fetch details for account {self.account}. HTTP Status: {response.status_code}")
    

    "--------------TRANSACTION METHODS--------------"


    def unstake_wax(self, from_account, cpu_amount=0, net_amount=0):
        """Unstake WAX from account"""

        action = {
            "account": "eosio",
            "name": "undelegatebw",
            "authorization": [{"actor": self.account, "permission": "active"}],
            "data": {
                "from": self.account,
                "receiver": from_account,
                "unstake_cpu_quantity": f"{cpu_amount:.8f} WAX",
                "unstake_net_quantity": f"{net_amount:.8f} WAX",
            },
        }

        self._send_transaction([action])
        print(f"{self.account} unstaked {cpu_amount} WAX of CPU and {net_amount} WAX of NET from {from_account}")


    def transfer_wax(self, recipient, amount, memo=""):
        """Transfer WAX to recipient"""

        action = {
            "account": "eosio.token",
            "name": "transfer",
            "authorization": [{"actor": self.account, "permission": "active"}],
            "data": {
                "from": self.account,
                "to": recipient,
                "quantity": f"{amount:.8f} WAX",
                "memo": memo,
            },
        }

        self._send_transaction([action])
        print(f"{self.account} transferred {amount} WAX to {recipient}")


    def bulk_transfer_nfts(self, recipient, nfts_list: list, memo=""):
        """Transfer single or multiple NFTs to a new owner"""

        action = {
            "account": "atomicassets",
            "name": "transfer",
            "authorization": [{"actor": self.account, "permission": "active"}],
            "data": {
                "from": self.account,
                "to": recipient,
                "asset_ids": nfts_list,
                "memo": memo,
            },
        }

        self._send_transaction([action])
        print(f"{len(nfts_list)} NFTs transferred from {self.account} to {recipient}")