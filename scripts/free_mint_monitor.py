#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2022/6/15 5:17 PM
# @Author  : donghao
import asyncio
import json
import os.path
from os import path

from web3 import Web3
from web3._utils.encoding import to_json
import warnings

from dotenv import load_dotenv
load_dotenv()

MAIN_NET_PROJECT_ID = os.environ.get("MAIN_NET_PROJECT_ID")


warnings.filterwarnings('ignore')

NONE_ADDRESS = "0x0000000000000000000000000000000000000000"
DEFAULT_ABI_JSON_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "abi")


def get_contract_abi(contract_name: str, abi_dir=DEFAULT_ABI_JSON_FILE_PATH):
    file_name = f"{contract_name}.json"
    file_full_name = path.join(abi_dir, file_name)
    with open(file_full_name) as f:
        abi_data = f.read()
        abi_json = json.loads(abi_data)
        return abi_json['abi']


IERC721_CONTRACT_ABI = get_contract_abi("IERC721")
IERC1155_CONTRACT_ABI = get_contract_abi("IERC1155")


class Handler(object):

    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{MAIN_NET_PROJECT_ID}'))
        self.erc721_contract_instance = self.w3.eth.contract(address=None, abi=IERC721_CONTRACT_ABI)
        self.erc1155_contract_instance = self.w3.eth.contract(address=None, abi=IERC1155_CONTRACT_ABI)

    def _parese_event(self, event_obj, log):
        result = event_obj.processReceipt(log)
        if result:
            result = json.loads(to_json(result))
        return result

    def _transfer_event(self, log):
        return self._parese_event(self.erc721_contract_instance.events.Transfer(), log)

    def _transfer_single_event(self, log):
        return self._parese_event(self.erc1155_contract_instance.events.TransferSingle(), log)

    def _transfer_batch_event(self, log):
        return self._parese_event(self.erc1155_contract_instance.events.TransferBatch(), log)

    async def prase_logs(self, block_number):
        block_logs = self.w3.eth.get_logs({
                "toBlock": block_number,
                "fromBlock": block_number})
        block_info = self.w3.eth.get_block(block_number, full_transactions=True)
        transactions = block_info['transactions']
        transaction_hash_to_data = {}
        for transaction in transactions:
            value_ether = self.w3.fromWei(transaction['value'], 'ether')
            if value_ether == 0:
                # https://docs.infura.io/infura/networks/ethereum/json-rpc-methods/eth_gettransactionbyhash
                transaction_hash_to_data[transaction['hash']] = {
                    # value transferred in Wei
                    "value_wei": format(value_ether, 'f'),
                    "value_ether": format(value_ether, 'f'),
                    "from_addr": transaction['from'],
                    "to_addr": transaction['to'],
                    "gas_price": transaction['gasPrice'],
                    "chain_id": transaction.get("chainID"),
                    "transaction_log": transaction,
                }
        for transaction_log in block_logs:
            transaction_hash = transaction_log['transactionHash']
            transaction_data = transaction_hash_to_data.get(transaction_hash)
            if not transaction_data:
                continue
            transaction_logs = {"logs": [transaction_log]}
            transfer_events = self._transfer_event(transaction_logs)
            for event in transfer_events:
                args = event['args']
                if args['from'] != NONE_ADDRESS:
                    continue
                data_info = {
                    "from_addr": args['from'],
                    "to": args['to'],
                    "token_id": args['tokenId']
                }
                print(data_info)
            # transfer_single_events = self._transfer_single_event(transaction_logs)
            # for event in transfer_single_events:
            #     args = event['args']
            #     data_info = {
            #         "operator": args['operator'],
            #         "from_addr": args['from'],
            #         "token_id": args['id'],
            #         "value": args['value']
            #     }
            #     print(data_info)
            # transfer_batch_events = self._transfer_batch_event(transaction_logs)
            # if transfer_batch_events:
            #     print('transfer_batch_events', transfer_batch_events)


chain_handler_manager = Handler()


if __name__ == '__main__':
    block_number = 14966303
    handler = Handler()
    asyncio.run(handler.prase_logs(block_number))
