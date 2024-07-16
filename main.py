import logging
import random
import time
from web3 import Web3
from abi import abi
from colorama import Fore, Style, init
from settings import VALIDATORS, DELAY

init()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('transactions.log')
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

infura_url = "https://mainnet.base.org"
web3 = Web3(Web3.HTTPProvider(infura_url))

if not web3.is_connected():
    raise Exception("Не удается подключиться к сети Base")

contract_address = Web3.to_checksum_address("0xB0fFa8000886e57F86dd5264b9582b2Ad87b2b91")
contract = web3.eth.contract(address=contract_address, abi=abi)

with open('private_keys.txt', 'r') as file:
    private_keys = [line.strip() for line in file.readlines()]

total_keys = len(private_keys)

def send_transaction(private_key, index):
    my_address = web3.eth.account.from_key(private_key).address  
    try:
        random_delegate = random.choice(VALIDATORS)
        transaction = contract.functions.delegate(random_delegate)
        gas_estimate = transaction.estimate_gas({'from': my_address})
        txn = transaction.build_transaction({
            'chainId': 8453,  
            'gas': gas_estimate,
            'gasPrice': web3.to_wei('20', 'gwei'),
            'nonce': web3.eth.get_transaction_count(my_address),
        })

        signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        message = f"[{my_address}] : {tx_receipt}"
        logging.info(message)
        print(Fore.GREEN + message + Style.RESET_ALL)

    except Exception as e:
        message = f"[{my_address}] : {e}"
        logging.error(message)
        print(Fore.RED + message + Style.RESET_ALL)


        with open('error_keys.txt', 'a') as error_file:
            error_file.write(private_key + '\n')


    print(Fore.YELLOW + f"Обработано {index + 1} из {total_keys} кошельков." + Style.RESET_ALL)

for index, private_key in enumerate(private_keys):
    send_transaction(private_key, index)

    sec_to_sleep = random.randint(DELAY[0], DELAY[1])
    print(f"Sleep {sec_to_sleep} seconds....")
    time.sleep(sec_to_sleep)