from dot20.dot20 import Dot20
from dotadb.db import DotaDB
from decimal import Decimal

from dot20.dot20_memo_filters import Dot20MemoFilters


class TestDot20():
    def __init__(self) -> None:
        self.db = DotaDB(
            "mysql+mysqlconnector://root:123456@localhost:3306/wjy")
        self.dot20 = Dot20(self.db, valid_ss58_format=42)

    def test_deploy(self):
        try:

            deploy_json1 = {
                "block_num": 273111,
                "block_hash": "0x240079607dbb76c81b974be2256fbf79ed809995a973e1b3b1292c6b5ec4d7d0",
                "extrinsic_hash": "0x9cef5f083d7ed72098bfe6768d65602d8fa196c696bcf3456a4e5a982e45aa7a",
                "extrinsic_index": 2,
                "batchall_index": 0,
                "remark_index": 0,
                "remark_hash": "0x98f4b6890ae25bb9dd975a50f320fc1ab0cfbbd92673a55c9fc58ffac25aedfb",
                "origin": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
                "user": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
                "memo": {
                    "p": "dot-20",
                    "op": "deploy",
                    "mode": "owner",
                    "tick": "dota",
                    "decimal": 18,
                    "start": 273115,
                    "max": 100000,
                    "lim": 10000,
                    "amt": 1000,
                    "end": 283115,
                    "admin": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
                    "memo_remark": "1111"
                }
            }
            deploy_json2 = {
                "block_num": 273111,
                "block_hash": "0x240079607dbb76c81b974be2256fbf79ed809995a973e1b3b1292c6b5ec4d7d0",
                "extrinsic_hash": "0x9cef5f083d7ed72098bfe6768d65602d8fa196c696bcf3456a4e5a982e45aa7a",
                "extrinsic_index": 2,
                "batchall_index": 0,
                "remark_index": 0,
                "remark_hash": "0x98f4b6890ae25bb9dd975a50f320fc1ab0cfbbd92673a55c9fc58ffac25aedfb",
                "origin": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
                "user": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
                "memo": {
                    "p": "dot-20",
                    "op": "deploy",
                    "mode": "owner",
                    "tick": "dot",
                    "decimal": 18,
                    "start": 273115,
                    "max": 10000,
                    "lim": 5000,
                    "amt": 1000,
                    "end": 283115,
                    "admin": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
                    "memo_remark": "1111"
                }
            }
            deploy_json3 = {
                "block_num": 273114,
                "block_hash": "0x240079607dbb76c81b974be2256fbf79ed809995a973e1b3b1292c6b5ec4d7d0",
                "extrinsic_hash": "0x9cef5f083d7ed72098bfe6768d65602d8fa196c696bcf3456a4e5a982e45aa7a",
                "extrinsic_index": 2,
                "batchall_index": 0,
                "remark_index": 0,
                "remark_hash": "0x98f4b6890ae25bb9dd975a50f320fc1ab0cfbbd92673a55c9fc58ffac25aedfb",
                "origin": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
                "user": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
                "memo": {
                    "p": "dot-20",
                    "op": "deploy",
                    "mode": "owner",
                    "tick": "dop",
                    "decimal": 18,
                    "start": 273115,
                    "max": 10000,
                    "lim": 5000,
                    "amt": 1000,
                    "end": 283115,
                    "admin": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
                    "memo_remark": "1111"
                }
            }
            with self.db.session.begin():
                ticks = [self.dot20.deploy(**deploy_json1),
                         #  self.dot20.deploy(**deploy_json2),
                         self.dot20.deploy(**deploy_json3)]
                for tick in ticks:
                    self.db.create_tables_for_new_tick(tick)
        except Exception as e:
            print(f"======DEPLOY_ERR=======\n{e}\n=================")

    def test_mint(self):
        try:
            mint_json1 = {
                "block_num": 273116,
                "block_hash": "0x240079607dbb76c81b974be2256fbf79ed809995a973e1b3b1292c6b5ec4d7d0",
                "extrinsic_hash": "0x9cef5f083d7ed72098bfe6768d65602d8fa196c696bcf3456a4e5a982e45aa7a",
                "extrinsic_index": 2,
                "batchall_index": 0,
                "remark_index": 0,
                "remark_hash": "0x98f4b6890ae25bb9dd975a50f320fc1ab0cfbbd92673a55c9fc58ffac25aedfb",
                "origin": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
                "user": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
                "memo": {
                    "p": "dot-20",
                    "op": "mint",
                    "tick": "dota",
                    "lim": 10000,
                    "to": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
                    "memo_remark": "2222"
                }
            }
            mint_json2 = {
                "block_num": 273117,
                "block_hash": "0x240079607dbb76c81b974be2256fbf79ed809995a973e1b3b1292c6b5ec4d7d0",
                "extrinsic_hash": "0x9cef5f083d7ed72098bfe6768d65602d8fa196c696bcf3456a4e5a982e45aa7a",
                "extrinsic_index": 2,
                "batchall_index": 0,
                "remark_index": 0,
                "remark_hash": "0x98f4b6890ae25bb9dd975a50f320fc1ab0cfbbd92673a55c9fc58ffac25aedfb",
                "origin": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
                "user": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
                "memo": {
                    "p": "dot-20",
                    "op": "mint",
                    "tick": "dota",
                    "lim": 10000,
                    "to": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
                    "memo_remark": "2222"
                }
            }
            with self.db.session.begin():
                self.dot20.mint(**mint_json1)
                self.dot20.mint(**mint_json2)
        except Exception as e:
            print(f"======MINT_ERR=======\n{e}\n=================")

    def test_transfer(self):
        try:
            transfer_json1 = {
                "block_num": 273167,
                "block_hash": "0x240079607dbb76c81b974be2256fbf79ed809995a973e1b3b1292c6b5ec4d7d0",
                "extrinsic_hash": "0x9cef5f083d7ed72098bfe6768d65602d8fa196c696bcf3456a4e5a982e45aa7a",
                "extrinsic_index": 2,
                "batchall_index": 0,
                "remark_index": 0,
                "remark_hash": "0x98f4b6890ae25bb9dd975a50f320fc1ab0cfbbd92673a55c9fc58ffac25aedfb",
                "origin": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
                "user": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
                "memo": {
                    "p": "dot-20",
                    "op": "transfer",
                    "tick": "dota",
                    "amt": 100,
                    "to": "5CiPPseXPECbkjWCa6MnjNokrgYjMqmKndv2rSnekmSK2DjL",
                    "memo_remark": "3333"
                }
            }
            transfer_json2 = {
                "block_num": 273168,
                "block_hash": "0x240079607dbb76c81b974be2256fbf79ed809995a973e1b3b1292c6b5ec4d7d0",
                "extrinsic_hash": "0x9cef5f083d7ed72098bfe6768d65602d8fa196c696bcf3456a4e5a982e45aa7a",
                "extrinsic_index": 2,
                "batchall_index": 0,
                "remark_index": 0,
                "remark_hash": "0x98f4b6890ae25bb9dd975a50f320fc1ab0cfbbd92673a55c9fc58ffac25aedfb",
                "origin": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
                "user": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
                "memo": {
                    "p": "dot-20",
                    "op": "transfer",
                    "tick": "dota",
                    "amt": 1000,
                    "to": "5HGjWAeFDfFCWPsjFQdVV2Msvz2XtMktvgocEZcCj68kUMaw",
                    "memo_remark": "3333"
                }
            }
            with self.db.session.begin():
                self.dot20.transfer(**transfer_json1)
                self.dot20.transfer(**transfer_json2)
        except Exception as e:
            print(f"======TRANSFER_ERR=======\n{e}\n=================")

    def test_approve(self):
        try:
            approve_json = {
                "block_num": 273149,
                "block_hash": "0x240079607dbb76c81b974be2256fbf79ed809995a973e1b3b1292c6b5ec4d7d0",
                "extrinsic_hash": "0x9cef5f083d7ed72098bfe6768d65602d8fa196c696bcf3456a4e5a982e45aa7a",
                "extrinsic_index": 2,
                "batchall_index": 0,
                "remark_index": 0,
                "remark_hash": "0x98f4b6890ae25bb9dd975a50f320fc1ab0cfbbd92673a55c9fc58ffac25aedfb",
                "origin": "5HGjWAeFDfFCWPsjFQdVV2Msvz2XtMktvgocEZcCj68kUMaw",
                "user": "5HGjWAeFDfFCWPsjFQdVV2Msvz2XtMktvgocEZcCj68kUMaw",
                "memo": {
                    "p": "dot-20",
                    "op": "approve",
                    "tick": "dota",
                    "amt": 9999,
                    "to": "5CiPPseXPECbkjWCa6MnjNokrgYjMqmKndv2rSnekmSK2DjL",
                    "memo_remark": "444444"
                }
            }
            with self.db.session.begin():
                self.dot20.approve(**approve_json)
        except Exception as e:
            print(f"======APPROVE_ERR=======\n{e}\n=================")

    def test_transfer_from(self):
        try:
            transfer_json = {
                "block_num": 273175,
                "block_hash": "0x240079607dbb76c81b974be2256fbf79ed809995a973e1b3b1292c6b5ec4d7d0",
                "extrinsic_hash": "0x9cef5f083d7ed72098bfe6768d65602d8fa196c696bcf3456a4e5a982e45aa7a",
                "extrinsic_index": 2,
                "batchall_index": 0,
                "remark_index": 0,
                "remark_hash": "0x98f4b6890ae25bb9dd975a50f320fc1ab0cfbbd92673a55c9fc58ffac25aedfb",
                "origin": "5CiPPseXPECbkjWCa6MnjNokrgYjMqmKndv2rSnekmSK2DjL",
                "user": "5CiPPseXPECbkjWCa6MnjNokrgYjMqmKndv2rSnekmSK2DjL",
                "memo": {
                    "p": "dot-20",
                    "op": "transferFrom",
                    "tick": "dota",
                    "amt": 100,
                    "from": "5HGjWAeFDfFCWPsjFQdVV2Msvz2XtMktvgocEZcCj68kUMaw",
                    "to": "5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty",
                    "memo_remark": ""
                }
            }
            with self.db.session.begin():
                self.dot20.transferFrom(**transfer_json)
        except Exception as e:
            print(f"======TRANSFER_FROM_ERR=======\n{e}\n=================")

    def test_filter(self):

        filter = Dot20MemoFilters(valid_ss58_format=42)
        # (s, m) = filter.is_deploy_memo(memo_data={
        #     "p": "dot-20",
        #     "op": "deploy",
        #     "mode": "normal",
        #     "tick": "dota",
        #     "decimal": 18,
        #     "start": 1,
        #     "max": 111,
        #     "lim": 22,
        #     "amt": 1999999,
        #     "end": 10,
        #     "admin": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
        #     "memo_remark": ""
        # })
        # print(f"{s} ------ {m}")

        (s, m) = filter.is_mint_memo(memo_data={
            "p": "dot-20",
            "op": "mint",
            "tick": "dota",
            "lim": 1,
            # "to": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
            "memo_remark": ""
        })
        print(f"{s} ------ {m}")
        # filter.is_transfer_memo(memo_data={})
        # filter.is_approve_memo(memo_data={})
        # filter.is_memo_memo(memo_data={})
        # (s, m) = filter.is_transferFrom_memo(memo_data={
        #     "p": "dot-20",
        #     "op": "transferFrom",
        #     "tick": "dota",
        #     "amt": 0.000000000000000001,
        #     "from": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
        #     "to": "5CiPPseXPECbkjWCa6MnjNokrgYjMqmKndv2rSnekmSK2DjL"
        # })
        # print(f"{s} ------ {m}")

        # filter.is_memo_merge(op="deploy", memo_data={})


if __name__ == '__main__':
    test = TestDot20()

    # test.test_deploy()
    # test.test_mint()
    # test.test_transfer()
    # test.test_approve()
    # test.test_transfer_from()

    test.test_filter()
