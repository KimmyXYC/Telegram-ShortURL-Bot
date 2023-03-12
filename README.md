# Telegram 短链接机器人
### 使用方法
- 安装 `Python3.7` 或更高的版本
- 执行 `pip install -r requirements.txt` 安装依赖
- 复制 `Config/app_exp.toml` 到 `Config/app.toml`
- 填写 `Config/app.toml`
- `python3 main.py`运行程序
- 在 Bot 聊天页面发送 `/setdefault [URL]` 设置默认后端地址


### 注意事项
- 目前后端仅适配 [UrlShorter](https://github.com/soxft/UrlShorter/wiki/API)
- 必须设置有效的后端地址，否则无法使用!