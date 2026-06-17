from validator import validate_with_rules, FieldRule, DynamicValidator


def print_separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def test_generic_custom_message():
    print_separator("1. 通用自定义错误消息（message）")

    rules = [
        FieldRule(
            name="username",
            type="str",
            required=True,
            min_length=3,
            max_length=20,
            pattern=r"^[a-zA-Z0-9_]+$",
            message="用户名格式不正确，请输入3-20位字母、数字或下划线",
        ),
    ]

    print("测试1: 字段缺失（使用通用消息）")
    result = validate_with_rules({}, rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试2: 长度太短（使用通用消息）")
    result = validate_with_rules({"username": "ab"}, rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试3: 正则不匹配（使用通用消息）")
    result = validate_with_rules({"username": "user@name"}, rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")


def test_specific_custom_messages():
    print_separator("2. 按错误类型配置自定义消息（messages）")

    rules = [
        FieldRule(
            name="email",
            type="str",
            required=True,
            pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            messages={
                "required": "请输入邮箱地址",
                "pattern": "邮箱格式不正确，例如：user@example.com",
                "type": "邮箱必须是字符串类型",
            },
        ),
        FieldRule(
            name="age",
            type="int",
            required=True,
            min_value=0,
            max_value=150,
            messages={
                "required": "请输入年龄",
                "type": "年龄必须是整数",
                "min_value": "年龄不能小于0岁",
                "max_value": "年龄不能大于150岁",
            },
        ),
    ]

    print("测试1: 邮箱缺失")
    result = validate_with_rules({"age": 25}, rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试2: 邮箱格式错误")
    result = validate_with_rules({"email": "invalid-email", "age": 25}, rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试3: 年龄类型错误")
    result = validate_with_rules({"email": "test@example.com", "age": "twenty"}, rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试4: 年龄小于0")
    result = validate_with_rules({"email": "test@example.com", "age": -5}, rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试5: 年龄大于150")
    result = validate_with_rules({"email": "test@example.com", "age": 200}, rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")


def test_template_variables():
    print_separator("3. 模板变量替换")

    rules = [
        FieldRule(
            name="username",
            type="str",
            required=True,
            min_length=3,
            max_length=20,
            pattern=r"^[a-zA-Z0-9_]+$",
            messages={
                "required": "{name} 不能为空",
                "min_length": "{name} 长度不能少于 {min_length} 个字符",
                "max_length": "{name} 长度不能超过 {max_length} 个字符",
                "pattern": "{name} 格式不正确，需匹配正则：{pattern}",
            },
        ),
        FieldRule(
            name="score",
            type="float",
            required=True,
            min_value=0.0,
            max_value=100.0,
            gt=0,
            lt=100,
            messages={
                "required": "请输入 {name}",
                "min_value": "{name} 不能小于 {min_value}",
                "max_value": "{name} 不能大于 {max_value}",
                "gt": "{name} 必须大于 {gt}",
                "lt": "{name} 必须小于 {lt}",
            },
        ),
    ]

    print("测试1: 必填错误（使用 {name} 变量）")
    result = validate_with_rules({}, rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试2: 长度错误（使用 {min_length} 变量）")
    result = validate_with_rules({"username": "ab", "score": 50}, rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试3: 正则错误（使用 {pattern} 变量）")
    result = validate_with_rules({"username": "user@name", "score": 50}, rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试4: 数值范围错误（使用 {min_value} 变量）")
    result = validate_with_rules({"username": "testuser", "score": -10}, rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")


def test_nested_custom_messages():
    print_separator("4. 嵌套对象自定义消息")

    rules = [
        FieldRule(
            name="username",
            type="str",
            required=True,
            message="用户名不能为空",
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
                    messages={
                        "required": "请输入城市名称",
                        "min_length": "城市名称至少需要 {min_length} 个字符",
                    },
                ),
                FieldRule(
                    name="zipcode",
                    type="str",
                    required=True,
                    pattern=r"^\d{6}$",
                    message="邮政编码格式不正确，应为6位数字",
                ),
            ],
        ),
    ]

    print("测试1: 嵌套字段缺失")
    result = validate_with_rules({
        "username": "testuser",
        "address": {
            "zipcode": "123",
        }
    }, rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试2: 嵌套字段长度和正则错误")
    result = validate_with_rules({
        "username": "testuser",
        "address": {
            "city": "B",
            "zipcode": "123",
        }
    }, rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")


def test_array_custom_messages():
    print_separator("5. 数组元素自定义消息")

    rules = [
        FieldRule(
            name="order_no",
            type="str",
            required=True,
            message="订单号不能为空",
        ),
        FieldRule(
            name="items",
            type="array",
            required=True,
            items=[
                FieldRule(
                    name="product_id",
                    type="int",
                    required=True,
                    min_value=1,
                    messages={
                        "required": "商品ID不能为空",
                        "min_value": "商品ID必须大于等于 {min_value}",
                        "type": "商品ID必须是整数",
                    },
                ),
                FieldRule(
                    name="quantity",
                    type="int",
                    required=True,
                    min_value=1,
                    max_value=99,
                    messages={
                        "required": "请输入商品数量",
                        "min_value": "商品数量至少为 {min_value} 件",
                        "max_value": "商品数量最多为 {max_value} 件",
                    },
                ),
            ],
        ),
    ]

    print("测试1: 数组元素错误")
    result = validate_with_rules({
        "order_no": "ORD-001",
        "items": [
            {"product_id": 1, "quantity": 5},
            {"product_id": 0, "quantity": 100},
        ]
    }, rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")


def test_message_priority():
    print_separator("6. 消息优先级（message > messages > 默认）")

    rules = [
        FieldRule(
            name="field1",
            type="str",
            required=True,
            min_length=5,
            message="通用消息优先级最高",
            messages={
                "required": "必填消息",
                "min_length": "长度消息",
            },
        ),
        FieldRule(
            name="field2",
            type="str",
            required=True,
            min_length=5,
            messages={
                "required": "必填消息",
                "min_length": "长度消息",
            },
        ),
        FieldRule(
            name="field3",
            type="str",
            required=True,
            min_length=5,
        ),
    ]

    print("测试1: message 优先级最高")
    result = validate_with_rules({"field1": "ab"}, rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        if err["field"] == "field1":
            print(f"  - {err['field']}: {err['message']}")

    print("\n测试2: messages 次之")
    result = validate_with_rules({"field2": "ab"}, rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        if err["field"] == "field2":
            print(f"  - {err['field']}: {err['message']}")

    print("\n测试3: 默认消息兜底")
    result = validate_with_rules({"field3": "ab"}, rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        if err["field"] == "field3":
            print(f"  - {err['field']}: {err['message']}")


def test_gt_lt_messages():
    print_separator("7. gt 和 lt 自定义消息")

    rules = [
        FieldRule(
            name="price",
            type="float",
            required=True,
            gt=0,
            lt=10000,
            messages={
                "required": "请输入价格",
                "gt": "价格必须大于 {gt} 元",
                "lt": "价格必须小于 {lt} 元",
            },
        ),
    ]

    print("测试1: 价格等于0（gt 约束）")
    result = validate_with_rules({"price": 0}, rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")

    print("\n测试2: 价格等于10000（lt 约束）")
    result = validate_with_rules({"price": 10000}, rules)
    print(f"  成功: {result.success}")
    for err in result.errors:
        print(f"  - {err['field']}: {err['message']}")


def test_correct_data():
    print_separator("8. 正确数据校验成功")

    rules = [
        FieldRule(
            name="username",
            type="str",
            required=True,
            min_length=3,
            message="用户名格式不正确",
        ),
        FieldRule(
            name="age",
            type="int",
            required=True,
            min_value=0,
            max_value=150,
            messages={
                "required": "请输入年龄",
                "min_value": "年龄不能小于0",
                "max_value": "年龄不能大于150",
            },
        ),
    ]

    print("测试: 所有字段正确")
    result = validate_with_rules({"username": "testuser", "age": 25}, rules)
    print(f"  成功: {result.success}")
    print(f"  数据: {result.data}")


def main():
    print("\n" + "="*60)
    print("  自定义错误消息功能 - 完整测试")
    print("="*60)

    test_generic_custom_message()
    test_specific_custom_messages()
    test_template_variables()
    test_nested_custom_messages()
    test_array_custom_messages()
    test_message_priority()
    test_gt_lt_messages()
    test_correct_data()

    print_separator("测试完成")
    print("所有测试用例执行完毕！")
    print()


if __name__ == "__main__":
    main()
