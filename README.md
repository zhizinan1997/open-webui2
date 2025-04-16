# Open WebUI 👋

官方文档: [Open WebUI Documentation](https://docs.openwebui.com/).  
官方更新日志: [CHANGELOG.md](./CHANGELOG.md)

## 拓展特性

完整特性请看更新日志 [CHANGELOG_EXTRA.md](./CHANGELOG_EXTRA.md)

### 用户积分管理与充值

![user credit](./docs/user_credit.png)

### 按照 Token 或请求次数计费，并在对话 Usage 中显示扣费详情

![usage](./docs/usage.png)

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

# 允许充值的金额范围，不设置则不限制
# 多个配置使用英文逗号分隔，区间使用 - 分开，例如
# 10-20,30,40-50
# 上面的值表示允许充值 10-20元，30元，40-50元
EZFP_AMOUNT_CONTROL: ""

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
