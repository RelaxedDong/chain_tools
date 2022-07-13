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

from api.db_manager import project_info_db, mint_record_db
from manager.opensea_manager import get_opensea_collection_info
from utils.function_cache import async_func_cache
from utils.redis_db.redis_clients import RedisUtil

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

web3_provider = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{MAIN_NET_PROJECT_ID}'))


class Handler(object):

    def __init__(self):
        self.w3 = web3_provider
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
                collection_info = await get_opensea_collection_info(event['address'])
                if not collection_info:
                    continue
                collection = collection_info['collection']
                project_data = {
                    "opensea_url": f"https://opensea.io/collection/{collection['slug']}",
                    "name": collection_info['name'],
                    "opensea_image_url": collection_info['image_url'],
                    "external_url": collection.get("external_url") or "",
                    "discord_url": collection.get("discord_url") or "",
                    "created_date": collection['created_date'],
                    "slug": collection['slug'],
                    "contract_address": collection_info['address']
                }
                twitter_username = collection.get("twitter_username") or ""
                if twitter_username:
                    project_data['twitter_url'] = f"https://twitter.com/{twitter_username}"

                # 创建项目信息
                project_id = await project_info_db.create_project(project_data)
                # 创建mint纪录信息
                # 如果mint过只需要增加mint的数量就好了
                update_filter = {"user_address": args['to'], "contract_address": collection_info['address']}
                exist_record = await mint_record_db.find_self_one(update_filter)
                if not exist_record:
                    await mint_record_db.insert_self({
                        "project_id": project_id,
                        "contract_address": collection_info['address'],
                        "user_address": args['to'],
                        "minted_cnt": 1,
                    })
                else:
                    await mint_record_db.update_self(update_filter, {"$inc": {"minted_cnt": 1}})

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

    @async_func_cache(ttl=60, build_without_params=True)
    async def get_latest_block_number(self):
        return web3_provider.eth.get_block_number()

    async def record_process_block(self, block_number):
        return await RedisUtil.incr("current_block_number", block_number)

    async def get_current_process_block(self):
        return await RedisUtil.get("current_block_number") or None


chain_handler_manager = Handler()


async def main():
    while True:
        new_east_block = await chain_handler_manager.get_latest_block_number()
        current_block = await chain_handler_manager.get_current_process_block()
        if not current_block:
            current_block = await chain_handler_manager.record_process_block(new_east_block)
        current_block = int(current_block)
        if current_block > new_east_block:
            print('(sleep 10.) wait for next block comming...')
            await asyncio.sleep(10)
            continue

        await chain_handler_manager.prase_logs(current_block)
        await chain_handler_manager.record_process_block(1)
        print('(sleep 10.) ready to process next block...')
        await asyncio.sleep(10)


if __name__ == '__main__':
    asyncio.run(main())
