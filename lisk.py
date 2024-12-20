import time
import json
import requests
from web3 import Web3
from time import sleep
import os
import random
from colorama import Fore, Style, init
import datetime
from datetime import datetime, timedelta
import threading
from decimal import Decimal
import pytz
from pyfiglet import figlet_format
from termcolor import colored

init(autoreset=True)


def current_time():
    timezone = pytz.timezone('Asia/Jakarta')

    local_time = datetime.now(timezone)

    return local_time.strftime('%H:%M:%S')

def print_success(message, end='\n'):
    print(Fore.GREEN + f"[{current_time()}] " + Fore.GREEN + Style.BRIGHT + f"[SUCCESS] {message}" + Style.RESET_ALL, end=end)

def print_error(message, end='\n'):
    print(Fore.RED + f"[{current_time()}] " + Fore.RED + Style.BRIGHT + f"[ERROR] {message}" + Style.RESET_ALL, end=end)

def print_warning(message, end='\n'):
    print(Fore.YELLOW + f"[{current_time()}] " + Fore.YELLOW + Style.BRIGHT + f"[WARNING] {message}" + Style.RESET_ALL, end=end)

def print_info(message, end='\n'):
    print(Fore.BLUE + f"[{current_time()}] " + Fore.BLUE + Style.BRIGHT + f"[INFO] {message}" + Style.RESET_ALL, end=end)

def print_header():
    ascii_art = figlet_format("LISK", font="slant")
    colored_art = colored(ascii_art, color="blue")
    border = "-" * 25

    print(Fore.BLUE + Style.BRIGHT + border)
    print(colored_art)
    print(Fore.YELLOW + Style.BRIGHT +"github.com/dpangestuw")
    print(Fore.BLUE + Style.BRIGHT + border)
    print()

w3 = Web3(Web3.HTTPProvider("https://lisk.drpc.org"))

