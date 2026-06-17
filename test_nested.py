from validator import validate_with_rules, FieldRule, DynamicValidator


def print_separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def test_nested_object_validation():
    print_separator("嵌套对象校验测试")

    rules = [
        FieldRule(
            name="username",
            type="str",
            required=True,
            min_length=3,
        ),
        FieldRule(
            name="address",
            type="object",
            required=True,
            rules=[
                FieldRule(
                    name="city",
                    type="str",
                    required=True,
                    min_length=2,
                ),
                FieldRule(
                    name="street",
                    type="str",
                    required=True,
                    min_length=5,
                ),
                FieldRule(
                    name="zipcode",
                    type="str",
                    required=True,
                    pattern=r"^\d{6}$",
                ),
            ],
        ),
    ]

    print("测试1: 嵌套对象字段错误（应该显示完整路径）")
    result = validate_with_rules({
        "username": "testuser",
        "address": {
            "city": "B",
            "street": "Main",
            "zipcode": "12345",
        }
    }, rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试2: 深度嵌套对象校验")
    deep_rules = [
        FieldRule(
            name="level1",
            type="object",
            required=True,
            rules=[
                FieldRule(
                    name="level2",
                    type="object",
                    required=True,
                    rules=[
                        FieldRule(
                            name="value",
                            type="int",
                            required=True,
                            min_value=10,
                            max_value=100,
                        ),
                    ],
                ),
            ],
        ),
    ]
    result = validate_with_rules({
        "level1": {
            "level2": {
                "value": 5,
            }
        }
    }, deep_rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试3: 数组嵌套对象校验")
    array_rules = [
        FieldRule(
            name="name",
            type="str",
            required=True,
        ),
        FieldRule(
            name="items",
            type="array",
            required=True,
            items=[
                FieldRule(
                    name="id",
                    type="int",
                    required=True,
                    min_value=1,
                ),
                FieldRule(
                    name="price",
                    type="float",
                    required=True,
                    gt=0,
                ),
            ],
        ),
    ]
    result = validate_with_rules({
        "name": "订单1",
        "items": [
            {"id": 1, "price": 99.9},
            {"id": 0, "price": -10.0},
        ]
    }, array_rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试4: 正确数据（应该成功）")
    result = validate_with_rules({
        "username": "testuser",
        "address": {
            "city": "Beijing",
            "street": "Chaoyang Road",
            "zipcode": "100000",
        }
    }, rules)
    print(f"  成功: {result.success}")
    print(f"  数据: {result.data}")


if __name__ == "__main__":
    test_nested_object_validation()
