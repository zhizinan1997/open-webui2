# Open WebUI 👋

官方文档: [Open WebUI Documentation](https://docs.openwebui.com/).  
官方更新日志: [CHANGELOG.md](./CHANGELOG.md)

## 部署方式

> [!TIP]
> 部署后，不能直接回退到官方镜像；如需使用官方镜像，请参考此篇 [Wiki](https://github.com/U8F69/open-webui/wiki/%E9%87%8D%E6%96%B0%E4%BD%BF%E7%94%A8%E5%AE%98%E6%96%B9%E9%95%9C%E5%83%8F) 处理

部署二开版本只需要替换镜像和版本，其他的部署与官方版本没有差别，版本号请在 [Release](https://github.com/U8F69/open-webui/releases/latest) 中查看，环境变量参考下方 [拓展环境变量](#%E6%8B%93%E5%B1%95%E7%8E%AF%E5%A2%83%E5%8F%98%E9%87%8F)

```
ghcr.io/u8f69/open-webui:<版本号>
```

## 拓展特性

完整特性请看更新日志 [CHANGELOG_EXTRA.md](./CHANGELOG_EXTRA.md)

### 积分报表

![usage panel](./docs/usage_panel.png)

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
