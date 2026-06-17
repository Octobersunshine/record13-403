from typing import Any, Dict, List, Optional, Type, Union
from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    ConfigDict,
    create_model,
)


class ValidationResult:
    def __init__(self, success: bool, data: Optional[Dict[str, Any]] = None, errors: Optional[List[Dict[str, Any]]] = None):
        self.success = success
        self.data = data
        self.errors = errors or []

    def __repr__(self):
        if self.success:
            return f"ValidationResult(success=True, data={self.data})"
        return f"ValidationResult(success=False, errors={self.errors})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "errors": self.errors,
        }


class FieldRule(BaseModel):
    name: str
    type: str = "str"
    required: bool = True
    default: Any = None
    pattern: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    gt: Optional[Union[int, float]] = None
    lt: Optional[Union[int, float]] = None
    description: Optional[str] = None
    rules: Optional[List["FieldRule"]] = None
    items: Optional[List["FieldRule"]] = None
    message: Optional[str] = None
    messages: Optional[Dict[str, str]] = None


FieldRule.model_rebuild()


class DynamicValidator:
    _type_mapping = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "list": list,
        "dict": dict,
        "object": dict,
        "array": list,
    }

    _error_type_mapping = {
        "missing": "required",
        "int_parsing": "type",
        "float_parsing": "type",
        "bool_parsing": "type",
        "string_type": "type",
        "int_type": "type",
        "float_type": "type",
        "bool_type": "type",
        "list_type": "type",
        "dict_type": "type",
        "string_pattern_mismatch": "pattern",
        "string_too_short": "min_length",
        "string_too_long": "max_length",
        "greater_than_equal": "min_value",
        "less_than_equal": "max_value",
        "greater_than": "gt",
        "less_than": "lt",
        "extra_forbidden": "extra",
    }

    def __init__(self, rules: List[FieldRule]):
        self.rules = rules
        self._model = self._build_model()
        self._rule_lookup = self._build_rule_lookup(rules)

    def _build_rule_lookup(self, rules: List[FieldRule], prefix: str = "") -> Dict[str, FieldRule]:
        lookup = {}
        for rule in rules:
            field_path = f"{prefix}.{rule.name}" if prefix else rule.name
            lookup[field_path] = rule
            if rule.type == "object" and rule.rules:
                lookup.update(self._build_rule_lookup(rule.rules, field_path))
            if rule.type == "array" and rule.items:
                lookup.update(self._build_rule_lookup(rule.items, f"{field_path}.*"))
        return lookup

    def _get_template_vars(self, rule: FieldRule) -> Dict[str, Any]:
        return {
            "name": rule.name,
            "type": rule.type,
            "pattern": rule.pattern,
            "min_length": rule.min_length,
            "max_length": rule.max_length,
            "min_value": rule.min_value,
            "max_value": rule.max_value,
            "gt": rule.gt,
            "lt": rule.lt,
            "description": rule.description,
        }

    def _format_message(self, template: str, rule: FieldRule) -> str:
        vars_dict = self._get_template_vars(rule)
        try:
            return template.format(**vars_dict)
        except (KeyError, ValueError):
            return template

    def _get_custom_message(self, field_path: str, error_type: str, default_msg: str) -> str:
        lookup_key = field_path
        if "." in lookup_key:
            parts = lookup_key.split(".")
            for i in range(len(parts)):
                if parts[i].isdigit():
                    parts[i] = "*"
            lookup_key = ".".join(parts)

        rule = self._rule_lookup.get(lookup_key)
        if rule is None:
            return default_msg

        if rule.message:
            return self._format_message(rule.message, rule)

        if rule.messages:
            mapped_type = self._error_type_mapping.get(error_type, error_type)
            custom_msg = rule.messages.get(mapped_type)
            if custom_msg:
                return self._format_message(custom_msg, rule)
            if mapped_type != error_type:
                custom_msg = rule.messages.get(error_type)
                if custom_msg:
                    return self._format_message(custom_msg, rule)

        return default_msg

    def _build_nested_model(self, rules: List[FieldRule], model_name: str = "NestedModel") -> Type[BaseModel]:
        fields = {}

        for rule in rules:
            field_kwargs = {}
            python_type = self._type_mapping.get(rule.type, str)

            if rule.type == "object" and rule.rules:
                python_type = self._build_nested_model(rule.rules, f"{model_name}_{rule.name}")
            elif rule.type == "array" and rule.items:
                item_type = self._build_nested_model(rule.items, f"{model_name}_{rule.name}_item")
                python_type = List[item_type]

            if not rule.required and rule.default is not None:
                field_kwargs["default"] = rule.default
            elif not rule.required:
                field_kwargs["default"] = None
                python_type = Optional[python_type]

            if rule.type not in ("object", "array"):
                if rule.min_length is not None:
                    field_kwargs["min_length"] = rule.min_length
                if rule.max_length is not None:
                    field_kwargs["max_length"] = rule.max_length

                if rule.min_value is not None:
                    field_kwargs["ge"] = rule.min_value
                if rule.max_value is not None:
                    field_kwargs["le"] = rule.max_value
                if rule.gt is not None:
                    field_kwargs["gt"] = rule.gt
                if rule.lt is not None:
                    field_kwargs["lt"] = rule.lt

                if rule.pattern is not None:
                    field_kwargs["pattern"] = rule.pattern

            if rule.description:
                field_kwargs["description"] = rule.description

            fields[rule.name] = (python_type, Field(**field_kwargs))

        model_config = ConfigDict(extra="forbid")
        model = create_model(
            model_name,
            __config__=model_config,
            **fields,
        )

        return model

    def _build_model(self) -> Type[BaseModel]:
        return self._build_nested_model(self.rules, "DynamicModel")

    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        try:
            instance = self._model.model_validate(data)
            return ValidationResult(success=True, data=instance.model_dump())
        except ValidationError as e:
            errors = []
            for error in e.errors():
                field_name = ".".join(str(loc) for loc in error["loc"])
                custom_message = self._get_custom_message(field_name, error["type"], error["msg"])
                errors.append({
                    "field": field_name,
                    "message": custom_message,
                    "type": error["type"],
                })
            return ValidationResult(success=False, errors=errors)


