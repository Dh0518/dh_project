import os
import json
import requests
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
from langchain_core.messages import ToolMessage
from dotenv import load_dotenv

load_dotenv()

# ----------用@tool定义工具---------
@tool
def get_weather(city: str) -> str:
    """查询指定城市的当前天气信息，包括温度、天气状况、湿度、风速。
    当用户询问某个城市或地区的天气、气温、冷不冷、热不热、下不下雨时，使用此工具。

    Args:
        city:要查询天气的城市名称：例如"北京"、"上海"、"长沙"、"广州"
    """
    try:
        url = f"https://wttr.in/{city}?format=j1&lang=zh-CN"
        resp = requests.get(url, timeout=10, headers={'User-Agent': 'curl/7.68.0'})
        resp.raise_for_status()
        data = resp.json()
        current = data['current_condition'][0]
        area = data['nearest_area'][0]
        return (
            f"【{area['areaName'][0]['value']}天气】\n"
            f"天气:{current['weather'][0]['value']}\n"
            f"温度:{current['temp_c']}°C（体感{current['FeelsLikeC']}°C）\n"
            f"湿度:{current['humidity']}%\n"
            f"风速:{current['windspeedKmph']}km/h"
        )
    except Exception:
        return(
            f"【{city}天气】（模拟数据，网络不通时显示）\n"
            f"天气：晴。温度：28°C（体感30°C）。湿度：65%。风速：12km/h"
        )

tools = [get_weather]
tool_map = {t.name: t for t in tools}


# -------------初始化LLM 并绑定工具----------
llm = ChatOpenAI(
    model=os.getenv("DATA_MODEL"),
    base_url=os.getenv("DATA_BASE_URL"),
    api_key=os.getenv("DATA_API_KEY"),
    temperature=0
)
llm_with_tools = llm.bind_tools(tools)


# -------------ReAct 循环（核心！）----------
def run_agent(user_input: str, verbose: bool = True) -> str:
    messages = [HumanMessage(content=user_input)]
    for step in range(5):  # 最多几轮，防止死循环
        response: AIMessage = llm_with_tools.invoke(messages)
        messages.append(response)
        # 没有工具调用 => 直接就是最终回答
        if not response.tool_calls:
            return response.content
        if verbose:
            for tc in response.tool_calls:
                print(f" [步骤{step+1}] 调用工具：{tc['name']}， 参数：{json.dumps(tc['args'], ensure_ascii=False)}")
        # 有工具调用 => 执行本地函数，把结果回传给模型
        for tc in response.tool_calls:
            tool_result = tool_map[tc["name"]].invoke(tc["args"])
            if verbose:
                print(f" [步骤{step+1}] 工具返回：{str(tool_result)[:60]}...")
            messages.append(ToolMessage(content=str(tool_result), tool_call_id=tc["id"]))

    return "抱歉，查询失败，请稍后再试。"


if __name__ == "__main__":
    print("=" * 50)
    print("天气助手 V1（手写ReAct循环）")
    print("=" * 50)
    for q in ["北京今天天气怎么样？", "长沙现在热不热？"]:
        print(f"\n 你：{q}")
        print(f"助手：{run_agent(q)}")
        print("-" * 50)