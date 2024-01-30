import json
import re
from substrateinterface import keypair
from dotadb.db import DotaDB


class Dot20:

    def __init__(self, db: DotaDB):
        self.dota_db = db
        self.p = "dot-20"

    # 部署
    def deploy(self, **json_data):
        try:
            (json, memo) = self._fmt_json_data("deploy", **json_data)
        except Exception as e:
            raise e

        # 验证tick
        tick = memo.get("tick")
        tick_pattern = r'^[a-zA-Z]{3,6}$'
        if tick is None:
            raise Exception("tick is empty")
        elif not re.match(tick_pattern, tick):
            raise Exception("3-6 letters are case insensitive")
        elif self.get_deploy_info(tick) is not None:
            raise Exception(f"'{tick}' already exist")

        # 验证decimal 数字0-18
        decimal = memo.get("decimal")
        if decimal is None:
            memo["decimal"] = 18
        elif not (0 <= decimal <= 18):
            raise Exception("Only digits 0-18 are allowed")

        # 获取模式
        mode = memo.get("mode")
        if mode is None:
            raise Exception("Mode get failure")
        if not mode in ["normal", "fair", "owner"]:
            raise Exception("Unknown mode")

        # 判断start与区块高度
        start = memo.get("start")
        if start is None:
            raise Exception("Start get failure")
        block_num = json.get("block_num")
        if block_num is None:
            raise Exception("Block get failure")
        if start < block_num:
            raise Exception(
                "start must be equal to or later than the deployment block height")

        # 常规模式（normal，单次mint获得固定数量铭文）
        # <start, max, lim>
        if mode == "normal":
            max, lim = (memo.get(key) for key in ['max', 'lim'])
            if max is None or lim is None:
                raise Exception("The max or lim read failed")
            if lim == 0:
                raise Exception("lim is 0")
            if max == 0:
                raise Exception("max is 0")
            if max > 10 ** 32:
                raise Exception("max Max is 10^32")
            if lim > max:
                raise Exception(
                    "The amount of lim cast at a time cannot be higher than max")

        # 公平模式（fair，区块内平分铭文）
        # <amt, start, end>
        if mode == "fair":
            amt, end = (memo.get(key) for key in ['amt', 'end'])
            if amt is None or end is None:
                raise Exception("amt or end read failed")
            if amt*(end-start+1) > 10 ** 32:
                raise Exception(
                    "amt*(end-start+1) must not be higher than 10^32")

        # 控制者模式（owner，仅admin可以铸造铭文）
        # <admin>
        if mode == "owner":
            admin = memo.get("admin")
            if admin is None:
                raise Exception("admin read failed")
            if self.is_valid_ss58_address(admin) is False:
                raise Exception(
                    "admin does not comply with the ss58 specifications")

        deploy_data = {
            "deployer": json.get("user"),
            "block_height": json.get("block_num"),
            "block_hash": json.get("block_hash"),
            "extrinsic_index": json.get("extrinsic_index"),
            "batchall_index": json.get("batchall_index"),
            "remark_index": json.get("remark_index"),
            **memo
        }
        try:
            self.dota_db.create_tables_for_new_tick(tick)
            self.dota_db.insert_deploy_info(deploy_data)
        except Exception as e:
            raise e

    # 铸造
    def mint(self, **json_data):
        try:
            (json, memo) = self._fmt_json_data("mint", **json_data)
        except Exception as e:
            raise e

        # 获取deploy info 验证tick是否存在
        tick = memo.get("tick")
        if tick is None:
            raise Exception("tick is empty")
        deploy_info = self.get_deploy_info(tick)
        if deploy_info is None:
            raise Exception(f"{tick}'s deploy does not exist")

        # mint是否结束
        block_num = json.get("block_num")
        if block_num is None:
            raise Exception("Block read failure")
        if self.is_mint_finish(block_num, **deploy_info) is True:
            raise Exception("Mint has ended")

        # to是否符合ss58
        to = memo.get("to")
        if to is None:
            raise Exception("to read failed")
        if self.is_valid_ss58_address(to) is False:
            raise Exception(
                "The address does not comply with the ss58 specification")

        # 获取模式
        mode = deploy_info.get("mode")
        if mode is None:
            raise Exception("Mode get failure")
        if not mode in ["normal", "fair", "owner"]:
            raise Exception("Unknown mode")

        # normal
        if mode == "normal":
            lim = memo.get("lim")
            if lim is None:
                raise Exception("lim read failed")
            deploy_lim = deploy_info.get("lim")
            if deploy_lim is None:
                raise Exception("deploy's lim read failed")
            if lim > deploy_lim:
                raise Exception(
                    "The quantity must not be higher than a single mint quantity")

        # owner
        if mode == "owner":
            user = json.get("user")
            if user is None:
                raise Exception("user read failed")
            deploy_owner = deploy_info.get("admin")
            if deploy_owner is None:
                raise Exception("deploy's owner read failed")
            if user != deploy_owner:
                raise Exception("Only the owner address can be mint")

        mint_data = {
            "singer": json.get("user"),
            "block_height": json.get("block_num"),
            "block_hash": json.get("block_hash"),
            "extrinsic_index": json.get("extrinsic_index"),
            "batchall_index": json.get("batchall_index"),
            "remark_index": json.get("remark_index"),
            **memo
        }
        try:
            self.dota_db.insert_mint_info(tick, [mint_data])
            user_currency_balance = self.get_user_currency_balance(
                tick, json.get("user"))
            if user_currency_balance is not None:
                self.dota_db.insert_or_update_user_currency_balance(
                    tick, user_currency_balance)
        except Exception as e:
            raise e

    # 验证address是否符合ss58规范
    def is_valid_ss58_address(_, address: str) -> bool:
        try:
            keypair.ss58_decode(address)
            return True
        except ValueError:
            return False

    # 获取deploy_info，并判断tick是否存在
    def get_deploy_info(self, tick: str):
        try:
            tbl_result = self.dota_db.get_deploy_info(tick)
            if len(tbl_result) == 0:
                return None
            else:
                return tbl_result[0]
        except Exception:
            return None

    # 获取get_total_supply,已mint总量
    def get_total_supply(self, tick: str):
        try:
            tbl_result = self.dota_db.get_total_supply(tick)
            if len(tbl_result) == 0:
                return None
            else:
                return tbl_result[0]
        except Exception:
            return None

    # 获取用户余额
    def get_user_currency_balance(self, tick: str, user: str):
        try:
            tbl_result = self.dota_db.get_user_currency_balance(
                tick, user)
            if len(tbl_result) == 0:
                return None
            else:
                return tbl_result[0]
        except Exception:
            return None

    # 验证mint是否结束
    def is_mint_finish(self, block_num, **deploy_info) -> bool:
        mode, max, tick = (deploy_info.get(key)
                           for key in ['mode', 'max', 'tick'])
        if mode == "normal":
            total = self.get_total_supply(tick)
            if max is not None and total is not None and total > max:
                return True
        if mode == "fair":
            end = deploy_info.get("end")
            if end is not None and block_num is not None and block_num > end:
                return True

        return False

    # 格式化json_data
    def _fmt_json_data(self, op: str, **data) -> (dict, dict):
        try:
            data["memo"] = json.loads(data.get("memo"))
        except json.JSONDecodeError:
            data["memo"] = None

        memo = data.get("memo")
        if memo is None:
            raise Exception("Failed to obtain memo")
        if memo.get("p") != self.p:
            raise Exception("Non dot-20 data")
        if memo.get("op") != op:
            raise Exception(f"Please pass in the json data for '{op}'")

        return data, memo
