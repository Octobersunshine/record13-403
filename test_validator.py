from validator import (
    UserValidator,
    ProductValidator,
    DynamicValidator,
    FieldRule,
    validate_with_rules,
)


def print_separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def test_required_validation():
    print_separator("1. 必填校验测试")

    validator = UserValidator()

    print("测试1: 缺少必填字段 username 和 email")
    result = validator.validate({})
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试2: 只提供 username，缺少 email")
    result = validator.validate({"username": "testuser"})
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试3: 提供所有必填字段")
    result = validator.validate({"username": "testuser", "email": "test@example.com"})
    print(f"  成功: {result.success}")
    print(f"  数据: {result.data}")


def test_type_validation():
    print_separator("2. 类型校验测试")

    validator = UserValidator()

    print("测试1: age 传入字符串（应该失败）")
    result = validator.validate({"username": "testuser", "email": "test@example.com", "age": "not_a_number"})
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试2: age 传入整数（应该成功）")
    result = validator.validate({"username": "testuser", "email": "test@example.com", "age": 25})
    print(f"  成功: {result.success}")
    print(f"  数据: {result.data}")

    print("\n测试3: score 传入浮点数（应该成功）")
    result = validator.validate({"username": "testuser", "email": "test@example.com", "score": 85.5})
    print(f"  成功: {result.success}")
    print(f"  数据: {result.data}")


def test_regex_validation():
    print_separator("3. 正则匹配测试")

    validator = UserValidator()

    print("测试1: username 包含特殊字符（应该失败）")
    result = validator.validate({"username": "test@user", "email": "test@example.com"})
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试2: username 合法（应该成功）")
    result = validator.validate({"username": "test_user123", "email": "test@example.com"})
    print(f"  成功: {result.success}")
    print(f"  数据: {result.data}")

    print("\n测试3: email 格式错误（应该失败）")
    result = validator.validate({"username": "testuser", "email": "invalid-email"})
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试4: phone 手机号格式（应该成功）")
    result = validator.validate({"username": "testuser", "email": "test@example.com", "phone": "13812345678"})
    print(f"  成功: {result.success}")
    print(f"  数据: {result.data}")

    print("\n测试5: phone 手机号格式错误（应该失败）")
    result = validator.validate({"username": "testuser", "email": "test@example.com", "phone": "12345678901"})
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")


def test_range_validation():
    print_separator("4. 数值范围校验测试")

    validator = UserValidator()

    print("测试1: age 小于 0（应该失败）")
    result = validator.validate({"username": "testuser", "email": "test@example.com", "age": -1})
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试2: age 大于 150（应该失败）")
    result = validator.validate({"username": "testuser", "email": "test@example.com", "age": 200})
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试3: age 在范围内（应该成功）")
    result = validator.validate({"username": "testuser", "email": "test@example.com", "age": 25})
    print(f"  成功: {result.success}")
    print(f"  数据: {result.data}")

    print("\n测试4: score 小于 0（应该失败）")
    result = validator.validate({"username": "testuser", "email": "test@example.com", "score": -1.5})
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试5: score 大于 100（应该失败）")
    result = validator.validate({"username": "testuser", "email": "test@example.com", "score": 101.0})
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试6: score 在范围内（应该成功）")
    result = validator.validate({"username": "testuser", "email": "test@example.com", "score": 92.5})
    print(f"  成功: {result.success}")
    print(f"  数据: {result.data}")


def test_product_validator():
    print_separator("5. 产品校验器测试")

    validator = ProductValidator()

    print("测试1: 价格大于 0（应该成功）")
    result = validator.validate({
        "product_name": "iPhone 15",
        "price": 5999.00,
        "stock": 100,
        "sku": "APP-12345",
    })
    print(f"  成功: {result.success}")
    print(f"  数据: {result.data}")

    print("\n测试2: 价格等于 0（应该失败，使用 gt 约束）")
    result = validator.validate({
        "product_name": "iPhone 15",
        "price": 0,
        "stock": 100,
        "sku": "APP-12345",
    })
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试3: SKU 格式错误（应该失败）")
    result = validator.validate({
        "product_name": "iPhone 15",
        "price": 5999.00,
        "stock": 100,
        "sku": "abc-123",
    })
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试4: 缺少 category，使用默认值（应该成功）")
    result = validator.validate({
        "product_name": "MacBook Pro",
        "price": 14999.00,
        "stock": 50,
        "sku": "MAC-9999",
    })
    print(f"  成功: {result.success}")
    print(f"  数据: {result.data}")


def test_dynamic_validator():
    print_separator("6. 动态校验器测试")

    rules = [
        FieldRule(
            name="order_id",
            type="str",
            required=True,
            pattern=r"^ORD-\d{8}$",
            description="订单号格式：ORD-yyyyMMdd",
        ),
        FieldRule(
            name="amount",
            type="float",
            required=True,
            gt=0,
            lt=100000,
            description="订单金额，0到10万之间",
        ),
        FieldRule(
            name="quantity",
            type="int",
            required=True,
            min_value=1,
            max_value=99,
            description="数量，1-99",
        ),
        FieldRule(
            name="remark",
            type="str",
            required=False,
            max_length=200,
            description="备注，最长200字符",
        ),
    ]

    validator = DynamicValidator(rules)

    print("测试1: 合法数据（应该成功）")
    result = validator.validate({
        "order_id": "ORD-20240115",
        "amount": 999.99,
        "quantity": 5,
        "remark": "加急发货",
    })
    print(f"  成功: {result.success}")
    print(f"  数据: {result.data}")

    print("\n测试2: 金额超过上限（应该失败）")
    result = validator.validate({
        "order_id": "ORD-20240115",
        "amount": 100000.00,
        "quantity": 5,
    })
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试3: 数量为 0（应该失败）")
    result = validator.validate({
        "order_id": "ORD-20240115",
        "amount": 99.99,
        "quantity": 0,
    })
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试4: 使用 validate_with_rules 便捷函数")
    result = validate_with_rules(
        {"name": "张三", "age": 30},
        [
            FieldRule(name="name", type="str", required=True, min_length=2),
            FieldRule(name="age", type="int", required=True, min_value=0, max_value=120),
        ]
    )
    print(f"  成功: {result.success}")
    print(f"  数据: {result.data}")


def test_string_length_validation():
    print_separator("7. 字符串长度校验测试")

    validator = UserValidator()

    print("测试1: username 太短（应该失败）")
    result = validator.validate({"username": "ab", "email": "test@example.com"})
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试2: username 太长（应该失败）")
    result = validator.validate({"username": "a" * 21, "email": "test@example.com"})
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试3: username 长度正好（应该成功）")
    result = validator.validate({"username": "abc", "email": "test@example.com"})
    print(f"  成功: {result.success}")
    print(f"  数据: {result.data}")


def main():
    print("\n" + "="*60)
    print("  Pydantic 数据校验服务 - 完整测试")
    print("="*60)

    test_required_validation()
    test_type_validation()
    test_regex_validation()
    test_range_validation()
    test_string_length_validation()
    test_product_validator()
    test_dynamic_validator()

    print_separator("测试完成")
    print("所有测试用例执行完毕！")
    print()


if __name__ == "__main__":
    main()
