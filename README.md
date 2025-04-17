# Open WebUI 👋

官方文档: [Open WebUI Documentation](https://docs.openwebui.com/).  
官方更新日志: [CHANGELOG.md](./CHANGELOG.md)

## 拓展特性

完整特性请看更新日志 [CHANGELOG_EXTRA.md](./CHANGELOG_EXTRA.md)

### 全局积分设置

![credit config](./docs/credit_config.png)

### 用户积分管理与充值

![user credit](./docs/user_credit.png)

### 按照 Token 或请求次数计费，并在对话 Usage 中显示扣费详情

![usage](./docs/usage.png)

## 拓展环境变量

支付相关的配置请在 管理员面板-设置-积分 中配置

```bash
# 配置为任意非空值即可
LICENSE_KEY: "enterprise"

# 组织名称，填写你喜欢的名称
ORGANIZATION_NAME: "XXX"

# 网站名称
CUSTOM_NAME: "XXX"

# 网站 Logo，ICO 格式
CUSTOM_ICO: "https://example.com/favicon.ico"

# 网站 Logo，PNG 格式
CUSTOM_PNG: "https://example.com/favicon.png"

# 网站深色模式 LOGO，PNG 格式
CUSTOM_DARK_PNG: "https://example.com/favicon.png"

# 网站 Logo，SVG 格式
CUSTOM_SVG: "https://example.com/favicon.svg"
```