WETH_ADDRESS = "0x4200000000000000000000000000000000000006"
WETH_ABI = [
    {
        "constant": False,
        "inputs": [],
        "name": "deposit",
        "outputs": [],
        "payable": True,
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [{"name": "wad", "type": "uint256"}],
        "name": "withdraw",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

def get_eth_balance(address):
    try:
        balance_wei = w3.eth.get_balance(address)
        balance_eth = Web3.from_wei(balance_wei, 'ether')
        return balance_eth
    except Exception as e:
        print_error(f"Error fetching ETH balance",end='\r')
        return 0

def get_weth_balance(address):
    try:
        weth_contract = w3.eth.contract(address=WETH_ADDRESS, abi=ERC20_ABI)
        balance_wei = weth_contract.functions.balanceOf(address).call()
        balance_eth = Web3.from_wei(balance_wei, 'ether')
        return balance_eth
    except Exception as e:
        print_error(f"Error fetching WETH balance",end='\r')
        return 0

def wrap_eth(private_key):
    try:
        account = w3.eth.account.from_key(private_key.strip())
        address = account.address
        eth_balance = get_eth_balance(address)

        if eth_balance <= 0.00005:
            return False

        amount_eth = Decimal(str(eth_balance)) - Decimal('0.00005')

        weth_contract = w3.eth.contract(address=WETH_ADDRESS, abi=WETH_ABI)

        amount_wei = w3.to_wei(amount_eth, 'ether')
        txn = weth_contract.functions.deposit().build_transaction({
            'from': address,
            'value': amount_wei,
            'gas': 50000,
            'nonce': w3.eth.get_transaction_count(address),
            'gasPrice': w3.eth.gas_price,
        })
        print_info(f"Wrapping {amount_eth:.5f} ETH",end='\r')

        signed_txn = account.sign_transaction(txn)

        txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
        
        if receipt['status'] == 1:
            return True
        else:
            return False
    except Exception as e:
        return False

def unwrap_eth(private_key):
    try:
        account = w3.eth.account.from_key(private_key.strip())
        address = account.address
        weth_balance = get_weth_balance(address)

        if weth_balance <= 0:
            return False

        amount_weth = Decimal(str(weth_balance))

        weth_contract = w3.eth.contract(address=WETH_ADDRESS, abi=WETH_ABI)

        amount_wei = w3.to_wei(amount_weth, 'ether')
        txn = weth_contract.functions.withdraw(amount_wei).build_transaction({
            'from': address,
            'gas': 50000,
            'nonce': w3.eth.get_transaction_count(address),
            'gasPrice': w3.eth.gas_price,
        })
        print_info(f"Unwrapping {amount_weth:.5f} ETH",end='\r')
        signed_txn = account.sign_transaction(txn)
        
        txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
        
        if receipt['status'] == 1:
            return True
        else:
            return False
    except Exception as e:
        return False

def fetch_tasks(address):
    try:
        url = "https://portal-api.lisk.com/graphql"
        query = """
        query AirdropUser($filter: UserFilter!, $pointsHistoryFilter: QueryFilter, $tasksFilter: QueryFilter) {
          userdrop {
            user(filter: $filter) {
              address
              referredBy
              verifiedStatus
              rank
              points
              updatedAt
              createdAt
              referrals {
                totalCount
                points
                code
                rank
                referralsInfo {
                  userAddress
                  createdAt
                  points
                }
              }
              pointsHistories(filter: $pointsHistoryFilter) {
                totalCount
                histories {
                  id
                  taskID
                  taskDescription
                  points
                  createdAt
                }
              }
              tasks(filter: $tasksFilter) {
                id
                title
                description
                tasks {
                  id
                  description
                  type
                  daysForStreak
                  createdAt
                  frequency
                  points
                  progress {
                    id
                    isCompleted
                    streakInDays
                    frequencyCounter
                    points
                    completedAt
                  }
                  taskMetadata {
                    link {
                      url
                      description
                    }
                    icon
                  }
                }
                type
              }
            }
          }
        }
        """
        variables = {
            "filter": {"address": address},
            "pointsHistoryFilter": {},
            "tasksFilter": {}
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/graphql-response+json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
            'Origin': 'https://portal.lisk.com',
            'Referer': 'https://portal.lisk.com/',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9,id;q=0.8',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site'
        }

        response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
        
        response.raise_for_status()

        data = response.json()
        
        if 'errors' in data:
            print(f"GraphQL errors: {data['errors']}")
            return None

        user_data = data.get('data', {}).get('userdrop', {}).get('user', {})
        
        tasks = user_data.get('tasks', [])
        points_histories = user_data.get('pointsHistories', [])
        points = user_data.get('points', 0)
        rank = user_data.get('rank', '')

        incomplete_tasks = [task for task in tasks if not task['tasks'][0]['progress']['isCompleted']]
        
        return {
            "tasks": incomplete_tasks,
            "pointsHistories": points_histories,
            "points": points,
            "rank": rank
        }
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        try:
            response_json = e.response.json()
            print(f"Error details: {response_json}")
        except Exception as json_error:
            print(f"Error parsing response JSON: {json_error}")
        return None

def claim_task(address, task_id):
    try:
        url = "https://portal-api.lisk.com/graphql"
        mutation = """
        mutation UpdateAirdropTaskStatus($input: UpdateTaskStatusInputData!) {
          userdrop {
            updateTaskStatus(input: $input) {
              success
              progress {
                isCompleted
                completedAt
              }
            }
          }
        }
        """
        variables = {"input": {"address": address, "taskID": task_id}}
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/graphql-response+json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
            'Origin': 'https://portal.lisk.com',
            'Referer': 'https://portal.lisk.com/',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9,id;q=0.8',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site'
        }
        response = requests.post(url, json={'query': mutation, 'variables': variables}, headers=headers)
        data = response.json()
        
        success = data.get('data', {}).get('userdrop', {}).get('updateTaskStatus', {}).get('success', False)
        if success:
            print_success(f"Task {Fore.MAGENTA}{task_id} {Fore.GREEN}successfully claimed!")
        else:
            print_error(f"Failed to claim task {task_id}.")
    except Exception as e:
        print("Done",end='\r')

def start_daily_and_process_tasks(private_keys_file):
    try:
        with open(private_keys_file, 'r') as f:
            private_keys = f.read().splitlines()

        for private_key in private_keys:
            total_operations = 0

            account = w3.eth.account.from_key(private_key.strip())
            address = account.address
            address_short = f"{address[:5]}...{address[-5:]}"
            print(Fore.YELLOW + Style.BRIGHT + "="*102 + Style.RESET_ALL)
            print_info(f"Starting earning points {Fore.MAGENTA}{Style.BRIGHT}(Claim Task and On-chain Activity) {Fore.BLUE}for address {Fore.YELLOW}{Style.BRIGHT}{address_short}")

            while total_operations <= 72:
                eth_balance = get_eth_balance(address)
                weth_balance = get_weth_balance(address)
                total_balance = eth_balance + weth_balance

                if eth_balance > weth_balance and total_operations < 72:
                    wrap_success = wrap_eth(private_key)
                    time.sleep(random.uniform(1, 3))
                    if wrap_success:
                        total_operations += 1
                        print_success(f"Successfully Wrap/Unwrap {Fore.MAGENTA}{Style.BRIGHT}{total_operations} {Fore.GREEN}times. | Balance: {Fore.MAGENTA}{Style.BRIGHT}{total_balance} {Fore.GREEN}ETH",end='\r')
                        time.sleep(random.uniform(1, 3))
                    else:
                        print_error(f"Wrap failed, skipping this round | Balance: {Fore.MAGENTA}{Style.BRIGHT}{total_balance} ETH")
                        break

                elif weth_balance > eth_balance and total_operations < 72:
                    unwrap_success = unwrap_eth(private_key)
                    time.sleep(random.uniform(1, 3))
                    if unwrap_success:
                        total_operations += 1
                        print_success(f"Successfully Wrap/Unwrap {Fore.MAGENTA}{Style.BRIGHT}{total_operations} {Fore.GREEN}times. | Balance: {Fore.MAGENTA}{Style.BRIGHT}{total_balance} {Fore.GREEN}ETH",end='\r')
                        time.sleep(random.uniform(1, 3))
                    else:
                        print_error(f"Unwrap failed, skipping this round | Balance: {Fore.MAGENTA}{Style.BRIGHT}{total_balance} ETH")
                        break

                if total_operations >= 72:
                    print_success(f"Successfully Wrap/Unwrap {Fore.MAGENTA}{Style.BRIGHT}{total_operations} {Fore.GREEN}times. | Balance: {Fore.MAGENTA}{Style.BRIGHT}{total_balance} {Fore.GREEN}ETH")
                    break

            response = fetch_tasks(address)
            if response:
                tasks = response.get('tasks', [])
                points = response.get('points', 0)
                rank = response.get('rank', '')

                for task in tasks:
                    claim_task(address, task['id'])
                
                print_success(f"All task Successful for address {Fore.YELLOW}{Style.BRIGHT}{address_short} {Fore.GREEN}| Point: {Fore.MAGENTA}{points} {Fore.GREEN}| Rank: {Fore.MAGENTA}{rank}")
            else:
                print_error(f"Failed to fetch tasks or user data for address {address_short}")

            print(Fore.YELLOW + Style.BRIGHT + "="*102 + Style.RESET_ALL)
    except Exception as e:
        print_error(f"Error processing tasks", end='\r')

def start_task(private_keys_file):
    while True:
        start_daily_and_process_tasks(private_keys_file)
        for remaining_seconds in range(86400, 0, -1):
            minutes, seconds = divmod(remaining_seconds, 60)
            countdown = f"{minutes:02}:{seconds:02}"
            print_info(f"⌛ Waiting for the next schedule: {Fore.YELLOW}{Style.BRIGHT}{countdown}", end='\r')
            time.sleep(1)
        print_info("⌛ Waiting for the next schedule: 00:00", end='\r')

def main():
    print_header()
    private_keys_file = "pvkey.txt"
    daily_thread = threading.Thread(target=start_task, args=(private_keys_file,))
    daily_thread.start()
    daily_thread.join()

if __name__ == "__main__":
    main()
