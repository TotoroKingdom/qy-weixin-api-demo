# 企业微信微盘 API 学习 Demo

一个面向学习和逐步验证的 Python 实验项目，用于调用企业微信（WeCom）微盘 API。

## 环境要求

- Python 3.11+
- 企业微信自建应用的 `CORP_ID` 与 `CORP_SECRET`

## 快速开始

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

在 `.env` 中填写企业微信配置后，按以下顺序逐个运行实验：

```powershell
python .\experiments\step01_auth.py
python .\experiments\step02_get_userid.py
python .\experiments\step03_create_space.py
python .\experiments\step04_space_info.py
python .\experiments\step05_add_space_member.py
python .\experiments\step06_file_list.py
```

未配置凭据时，第一步实验会给出配置提示，不会发起 API 请求。

## 学习步骤

1. `step01_auth.py`：认证并获取 `access_token`
2. `step02_get_userid.py`：通过手机号获取用户 `userid`
3. `step03_create_space.py`：创建微盘空间
4. `step04_space_info.py`：查询微盘空间信息
5. `step05_add_space_member.py`：为微盘空间添加成员权限
6. `step06_file_list.py`：获取微盘空间文件列表

## 验证记录

| 步骤 | 说明 | 状态 | 结果 |
| --- | --- | --- | --- |
| step01 | 获取 access_token | 待验证 | 配置 `.env` 后运行 `python main.py` |

实验响应、令牌结果及调试信息会写入 `output/`；该目录内容默认不提交到 Git。
