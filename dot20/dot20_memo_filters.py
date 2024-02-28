import json
import jsonschema
from jsonschema import Draft7Validator, validators
from jsonschema.exceptions import ValidationError
from scalecodec.types import is_valid_ss58_address


class Dot20MemoFilters:

    def __init__(self, valid_ss58_format=0) -> None:
        self.valid_ss58_format = valid_ss58_format
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
                        "pattern": "^[a-zA-Z]{3,8}$"
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
                        "type": "integer",
                        "exclusiveMinimum": 0,
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
                        "type": "integer",
                        "exclusiveMinimum": 0,
                        "maximum": 10**32,
                    },
                    "lim": {
                        "type": "integer",
                        "exclusiveMinimum": 0,
                        "maximum": 10**32,
                    },
                    "admin": {
                        "type": "string",
                    },
                    "memo_remark": {
                        "type": "string",
                        "maxLength": 1024,
                    }
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
                            "required": ["start", "admin"]
                        }
                    },
                ],
                "additionalProperties": False,
                "custom_deploy_validator": "custom_deploy"
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
                        "pattern": "^[a-zA-Z]{3,8}$"
                    },
                    "lim": {
                        "type": "integer",
                        "exclusiveMinimum": 0,
                        "maximum": 10**32,
                    },
                    "to": {
                        "type": "string",
                        "is_address": "to"
                    },
                    "memo_remark": {
                        "type": "string",
                        "maxLength": 1024,
                    }
                },
                "required": ["p", "op", "tick", "lim", "to"],
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
                        "pattern": "^[a-zA-Z]{3,8}$"
                    },
                    "amt": {
                        "type": "integer",
                        "exclusiveMinimum": 0,
                        "maximum": 10**32,
                    },
                    "to": {
                        "type": "string",
                        "is_address": "to"
                    },
                    "memo_remark": {
                        "type": "string",
                        "maxLength": 1024,
                    }
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
                        "pattern": "^[a-zA-Z]{3,8}$"
                    },
                    "amt": {
                        "type": "integer",
                        "exclusiveMinimum": 0,
                        "maximum": 10**32,
                    },
                    "to": {
                        "type": "string",
                        "is_address": "to"
                    },
                    "memo_remark": {
                        "type": "string",
                        "maxLength": 1024,
                    }
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
                        "pattern": "^[a-zA-Z]{3,8}$"
                    },
                    "amt": {
                        "type": "integer",
                        "exclusiveMinimum": 0,
                        "maximum": 10**32,
                    },
                    "from": {
                        "type": "string",
                        "is_address": "from"
                    },
                    "to": {
                        "type": "string",
                        "is_address": "to"
                    },
                    "memo_remark": {
                        "type": "string",
                        "maxLength": 1024,
                    }
                },
                "required": ["p", "op", "tick", "amt", "from", "to"],
                "additionalProperties": False,
                "custom_transfer_from_validator": "custom_transfer_from"
            },
            "memo": {
                "type": "object",
                "properties": {
                    "p": {
                        "enum": ["dot-20"]
                    },
                    "op": {
                        "enum": ["memo"]
                    },
                    "text": {
                        "type": "string",
                    },
                },
                "required": ["p", "op", "text"],
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
                        "type": ["object", "string"],
                        "is_json_str": "memo"
                    },
                },
                "required": ["block_num", "block_hash", "extrinsic_hash", "extrinsic_index", "batchall_index", "remark_index", "remark_hash", "origin", "user", "memo"],
                "additionalProperties": False
            },
        }
        all_validators = dict(Draft7Validator.VALIDATORS)
        all_validators['is_address'] = self.is_address
        all_validators['is_json_str'] = self.is_json_str
        all_validators['custom_deploy_validator'] = self.custom_deploy_validator
        all_validators['custom_transfer_from_validator'] = self.custom_transfer_from_validator
        self.custom_validator = validators.create(
            Draft7Validator.META_SCHEMA, all_validators)

    def is_deploy_memo(self, memo_data: object) -> (bool, str):
        return self.__is_xx_json("deploy", json_data=memo_data)

    def is_mint_memo(self, memo_data: object) -> (bool, str):
        return self.__is_xx_json("mint", json_data=memo_data)

    def is_transfer_memo(self, memo_data: object) -> (bool, str):
        return self.__is_xx_json("transfer", json_data=memo_data)

    def is_approve_memo(self, memo_data: object) -> (bool, str):
        return self.__is_xx_json("approve", json_data=memo_data)

    def is_transferFrom_memo(self, memo_data: object) -> (bool, str):
        return self.__is_xx_json("transferFrom", json_data=memo_data)

    def is_memo_memo(self, memo_data: object) -> (bool, str):
        return self.__is_xx_json("memo", json_data=memo_data)

    def is_raw_json(self, json_data: object) -> (bool, str):
        return self.__is_xx_json("rawJson", json_data=json_data)

    # op: ["deploy","mint","transfer","approve","transferFrom", "rawJson","memo"]
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
            return False, f"{e.relative_path}:{e.message}"

    def is_address(self, validator, value, instance, schema):
        if is_valid_ss58_address(instance, self.valid_ss58_format) is not True:
            raise ValidationError(f"'{value}' Invalid address")

    def is_json_str(_, validator, value, instance, schema):
        if isinstance(instance, str):
            try:
                s = json.loads(instance)
                if not isinstance(s, dict):
                    raise ValidationError(f"Not a json string")
            except json.JSONDecodeError as e:
                raise ValidationError(f"{value}:{e.msg}")

    def custom_deploy_validator(self, validator, value, instance, schema):
        start, end, lim, max, amt = (instance.get(key)
                                     for key in ["start", "end", "lim", "max", "amt"])
        if start is not None and end is not None and end <= start:
            raise ValidationError(f"'end' is less than or equal to 'start'")

        if lim is not None and max is not None and lim > max:
            raise ValidationError(f"'lim' greater than 'max'")

        if amt is not None and start is not None and end is not None and amt*(end-start+1) > 10 ** 32:
            raise ValidationError(
                f"'amt*(end-start+1)' must not be higher than 10^32")

    def custom_transfer_from_validator(self, validator, value, instance, schema):
        _from, to = (instance.get(key)
                     for key in ["from", "to"])
        if _from is not None and to is not None and _from == to:
            raise ValidationError(
                f"The addresses of 'from' and 'to' are the same")
