import json
from dotadb.db import DotaDB
from dot20.dot20_memo_filters import Dot20MemoFilters


class Dot20:

    def __init__(self, db: DotaDB, valid_ss58_format=0):
        self.dota_db = db
        self.valid_ss58_format = valid_ss58_format
        self.memo_filters = Dot20MemoFilters(valid_ss58_format)

    # 部署
    def deploy(self, **json_data):
        try:
            (raw_json, memo) = self._fmt_json_data("deploy", **json_data)
        except Exception as e:
            raise e

        # 解构所有需要的memo数据
        data_keys = ["tick", "mode",
                     "start", "max", "lim", "amt", "end"]
        tick, mode, start, max, lim, amt, end = (memo.get(key)
                                                 for key in data_keys)

        # 验证tick是否已经存在
        if self.get_deploy_info(tick) is not None:
            raise Exception(f"'{tick}' already exist")

        # 判断start高度需要大于等于区块高度
        if start < raw_json.get("block_num"):
            raise Exception(
                "start must be equal to or later than the deployment block height")

        # 1.常规模式（normal，单次mint获得固定数量铭文）
        # <start, max, lim>
        if mode == "normal":
            if lim == 0:
                raise Exception("lim is 0")
            if max == 0:
                raise Exception("max is 0")
            if lim > max:
                raise Exception(
                    "The amount of lim cast at a time cannot be higher than max")

        # 2.公平模式（fair，区块内平分铭文）
        # <amt, start, end>
        if mode == "fair":
            if amt*(end-start+1) > 10 ** 32:
                raise Exception(
                    "amt*(end-start+1) must not be higher than 10^32")

        # 3.控制者模式（owner，仅admin可以铸造铭文）
        # 地址必须性和可用性已经在memo_filter判定

        deploy_data = {
            "deployer": raw_json.get("user"),
            "block_height": raw_json.get("block_num"),
            "block_hash": raw_json.get("block_hash"),
            "extrinsic_index": raw_json.get("extrinsic_index"),
            "batchall_index": raw_json.get("batchall_index"),
            "remark_index": raw_json.get("remark_index"),
            **memo
        }
        self.dota_db.create_tables_for_new_tick(tick)
        self.dota_db.session.commit()
        try:
            with self.dota_db.session.begin():
                self.dota_db.insert_deploy_info(deploy_data)
            self.dota_db.session.commit()
        except Exception as e:
            raise e

    # 铸造
    def mint(self, **json_data):
        try:
            (raw_json, memo) = self._fmt_json_data("mint", **json_data)
        except Exception as e:
            raise e

        # 验证tick是否存在并且获取deployInfo
        tick = memo.get("tick")
        deploy_info = self.get_deploy_info(tick)
        if deploy_info is None:
            raise Exception(f"{tick}'s deploy does not exist")

        # 获取deploy中的模式
        mode = deploy_info.get("mode")
        if mode is None:
            raise Exception("Mode get failure")
        if not mode in ["normal", "fair", "owner"]:
            raise Exception("Unknown mode")

        # 判断mint是否结束
        if self.is_mint_finish(raw_json.get("block_num"), **deploy_info) is True:
            raise Exception("Mint has ended")

        # lim是业务层根据模式计算后的值,可用于用户资产更新
        lim = memo.get("lim")
        if lim is None:
            raise Exception("lim is none")

        # 1.normal
        if mode == "normal":
            deploy_lim = deploy_info.get("lim")
            if deploy_lim is None:
                raise Exception("deploy's lim read failed")
            if lim > deploy_lim:
                raise Exception(
                    "The quantity must not be higher than a single mint quantity")

        # 2.fair区块高度判断，在判断是否mint结束完成

        # 3.owner
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
        try:
            with self.dota_db.session.begin():
                self.dota_db.insert_mint_info(tick, [mint_data])
            self.dota_db.session.commit()
            self.update_user_currency_balance(
                tick, raw_json.get("user"), lim)
        except Exception as e:
            raise e

    # 转账
    def transfer(self, **json_data):
        try:
            (raw_json, memo) = self._fmt_json_data("transfer", **json_data)
        except Exception as e:
            raise e

        # 不能给自己转账
        if raw_json.get("user") == memo.get("to"):
            raise Exception("You can't transfer money to yourself")

        # amt需要大于0
        if memo.get("amt") <= 0:
            raise Exception(
                "The number of transfers is less than or equal to 0")

        # 验证tick是否存在并获取deploy info
        tick = memo.get("tick")
        deploy_info = self.get_deploy_info(tick)
        if deploy_info is None:
            raise Exception(f"{tick}'s deploy does not exist")

        # 获取模式
        mode = deploy_info.get("mode")
        if mode is None:
            raise Exception("Mode get failure")
        if not mode in ["normal", "fair", "owner"]:
            raise Exception("Unknown mode")

        # normal/fair模式mint中无法转账
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

        try:

            # 1.from扣款[余额异常会抛异常]
            self.update_user_currency_balance(
                tick, raw_json.get("user"), -memo.get("amt"))
            # 2.to进账
            self.update_user_currency_balance(
                tick, memo.get("to"), memo.get("amt"))
            # 3.增加记录
            with self.dota_db.session.begin():
                self.dota_db.insert_transfer_info(tick, [transfer_data])
            self.dota_db.session.commit()
        except Exception as e:
            raise e

    # 授权
    def approve(self, **json_data):
        try:
            (raw_json, memo) = self._fmt_json_data("approve", **json_data)
        except Exception as e:
            raise e

        # 不能给自己授权
        if raw_json.get("user") == memo.get("to"):
            raise Exception("You can't approve to yourself")

        # 验证tick是否存在并获取deploy info
        tick = memo.get("tick")
        deploy_info = self.get_deploy_info(tick)
        if deploy_info is None:
            raise Exception(f"{tick}'s deploy does not exist")

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

        try:
            # 1.更新approve
            self.dota_db.insert_or_update_user_approve(tick, [approve_data])
            self.dota_db.session.commit()

            # 2.新增记录
            self.dota_db.insert_approve_history(tick, [approve_history_data])
            self.dota_db.session.commit()
        except Exception as e:
            raise e

    # 授权转账
    def transferFrom(self, **json_data):
        try:
            (raw_json, memo) = self._fmt_json_data("transferFrom", **json_data)
        except Exception as e:
            raise e

        # 不能给自己转账
        if raw_json.get("user") == memo.get("to"):
            raise Exception("You can't transfer money to yourself")

        # amt需要大于0
        if memo.get("amt") <= 0:
            raise Exception(
                "The number of transfers is less than or equal to 0")

        # 验证tick是否存在并获取deploy info
        tick = memo.get("tick")
        deploy_info = self.get_deploy_info(tick)
        if deploy_info is None:
            raise Exception(f"{tick}'s deploy does not exist")

        # 获取模式
        mode = deploy_info.get("mode")
        if mode is None:
            raise Exception("Mode get failure")
        if not mode in ["normal", "fair", "owner"]:
            raise Exception("Unknown mode")

        # normal/fair模式mint中无法转账
        if mode in ["normal", "fair"]:
            block_num = raw_json.get("block_num")
            if self.is_mint_finish(block_num, **deploy_info) is False:
                raise Exception("Mint is in progress, unable to transfer")

        # 是否已经授权
        if self.get_user_approve_amount(memo.get("tick"), memo.get("to"), memo.get("from")) <= 0:
            raise Exception("Unauthorized transfers")

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

        try:

            # 1.from扣款[余额异常会抛异常]
            self.update_user_currency_balance(
                tick, memo.get("from"), -memo.get("amt"))
            # 2.to进账
            self.update_user_currency_balance(
                tick, memo.get("to"), memo.get("amt"))
            # 3.增加记录
            with self.dota_db.session.begin():
                self.dota_db.insert_transfer_info(tick, [transfer_from_data])
            self.dota_db.session.commit()
        except Exception as e:
            raise e

    # 判断tick是否存在 / 获取deploy_info
    def get_deploy_info(self, tick: str):
        try:
            results = self.dota_db.get_deploy_info(tick)
            self.dota_db.session.commit()
            if len(results) == 0:
                return None
            else:
                dicts = [dict(item._mapping) for item in results]
                return dicts[0]
        except Exception as e:
            print(e)
            return None

    # 获取get_total_supply,已mint总量
    def get_total_supply(self, tick: str):
        try:
            result = self.dota_db.get_total_supply(tick)
            self.dota_db.session.commit()
            if result is not None:
                return result[0]
            else:
                return None
        except Exception:
            return None

    # 获取用户余额
    def get_user_currency_balance(self, tick: str, user: str):
        try:
            result = self.dota_db.get_user_currency_balance(
                tick, user)
            self.dota_db.session.commit()
            if result is not None:
                return dict(result._mapping)
            else:
                return {"tick": tick, "user": user, "balance": 0}
        except Exception:
            return None

    # 更新账户余额
    def update_user_currency_balance(self, tick: str, user: str, amount: any):
        try:
            user_currency_balance = self.get_user_currency_balance(
                tick, user)
            balance = user_currency_balance.get("balance")
            if balance + amount < 0:
                raise Exception(f"{user} Insufficient balance")
            if user_currency_balance is not None:
                user_currency_balance["balance"] += amount
                with self.dota_db.session.begin():
                    self.dota_db.insert_or_update_user_currency_balance(
                        tick, [user_currency_balance])
                self.dota_db.session.commit()
        except Exception as e:
            raise e

    # 验证mint是否结束
    def is_mint_finish(self, block_num, **deploy_info):
        mode, max, tick, end = (deploy_info.get(key)
                                for key in ['mode', 'max', 'tick', 'end'])
        if mode == "normal":
            total = self.get_total_supply(tick)
            if max is not None and total is not None and total > max:
                return True
        if mode == "fair":
            if end is not None and block_num is not None and block_num > end:
                return True
        return False

    # 获取to地址的授权量
    def get_user_approve_amount(self, tick: str, to: str, _from: str):
        try:
            result = self.dota_db.get_user_approve_amount(tick, to, _from)
            self.dota_db.session.commit()
            if result is not None:
                return result[0]
            else:
                return -1
        except Exception:
            return -1

    # 格式化json_data
    def _fmt_json_data(self, op: str, **data) -> (dict, dict):
        # 检查原json格式
        (is_raw, raw_msg) = self.memo_filters.is_raw_json(json_data=data)
        if is_raw is not True:
            raise Exception(f"{raw_msg}")

        # 检查memo json格式
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
