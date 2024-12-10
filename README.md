# Lisk Task Automation

This repository contains a Python script that automates interacting with the Lisk for tasks such as wrapping and unwrapping ETH, and claiming tasks through the Lisk Portal Airdrop Program. The automation works with Ethereum (ETH) and Wrapped Ethereum (WETH) tokens and interacts with the Lisk portal's GraphQL API.

## Join Now
- https://portal.lisk.com/airdrop
- Connect Wallet Metamask Wallet
- Complete Task Guild & Verify
- Enter Code : ```Xjc7Ur```
- Complete Task *(task hold optional)*
- Bridge ETH Base To ETH LISK : https://relay.link/bridge/lisk

## Features

- **ETH & WETH Management**: The script can wrap and unwrap ETH on the Lisk blockchain.
- **Task Automation**: Automatically fetches and claims tasks related to the Lisk airdrop program.
- **Point Earning**: Earning points through on-chain activities and task completions.
- **Periodic Execution**: The script runs periodically to check and complete tasks at scheduled intervals.

## Requirements

Before running this script, ensure that you have the following installed:
- **Setup Private Keys File** :
  The script requires a file (pvkey.txt) containing your private keys (one key per line). Each key will be used to manage ETH/WETH balances and claim tasks. Ensure that the private keys provided belong to wallets that are active and have some ETH balance.

- **Python 3.x**
- **Required Python Libraries**:

```bash
pip install web3 requests colorama pyfiglet termcolor pytz
```

<img width="829" alt="Screenshot 2024-12-10 at 08 36 15" src="https://github.com/user-attachments/assets/ecae8dff-645d-4a13-91dc-3d9dabb40add">



