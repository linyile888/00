## 今日学习总结
- 学会使用 `requests` 模块封装函数，向 `https://open.bigmodel.cn/api/paas/v4/chat/completions` 发送 POST 请求，传入 `model`、`messages`、`temperature` 等参数，与智谱 GLM 模型交互。
- 了解如何在请求头中设置 `Authorization` 以及 `Content-Type`，并根据状态码判断请求是成功还是失败，必要时抛出异常便于调试。
- 通过维护一个 `messages` 列表，掌握对话式大模型接口的基本入参格式，其中包含角色与内容字段。
- 回顾 `while True` 输入循环的写法，结合 `input()` 获取用户输入，并在检测到特定指令（例如“再见”）后触发 `break` 以退出循环。
- 学习如何解析接口返回 JSON，提取 `choices[0].message.content` 作为模型回复。

## 003.py 使用说明
1. 安装依赖：脚本依赖 `requests`，可通过 `pip install requests` 安装。
2. 设置 `Authorization`：将 `headers` 中的 `Authorization` 替换为自己的 API Key，切勿在公开仓库暴露。
3. 运行方式：直接执行 `python 003.py`，程序会进入循环输入模式，输入内容后会调用智谱接口并输出模型回复。
4. 退出方式：在提示下输入 `再见`（需先修正条件判断中的语法错误）即可跳出循环并结束程序。

## 注意事项
- 当前脚本中 `if user_input in == "再见":` 存在语法问题，应修改为 `if user_input == "再见":` 才能正常退出。
- 请妥善保护密钥，建议通过环境变量或配置文件加载，避免硬编码。
- 若接口返回非 200 状态码，脚本会抛出异常，可根据 `response.text` 定位错误原因。
## 今日 Python 基础知识总结（基于 001.py 与 002.py）

### 001.py 覆盖点
- 变量与赋值：使用 `name = "lyl"` 声明并初始化字符串变量。
- 基本输出：`print(name)` 将变量内容输出到控制台。

要点：理解变量的创建、字符串类型以及 `print` 的基本使用。

### 002.py 覆盖点
- 模块导入：`import requests`、`import json` 展示第三方库与标准库导入。
- 函数定义与参数：`def call_zhipu_api(messages, model="glm-4-flash")` 展示带默认参数的函数定义与调用。
- 字典与列表：
  - 字典用于组织 `headers`、`data` 等键值对结构。
  - 列表存放多轮对话 `messages`。
- HTTP 请求基础：使用 `requests.post(url, headers=headers, json=data)` 发送 JSON 请求。
- 条件判断与错误处理：根据 `response.status_code` 判断是否成功；失败时 `raise Exception(...)` 抛出异常。
- JSON 处理：`response.json()` 将响应内容解析为 Python 字典；随后通过字典下标访问嵌套数据。
- 程序入口式调用示例：构造 `messages`，调用 `call_zhipu_api(messages)`，并打印结果字段。

要点：掌握函数封装、请求与响应处理、字典/列表的基本操作，以及简单的异常处理范式。

---

### 运行依赖
- Python 3.8+
- 依赖库：

```bash
pip install requests
```

### 安全提示（强烈建议）
002.py 中涉及到外部 API 的调用。实际项目中请通过环境变量管理敏感信息（如 API Key），避免将密钥硬编码进代码仓库。

示例（macOS/Linux）：

```bash
export ZHIPU_API_KEY="your_api_key_here"
```

在代码中使用：

```python
import os
api_key = os.getenv("ZHIPU_API_KEY")
```

并在构造 `headers` 时使用该变量。请勿将真实密钥直接写入源码或提交版本库。

### 示例使用流程（概览）
1) 安装依赖：`pip install requests`
2)（推荐）设置环境变量存放 API Key
3) 运行脚本：

```bash
python 001.py
python 002.py
```

### 小结
- 001.py 帮助理解变量与打印等最基础语法。
- 002.py 进一步实践了函数封装、HTTP 请求、JSON 解析、条件分支与异常处理，体现了把一次完整的 API 调用流程模块化与可复用化的思路。


