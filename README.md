# 🌤️ 天气助手（Weather Agent）

一个基于 **LangChain + OpenAI 兼容接口** 的多轮对话天气助手。
支持查询任意城市的实时天气（温度、体感、湿度、风速），并根据温度自动给出穿衣建议。

---

## ✨ 功能特性

- 🔍 **实时天气查询**：通过 [wttr.in](https://wttr.in) 免费接口查询全球任意城市天气
- 💬 **多轮对话**：自动维护上下文历史，可以连续追问
- 🧥 **智能建议**：根据温度自动给出穿衣提示（<10°C 保暖，>30°C 防暑）
- 🛡️ **网络兜底**：网络不通时返回模拟数据，保证对话不中断
- 🔌 **模型可切换**：通过 `.env` 配置即可对接任意 OpenAI 兼容 API（OpenAI、DeepSeek、通义、本地 Ollama 等）
- 🧹 **会话清空**：命令行内输入 `clear` 随时重置对话

---

## 📂 项目结构

```
.
├── weather.py           # 主程序
├── requirements.txt     # 依赖清单
├── .env                 # 环境变量（需自行创建，不入库）
├── .env.example         # 环境变量示例
└── README.md
```

---

## 🧰 环境要求

- Python **3.10+**
- 可访问 [wttr.in](https://wttr.in) 的网络环境（国内访问如遇慢，程序会自动降级到模拟数据）
- 任意 **OpenAI 兼容** 的大模型 API Key

---

## 🚀 快速开始

### 1. 克隆并安装依赖

```bash
git clone <your-repo-url>
cd <your-repo-dir>

# 建议使用虚拟环境
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```ini
# 模型名称（必填）
DATA_MODEL=gpt-4o-mini

# 接口地址（必填，需兼容 OpenAI 格式，且以 /v1 结尾）
DATA_BASE_URL=https://api.openai.com/v1

# API Key（必填）
DATA_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

> 💡 换用其他服务只需替换 `DATA_BASE_URL` 与 `DATA_MODEL`，例如：
>
> | 服务商 | DATA_BASE_URL | DATA_MODEL 示例 |
> |---|---|---|
> | OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
> | DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
> | 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |
> | Ollama（本地） | `http://localhost:11434/v1` | `qwen2.5` |

### 3. 运行

```bash
python weather.py
```

---

## 💬 使用示例

```
==================================================
天气助手 V1（多轮对话版）
命令：quit 退出 | clear 清空对话
==================================================

你：北京天气怎么样？
助手：【北京天气】
天气：晴
温度：26°C（体感 27°C）
湿度：40%
风速：15km/h
今天天气不错，穿短袖或薄长袖都可以，早晚微凉可以带件外套。

你：那上海呢？
助手：【上海天气】
...
（能理解上下文，知道你在继续问天气）

你：clear
对话已清空，重新开始~

你：quit
再见！
```

---

## 🧠 工作原理

1. **工具定义**：`get_weather(city)` 用 `@tool` 装饰，通过 wttr.in 的 `format=j1` JSON 接口拉取实时数据并格式化返回。
2. **Agent 构建**：`create_agent` 将 LLM 与 `get_weather` 工具绑定，配合 `system_prompt` 约束行为：
   - 天气问题必须调用工具（不编造数据）
   - 温度高低自动给穿衣建议
   - 未提供城市时礼貌询问
   - 非天气问题礼貌拒绝
3. **多轮对话**：`WeatherChat` 类自行维护 `self.messages` 列表。每次 `send()` 都会把用户消息 append 进历史，传入 `agent.invoke`，再用返回的完整消息列表（包含工具调用轨迹）替换历史，保证上下文不丢失。

---

## ⚙️ 可调项

| 位置 | 说明 |
|---|---|
| `system_prompt` | 修改助手人设、穿衣阈值、回答风格 |
| `get_weather` 中的 `except` 分支 | 替换兜底模拟数据 |
| `temperature=0` | 调整生成随机性 |
| `WeatherChat.messages` | 若需限制上下文长度，可在此做截断 |

---

## ❓ 常见问题

**Q1：报 `AttributeError: module 'langchain.agents' has no attribute 'create_agent'`？**
请确认 `langchain>=1.0` 且已按 `requirements.txt` 安装。旧版本没有 `create_agent`，需升级或改用 `create_react_agent`。

**Q2：天气接口偶尔返回模拟数据？**
`wttr.in` 在国内访问不稳。程序已在 `except` 中兜底为模拟数据；如需稳定，可替换 `get_weather` 中的 `url` 为其他天气 API（如高德、和风）。

**Q3：`DATA_BASE_URL` 需不需要带 `/v1`？**
取决于服务商。OpenAI 兼容接口一般必须带 `/v1`；Ollama 本地同样需要 `/v1`。

**Q4：如何限制对话历史长度避免 token 超限？**
可在 `WeatherChat.send()` 中 append 后判断 `len(self.messages) > N`，并保留首条 + 最近 N 条。

---

## 📄 License

MIT
