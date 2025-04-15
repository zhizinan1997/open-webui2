# Open WebUI 👋

官方文档： [Open WebUI Documentation](https://docs.openwebui.com/).

## 拓展特性

### 新功能

- 用户积分管理与充值
- 按照 Token 或请求次数计费，并在对话 Usage 中显示扣费详情
- 高级 Markdown 编辑器
- 通过 API 批量修改模型价格

### 优化

- 代码块样式

## 拓展环境变量

```bash
# 你的服务的地址，需要易支付能正常访问的
# 不需要携带路径，HTTP协议加域名即可
EZFP_CALLBACK_HOST: "https://my.openwebui.com"

# 易支付的地址，在易支付 API 信息页面有
EZFP_ENDPOINT: "https://xxxx.cn/"

# 易支付 Key
EZFP_KEY: "xxx"

# 易支付商户ID
EZFP_PID: "1"

# 余额不足的提示
CREDIT_NO_CREDIT_MSG: "余额不足，请在 '设置-积分' 中充值"

# 移除模型名前缀
# 例如，你的模型是 xxx-gpt-4o 与官方不一致，这里配置为 xxx-
# 如果是一致的则无需配置
USAGE_CALCULATE_MODEL_PREFIX_TO_REMOVE: ""

# Token 计算模型
# 如果没有返回 Usage，并且模型无法匹配上，则使用这个模型的 tiktoken encoder 来计算 Token
# 价格仍然使用请求的模型的价格
USAGE_DEFAULT_ENCODING_MODEL: "gpt-4o
```

## 开发文档

如果你是 Pipe 开发者，请参考下面的文档进行埋点，确保能够正常计费

### 流式传输

```python
from open_webui.models.models import Models
from open_webui.models.users import Users
from open_webui.utils.usage import CreditDeduct

with CreditDeduct(
    user=Users.get_user_by_id(__user__["id"]),
    model=Models.get_model_by_id(body["model"]).model_dump(),
    body=body,
    is_stream=True,
) as credit_deduct:

    # 唯一的区别是 yield 之前先调用 credit_deduct
    # 如果你的 chunk 不是标准的 openai 格式，请自行转换
    async for chunk in content:
        credit_deduct.run(response=chunk)
        yield chunk

    # 提交这个用于更新前端的 Usage 信息
    yield "data: " + json.dumps(
        {"usage": credit_deduct.usage_with_cost}
    )
```

### 非流式传输

```python
from open_webui.models.models import Models
from open_webui.models.users import Users
from open_webui.utils.usage import CreditDeduct

with CreditDeduct(
    user=Users.get_user_by_id(__user__["id"]),
    model=Models.get_model_by_id(body["model"]).model_dump(),
    body=body,
    is_stream=False,
) as credit_deduct:

    # 需要获取到 JSON
    # 如果你的 response 不是标准的 openai 格式，请自行转换
    response = response.json()

    credit_deduct.run(response=response)
    if isinstance(response, dict):
        response.update({"usage": credit_deduct.usage_with_cost})
```

### 转换方式

假设你只有文本 content

```python
content = "我是 LLM 的回复"

credit_deduct.run(
    {
        "id": uuid.uuid4().hex,
        "choices": [
            {
                "delta": {"content": content},
                "index": 0,
            }
        ],
        "created": int(datetime.datetime.now().timestamp()),
        "model": model_id,
    }
)
```
