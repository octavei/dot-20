import json
from dotadb.db import DotaDB
from dot20.dot20_memo_filters import Dot20MemoFilters


class Dot20:

    def __init__(self, db: DotaDB, valid_ss58_format=0):
        self.dota_db = db
        self.valid_ss58_format = valid_ss58_format
        self.memo_filters = Dot20MemoFilters(valid_ss58_format)

    def deploy(self, **json_data):
        try:
            (raw_json, memo) = self.fmt_json_data("deploy", **json_data)
        except Exception as e:
            raise e

        tick, start = (memo.get(key) for key in ["tick", "start"])

        if self.get_deploy_info(tick) is not None:
            raise Exception(f"'{tick}' already exist")

        if start < raw_json.get("block_num"):
            raise Exception(
                "The start height must be greater than or equal to the block height")

        deploy_data = {
            "deployer": raw_json.get("user"),
            "block_height": raw_json.get("block_num"),
            "block_hash": raw_json.get("block_hash"),
            "extrinsic_index": raw_json.get("extrinsic_index"),
            "batchall_index": raw_json.get("batchall_index"),
            "remark_index": raw_json.get("remark_index"),
            **memo
        }
        try:
            self.dota_db.insert_deploy_info(deploy_data)
        except Exception as e:
            raise e
        return tick

    def mint(self, **json_data):
        try:
            (raw_json, memo) = self.fmt_json_data("mint", **json_data)
        except Exception as e:
            raise e

        tick = memo.get("tick")
        deploy_info = self.get_deploy_info(tick)
        if deploy_info is None:
            raise Exception(f"{tick}'s deploy does not exist")

        if raw_json.get("block_num") <= deploy_info.get("start"):
            raise Exception(
                "The mint height must be greater than the deployment start height")

        mode = deploy_info.get("mode")
        if mode is None:
            raise Exception("Mode get failure")
        if not mode in ["normal", "fair", "owner"]:
            raise Exception("Unknown mode")

        total = self.get_total_supply(tick)
        if total is None:
            raise Exception(
                "Description mint failed to obtain the total amount")
        if self.is_mint_finish(raw_json.get("block_num"), _total=total, **deploy_info) is True:
            raise Exception("Mint has ended")

        lim = memo.get("lim")

        if mode == "normal":
            deploy_lim = deploy_info.get("lim")
            if deploy_lim is None:
                raise Exception("deploy's lim read failed")
            if lim > deploy_lim:
                raise Exception(
                    "The quantity must not be higher than a single mint quantity")
            if total + lim > deploy_info.get("max"):
                raise Exception("This mint, the total amount overflows")

        if mode == "owner":
            deploy_owner = deploy_info.get("admin")
            if deploy_owner is None:
                raise Exception("deploy's owner read failed")
            if raw_json.get("user") != deploy_owner:
                raise Exception("Only the owner address can be mint")

        mint_data = {
            "singer": raw_json.get("user"),
            "block_height": raw_json.get("block_num"),
            "block_hash": raw_json.get("block_hash"),
            "extrinsic_hash": raw_json.get("extrinsic_hash"),
            "extrinsic_index": raw_json.get("extrinsic_index"),
            "batchall_index": raw_json.get("batchall_index"),
            "remark_index": raw_json.get("remark_index"),
            **memo
        }

        _to = memo.get("to")
        if _to is None:
            _to = raw_json.get("user")

        try:
            self.dota_db.insert_mint_info(tick, [mint_data])
            self.update_user_currency_balance(tick, _to, lim)
        except Exception as e:
            raise e

    def transfer(self, **json_data):
        try:
            (raw_json, memo) = self.fmt_json_data("transfer", **json_data)
        except Exception as e:
            raise e

        if raw_json.get("user") == memo.get("to"):
            raise Exception("You can't transfer money to yourself")

        tick = memo.get("tick")
        deploy_info = self.get_deploy_info(tick)
        if deploy_info is None:
            raise Exception(f"{tick}'s deploy does not exist")

        mode = deploy_info.get("mode")
        if mode is None:
            raise Exception("Mode get failure")
        if not mode in ["normal", "fair", "owner"]:
            raise Exception("Unknown mode")

        if mode in ["normal", "fair"]:
            block_num = raw_json.get("block_num")
            if self.is_mint_finish(block_num, **deploy_info) is False:
                raise Exception("Mint is in progress, unable to transfer")

        transfer_data = {
            "user": raw_json.get("user"),
            "block_height": raw_json.get("block_num"),
            "block_hash": raw_json.get("block_hash"),
            "extrinsic_hash": raw_json.get("extrinsic_hash"),
            "extrinsic_index": raw_json.get("extrinsic_index"),
            "batchall_index": raw_json.get("batchall_index"),
            "remark_index": raw_json.get("remark_index"),
            "amount": memo.get("amt"),
            "from": raw_json.get("user"),
            "to": memo.get("to"),
            "tick": memo.get("tick"),
            "type": 0,
        }
        if memo.get("memo_remark") is not None:
            transfer_data["memo_remark"] = memo.get("memo_remark")

        try:
            self.update_user_currency_balance(
                tick, raw_json.get("user"), -memo.get("amt"))
            self.update_user_currency_balance(
                tick, memo.get("to"), memo.get("amt"))
            self.dota_db.insert_transfer_info(tick, [transfer_data])
        except Exception as e:
            raise e

    def approve(self, **json_data):
        try:
            (raw_json, memo) = self.fmt_json_data("approve", **json_data)
        except Exception as e:
            raise e

        if raw_json.get("user") == memo.get("to"):
            raise Exception("You can't approve to yourself")

        tick = memo.get("tick")
        deploy_info = self.get_deploy_info(tick)
        if deploy_info is None:
            raise Exception(f"{tick}'s deploy does not exist")

        if self.get_user_currency_balance(tick, raw_json.get("user")) is None:
            raise Exception("The approve user does not exist")

        approve_data = {
            "user": memo.get("to"),
            "from_address": raw_json.get("user"),
            "tick": memo.get("tick"),
            "amount": memo.get("amt"),
        }

        approve_history_data = {
            "user": memo.get("to"),
            "from": raw_json.get("user"),
            "tick": memo.get("tick"),
            "amount": memo.get("amt"),
            "block_height": raw_json.get("block_num"),
            "block_hash": raw_json.get("block_hash"),
            "extrinsic_index": raw_json.get("extrinsic_index"),
            "batchall_index": raw_json.get("batchall_index"),
            "remark_index": raw_json.get("remark_index"),
        }
        if memo.get("memo_remark") is not None:
            approve_history_data["memo_remark"] = memo.get("memo_remark")

        try:
            self.dota_db.insert_or_update_user_approve(tick, [approve_data])
            self.dota_db.insert_approve_history(tick, [approve_history_data])
        except Exception as e:
            raise e

    def transferFrom(self, **json_data):
        try:
            (raw_json, memo) = self.fmt_json_data("transferFrom", **json_data)
        except Exception as e:
            raise e

        if raw_json.get("user") == memo.get("from"):
            raise Exception("The approved person is himself")

        tick = memo.get("tick")
        deploy_info = self.get_deploy_info(tick)
        if deploy_info is None:
            raise Exception(f"{tick}'s deploy does not exist")

        mode = deploy_info.get("mode")
        if mode is None:
            raise Exception("Mode get failure")
        if not mode in ["normal", "fair", "owner"]:
            raise Exception("Unknown mode")

        if mode in ["normal", "fair"]:
            block_num = raw_json.get("block_num")
            if self.is_mint_finish(block_num, **deploy_info) is False:
                raise Exception("Mint is in progress, unable to transfer")

        approve = self.get_user_approve(
            memo.get("tick"), raw_json.get("user"), memo.get("from"))
        if approve is None:
            raise Exception("Transfers not approved")
        if memo.get("amt") > approve.get("amount"):
            raise Exception(
                "The transfer amount is greater than the authorized amount")

        transfer_from_data = {
            "user": raw_json.get("user"),
            "block_height": raw_json.get("block_num"),
            "block_hash": raw_json.get("block_hash"),
            "extrinsic_hash": raw_json.get("extrinsic_hash"),
            "extrinsic_index": raw_json.get("extrinsic_index"),
            "batchall_index": raw_json.get("batchall_index"),
            "remark_index": raw_json.get("remark_index"),
            "amount": memo.get("amt"),
            "from": memo.get("from"),
            "to": memo.get("to"),
            "tick": memo.get("tick"),
            "type": 1,
        }
        if memo.get("memo_remark") is not None:
            transfer_from_data["memo_remark"] = memo.get("memo_remark")

        try:
            self.update_user_currency_balance(
                tick, memo.get("from"), -memo.get("amt"))
            self.update_user_currency_balance(
                tick, memo.get("to"), memo.get("amt"))
            self.dota_db.insert_transfer_info(tick, [transfer_from_data])
            approve["amount"] -= memo.get("amt")
            self.dota_db.insert_or_update_user_approve(tick, [approve])

        except Exception as e:
            raise e

    def get_deploy_info(self, tick: str):
        try:
            results = self.dota_db.get_deploy_info(tick)
            if len(results) == 0:
                return None
            else:
                dicts = [dict(item._mapping) for item in results]
                return dicts[0]
        except Exception as e:
            raise e

    def get_total_supply(self, tick: str):
        try:
            result = self.dota_db.get_total_supply(tick)
            if result is not None and result[0] is not None:
                return result[0]
            else:
                return 0
        except Exception as e:
            raise e

    def get_user_currency_balance(self, tick: str, user: str):
        try:
            result = self.dota_db.get_user_currency_balance(
                tick, user)
            if result is not None:
                return dict(result._mapping)
            else:
                return None
        except Exception as e:
            raise e

    def update_user_currency_balance(self, tick: str, user: str, amount: any):
        try:
            user_currency_balance = self.get_user_currency_balance(
                tick, user)
            if user_currency_balance is None:
                user_currency_balance = {
                    "tick": tick, "user": user, "balance": 0}
            balance = user_currency_balance.get("balance")
            if amount < 0 and balance + amount < 0:
                raise Exception(f"{user} insufficient balance")
            user_currency_balance["balance"] += amount
            self.dota_db.insert_or_update_user_currency_balance(
                tick, [user_currency_balance])
        except Exception as e:
            raise e

    def is_mint_finish(self, block_num, _total=None, **deploy_info):
        mode, max, tick, end = (deploy_info.get(key)
                                for key in ['mode', 'max', 'tick', 'end'])
        if mode == "normal":
            if _total is not None:
                total = _total
            else:
                total = self.get_total_supply(tick)
            if max is not None and total is not None and total >= max:
                return True
        if mode == "fair":
            if end is not None and block_num is not None and block_num > end:
                return True
        return False

    def get_user_approve(self, tick: str, user: str, _from: str):
        try:
            result = self.dota_db.get_user_approve_amount(tick, user, _from)
            if result is not None:
                return dict(result._mapping)
            else:
                return None
        except Exception as e:
            raise e

    def fmt_json_data(self, op: str, **data) -> (dict, dict):
        (is_raw, raw_msg) = self.memo_filters.is_raw_json(json_data=data)
        if is_raw is not True:
            raise Exception(f"{raw_msg}")

        memo = data.get("memo")
        if isinstance(memo, str):
            memo_json = json.loads(memo)
        else:
            memo_json = memo

        (is_memo, memo_msg) = self.memo_filters.is_memo_merge(
            op, memo_data=memo_json)
        if is_memo is not True:
            raise Exception(f"{memo_msg}")

        del data["memo"]

        return data, dict(memo_json)
