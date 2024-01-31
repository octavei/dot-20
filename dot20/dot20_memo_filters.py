import json
import jsonschema
from jsonschema import Draft7Validator, validators
from jsonschema.exceptions import ValidationError
from scalecodec.types import is_valid_ss58_address


def is_address(validator, value, instance, schema):
    if is_valid_ss58_address(instance, 0) is not True:
        raise ValidationError(f"'{value}' Invalid address")


def is_json_str(validator, value, instance, schema):
    try:
        json.loads(instance)
    except json.JSONDecodeError as e:
        raise ValidationError(f"{e.msg}")


class Dot20MemoFilters:

    def __init__(self) -> None:
        self._schemas = {
            "deploy": {
                "type": "object",
                "properties": {
                    "p": {
                        "enum": ["dot-20"]
                    },
                    "op": {
                        "enum": ["deploy"]
                    },
                    "tick": {
                        "type": "string",
                        "pattern": "^[a-zA-Z]{3,6}$"
                    },
                    "decimal": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 18,
                        "default": 18
                    },
                    "mode": {
                        "enum": ["normal", "fair", "owner"]
                    },
                    "amt": {
                        "type": "number",
                        "multipleOf": 1e-18,
                        "minimum": 0,
                        "maximum": 10**32,
                    },
                    "start": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10**32,
                    },
                    "end": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10**32,
                    },
                    "max": {
                        "type": "number",
                        "multipleOf": 1e-18,
                        "minimum": 0,
                        "maximum": 10**32,
                    },
                    "lim": {
                        "type": "number",
                        "multipleOf": 1e-18,
                        "minimum": 0,
                        "maximum": 10**32,
                    },
                    "admin": {
                        "type": "string",
                    },
                },
                "required": ["p", "op", "tick", "mode"],
                "allOf": [
                    {
                        "if": {"properties": {"mode": {"enum": ["normal"]}}},
                        "then": {
                            "required": ["start", "max", "lim"]
                        }
                    },
                    {
                        "if": {"properties": {"mode": {"enum": ["fair"]}}},
                        "then": {
                            "required": ["amt", "start", "end"]
                        }
                    },
                    {
                        "if": {"properties": {"mode": {"enum": ["owner"]}}},
                        "then": {
                            "properties": {
                                "admin": {"is_address": "admin"}
                            },
                            "required": ["admin"]
                        }
                    },
                ],
                "additionalProperties": False
            },
            "mint": {
                "type": "object",
                "properties": {
                    "p": {
                        "enum": ["dot-20"]
                    },
                    "op": {
                        "enum": ["mint"]
                    },
                    "tick": {
                        "type": "string",
                        "pattern": "^[a-zA-Z]{3,6}$"
                    },
                    "lim": {
                        "type": "number",
                        "multipleOf": 1e-18,
                        "minimum": 0,
                        "maximum": 10**32,
                    },
                    "to": {
                        "type": "string",
                        "is_address": "to"
                    },
                },
                "required": ["p", "op", "tick"],
                "additionalProperties": False
            },
            "transfer": {
                "type": "object",
                "properties": {
                    "p": {
                        "enum": ["dot-20"]
                    },
                    "op": {
                        "enum": ["transfer"]
                    },
                    "tick": {
                        "type": "string",
                        "pattern": "^[a-zA-Z]{3,6}$"
                    },
                    "amt": {
                        "type": "number",
                        "multipleOf": 1e-18,
                        "minimum": 0,
                        "maximum": 10**32,
                    },
                    "to": {
                        "type": "string",
                        "is_address": "to"
                    },
                },
                "required": ["p", "op", "tick", "amt", "to"],
                "additionalProperties": False
            },
            "approve": {
                "type": "object",
                "properties": {
                    "p": {
                        "enum": ["dot-20"]
                    },
                    "op": {
                        "enum": ["approve"]
                    },
                    "tick": {
                        "type": "string",
                        "pattern": "^[a-zA-Z]{3,6}$"
                    },
                    "amt": {
                        "type": "number",
                        "multipleOf": 1e-18,
                        "minimum": 0,
                        "maximum": 10**32,
                    },
                    "to": {
                        "type": "string",
                        "is_address": "to"
                    },
                },
                "required": ["p", "op", "tick", "amt", "to"],
                "additionalProperties": False
            },
            "transferFrom": {
                "type": "object",
                "properties": {
                    "p": {
                        "enum": ["dot-20"]
                    },
                    "op": {
                        "enum": ["transferFrom"]
                    },
                    "tick": {
                        "type": "string",
                        "pattern": "^[a-zA-Z]{3,6}$"
                    },
                    "amt": {
                        "type": "number",
                        "multipleOf": 1e-18,
                        "minimum": 0,
                        "maximum": 10**32,
                    },
                    "from": {
                        "type": "string",
                    },
                    "to": {
                        "type": "string",
                        "is_address": "to"
                    },
                },
                "required": ["p", "op", "tick", "amt", "from", "to"],
                "additionalProperties": False
            },
            "rawJson": {
                "type": "object",
                "properties": {
                    "block_num": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10**32,
                    },
                    "block_hash": {
                        "type": "string",
                    },
                    "extrinsic_hash": {
                        "type": "string",
                    },
                    "extrinsic_index": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10**32,
                    },
                    "batchall_index": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10**32,
                    },
                    "remark_index": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10**32,
                    },
                    "remark_hash": {
                        "type": "string",
                    },
                    "origin": {
                        "type": "string",
                        "is_address": "origin"
                    },
                    "user": {
                        "type": "string",
                        "is_address": "user"
                    },
                    "memo": {
                        "type": "string",
                        "is_json_str": True
                    },
                },
                "required": ["block_num", "block_hash", "extrinsic_hash", "extrinsic_index", "batchall_index", "remark_index", "remark_hash", "origin", "user", "memo"],
                "additionalProperties": False
            },
        }
        all_validators = dict(Draft7Validator.VALIDATORS)
        all_validators['is_address'] = is_address
        all_validators['is_json_str'] = is_json_str
        self.custom_validator = validators.create(
            Draft7Validator.META_SCHEMA, all_validators)

    # 判断是否是deploy的memo
    def is_deploy_memo(self, memo_data: object) -> (bool, str):
        return self.__is_xx_json("deploy", json_data=memo_data)

    # 判断是否是mint的memo
    def is_mint_memo(self, memo_data: object) -> (bool, str):
        return self.__is_xx_json("mint", json_data=memo_data)

    # 判断是否是transfer的memo
    def is_transfer_memo(self, memo_data: object) -> (bool, str):
        return self.__is_xx_json("transfer", json_data=memo_data)

    # 判断是否是approve的memo
    def is_approve_memo(self, memo_data: object) -> (bool, str):
        return self.__is_xx_json("approve", json_data=memo_data)

    # 判断是否是deploy的memo
    def is_transferFrom_memo(self, memo_data: object) -> (bool, str):
        return self.__is_xx_json("transferFrom", json_data=memo_data)

    # 判断原json格式
    def is_raw_json(self, json_data: object) -> (bool, str):
        return self.__is_xx_json("rawJson", json_data=json_data)

    # 判断是否是memo的合并方法，需要手动传入op
    # op: enum["deploy","mint","transfer","approve","transferFrom", "rawJson"]
    def is_memo_merge(self, op: str, memo_data: object) -> (bool, str):
        if not op in self._schemas:
            return False, "There is no matching schema"
        return self.__is_xx_json(op, json_data=memo_data)

    def __is_xx_json(self, op: str, json_data: object) -> (bool, str):
        try:
            self.custom_validator(self._schemas.get(
                op)).validate(json_data)
            return True, "OK"
        except jsonschema.ValidationError as e:
            return False, f"{e.message}"
