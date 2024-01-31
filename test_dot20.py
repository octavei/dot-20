import unittest
from dot20.dot20 import Dot20
from dotadb.db import DotaDB
from decimal import Decimal


class TestDot20(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        db = DotaDB("mysql+mysqlconnector://root:123456@localhost:3306/wjy")
        self.dot20 = Dot20(db)
        super().__init__(methodName)

    # def test_deploy(self):
    #     try:

    #         deploy_json = {
    #             "block_num": 273111,
    #             "block_hash": "0x240079607dbb76c81b974be2256fbf79ed809995a973e1b3b1292c6b5ec4d7d0",
    #             "extrinsic_hash": "0x9cef5f083d7ed72098bfe6768d65602d8fa196c696bcf3456a4e5a982e45aa7a",
    #             "extrinsic_index": 2,
    #             "batchall_index": 0,
    #             "remark_index": 0,
    #             "remark_hash": "0x98f4b6890ae25bb9dd975a50f320fc1ab0cfbbd92673a55c9fc58ffac25aedfb",
    #             "origin": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
    #             "user": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
    #             "memo": "{\"p\": \"dot-20\", \"op\": \"deploy\",\"mode\": \"normal\", \"tick\": \"dota\",\"decimal\": 18, \"start\": 273115, \"max\": 10000, \"lim\": 5000, \"amt\": 1000, \"end\": 283115, \"admin\": \"15Dfr41oVWMhqKD6qL1pj6gZEE6vzNQ9RH8ShefFsoReVWsi\"}"
    #         }
    #         self.dot20.deploy(**deploy_json)
    #     except Exception as e:
    #         print(f"DEPLOY_ERR::{e}\n")

    def test_mint(self):
        try:
            mint_json = {
                "block_num": 273147,
                "block_hash": "0x240079607dbb76c81b974be2256fbf79ed809995a973e1b3b1292c6b5ec4d7d0",
                "extrinsic_hash": "0x9cef5f083d7ed72098bfe6768d65602d8fa196c696bcf3456a4e5a982e45aa7a",
                "extrinsic_index": 2,
                "batchall_index": 0,
                "remark_index": 0,
                "remark_hash": "0x98f4b6890ae25bb9dd975a50f320fc1ab0cfbbd92673a55c9fc58ffac25aedfb",
                "origin": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuZy",
                "user": "5FTcboVf86hubC8YJjo8LjK3c2uq2rWpK7idnrfazi4ePuKK",
                "memo": "{\"p\": \"dot-20\", \"op\": \"mint\",\"tick\": \"dota\", \"lim\": 5000, \"to\": \"15Dfr41oVWMhqKD6qL1pj6gZEE6vzNQ9RH8ShefFsoReVWsi\"}"
            }
            self.dot20.mint(**mint_json)
        except Exception as e:
            print(f"MINT_ERR::{e}\n")


if __name__ == '__main__':
    unittest.main()
