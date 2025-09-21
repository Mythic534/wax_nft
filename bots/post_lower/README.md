# Post Lower Bot

This bot monitors and manages NFT listings on the WAX marketplace.  
It ensures your NFTs remain the lowest listing for their template by undercutting the competition by a configurable increment.  

## ⚙ Configuration

The bot is configured using a `config.yaml` file located in the same directory (`bots/post_lower/config.yaml`).  
Since this file contains your personal NFT IDs and strategy settings, it is **not included in version control**. You will need to create it manually.

There is no limit to the number of NFTs you can track, but you may need to increase the rate_limit_seconds to manage a large amount.
Do **NOT** add multiple NFTs of the same template. I haven't added any logic for this so it will probably just continually undercut itself!

### Example `config.yaml`

```yaml
# Global settings
rate_limit_seconds: 5        # Small delay between API calls when no changes are needed
api_refresh_seconds: 40      # Delay after successful price update or listing

# NFT-specific settings
nfts:
  - nft_id: "1099967985055"
    min_price: 700
    wax_increment: 1

  - nft_id: "1099967294229"
    min_price: 19
    wax_increment: 0.1
```