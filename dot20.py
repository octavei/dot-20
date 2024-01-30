import json
import re
from substrateinterface import keypair


class Dot20:

    # 部署
    def deploy(self, **json_data) -> dict:
        try:
            (json, memo) = self._fmt_json_data(op="deploy", **json_data)
        except Exception as e:
            raise e

        # 验证tick
        tick = memo.get("tick")
        tick_pattern = r'^[a-zA-Z]{3,6}$'
        if tick is None:
            raise Exception("tick is empty")
        elif not re.match(tick_pattern, tick):
            raise Exception("3-6 letters are case insensitive")
        elif self.get_deploy_info(tick=tick) is not None:
            raise Exception(f"'{tick}' already exist")

        # 验证decimal 数字0-18
        decimal = memo.get("decimal")
        if decimal is None:
            memo["decimal"] = 18
        elif not (0 <= decimal <= 18):
            raise Exception("仅允许数字0-18")

        # 获取模式
        mode = memo.get("mode")
        if mode is None:
            raise Exception("模式读取失败")
        if not mode in ["normal", "fair", "owner"]:
            raise Exception("未知模式")

        # 判断start与区块高度
        start = memo.get("start")
        if start is None:
            raise Exception("读取start失败")
        block_num = json.get("block_num")
        if block_num is None:
            raise Exception("读取区块失败")
        if start < block_num:
            raise Exception("start必须等于或晚于部署区块高度")

        # 常规模式（normal，单次mint获得固定数量铭文）
        # <start, max, lim>
        if mode == "normal":
            max, lim = (memo.get(key) for key in ['max', 'lim'])
            if max is None or lim is None:
                raise Exception("常规模式:max或lim读取失败")
            if lim == 0:
                raise Exception("normal: lim is 0")
            if max == 0:
                raise Exception("normal: max is 0")
            if max > 10 ** 32:
                raise Exception("常规模式:max最大值为10^32")
            if lim > max:
                raise Exception("常规模式:单次lim铸造数量不能高于max")

        # 公平模式（fair，区块内平分铭文）
        # <amt, start, end>
        if mode == "fair":
            amt, end = (memo.get(key) for key in ['amt', 'end'])
            if amt is None or end is None:
                raise Exception("公平模式:amt或end读取失败")
            if amt*(end-start+1) > 10 ** 32:
                raise Exception("公平模式:amt*(end-start+1)不得高于10^32")

        # 控制者模式（owner，仅admin可以铸造铭文）
        # <admin>
        if mode == "owner":
            admin = memo.get("admin")
            if admin is None:
                raise Exception("控制者模式:admin读取失败")
            if self.is_valid_ss58_address(admin) is False:
                raise Exception("控制者模式:admin不符合ss58规范")

        return {
            "deployer": json.get("user"),
            "block_height": json.get("block_num"),
            "block_hash": json.get("block_hash"),
            "extrinsic_index": json.get("extrinsic_index"),
            "batchall_index": json.get("batchall_index"),
            "remark_index": json.get("remark_index"),
            **memo
        }

    # 铸造
    def mint(self, **json_data) -> dict:
        try:
            (json, memo) = self._fmt_json_data(op="mint", **json_data)
        except Exception as e:
            raise e

        # 获取deploy info 验证tick是否存在
        tick = memo.get("tick")
        if tick is None:
            raise Exception("tick is empty")
        deploy_info = self.get_deploy_info(tick=tick)
        if deploy_info is None:
            raise Exception(f"{tick}'s deploy does not exist")

        # mint是否结束
        block_num = json.get("block_num")
        if block_num is None:
            raise Exception("读取区块失败")
        if self.is_mint_finish(block_num=block_num, **deploy_info) is True:
            raise Exception("Mint已结束")

        # to是否符合ss58
        to = memo.get("to")
        if to is None:
            raise Exception("to字段读取失败")
        if self.is_valid_ss58_address(to) is False:
            raise Exception("地址不符合ss58规范")

        # TODO:normal/fair

        # TODO:owner

        return {
            "singer": json.get("user"),
            "block_height": json.get("block_num"),
            "block_hash": json.get("block_hash"),
            "extrinsic_index": json.get("extrinsic_index"),
            "batchall_index": json.get("batchall_index"),
            "remark_index": json.get("remark_index"),
            **memo
        }

    # 验证address是否符合ss58规范
    def is_valid_ss58_address(_, address: str) -> bool:
        try:
            keypair.ss58_decode(address)
            return True
        except ValueError:
            return False

    # 获取deploy_info，并判断tick是否存在
    def get_deploy_info(_, tick: str) -> None | dict:
        # TODO:从数据库获取deploy信息
        return None

    # 验证mint是否结束
    def is_mint_finish(_, block_num, **deploy_info) -> bool:
        mode = deploy_info.get("mode")
        if mode == "normal":
            max = deploy_info.get("max")
            # TODO:获取mint余量
            residual = 100000
            if max is not None and residual > 0:
                return True
        if mode == "fair":
            end = deploy_info.get("end")
            if end is not None and block_num is not None and end > block_num:
                return True

        return False

    # 格式化json_data
    def _fmt_json_data(_, op: str, **data) -> (dict, dict):
        try:
            data["memo"] = json.loads(data.get("memo"))
        except json.JSONDecodeError:
            data["memo"] = None

        memo = data.get("memo")
        if memo is None:
            raise Exception("memo获取失败")
        if memo.get("op") != op:
            raise Exception(f"请传入'{op}'的json数据")

        return data, memo