class UserValidator:
    def __init__(self):
        rules = [
            FieldRule(
                name="username",
                type="str",
                required=True,
                min_length=3,
                max_length=20,
                pattern=r"^[a-zA-Z0-9_]+$",
                description="用户名，3-20位字母数字下划线",
            ),
            FieldRule(
                name="email",
                type="str",
                required=True,
                pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                description="邮箱地址",
            ),
            FieldRule(
                name="age",
                type="int",
                required=False,
                min_value=0,
                max_value=150,
                description="年龄，0-150岁",
            ),
            FieldRule(
                name="phone",
                type="str",
                required=False,
                pattern=r"^1[3-9]\d{9}$",
                description="手机号，中国大陆格式",
            ),
            FieldRule(
                name="score",
                type="float",
                required=False,
                min_value=0.0,
                max_value=100.0,
                description="分数，0-100",
            ),
        ]
        self._validator = DynamicValidator(rules)

    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        return self._validator.validate(data)


class ProductValidator:
    def __init__(self):
        rules = [
            FieldRule(
                name="product_name",
                type="str",
                required=True,
                min_length=2,
                max_length=100,
                description="产品名称，2-100字符",
            ),
            FieldRule(
                name="price",
                type="float",
                required=True,
                gt=0,
                description="价格，必须大于0",
            ),
            FieldRule(
                name="stock",
                type="int",
                required=True,
                min_value=0,
                description="库存数量，非负整数",
            ),
            FieldRule(
                name="sku",
                type="str",
                required=True,
                pattern=r"^[A-Z]{3}-\d{4,}$",
                description="SKU编码，如ABC-1234",
            ),
            FieldRule(
                name="category",
                type="str",
                required=False,
                default="uncategorized",
                description="产品分类",
            ),
        ]
        self._validator = DynamicValidator(rules)

    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        return self._validator.validate(data)


def validate_with_rules(data: Dict[str, Any], rules: List[FieldRule]) -> ValidationResult:
    validator = DynamicValidator(rules)
    return validator.validate(data)
