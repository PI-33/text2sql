import os
import logging
from typing import Optional, List, Any
from langchain.llms.base import LLM
from openai import OpenAI
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_community.llms.utils import enforce_stop_tokens
from langchain_community.utilities import SQLDatabase
# 设置环境变量
os.environ["API_KEY"] = "131a1191-6d02-48fd-9117-614ac66a78a8"
os.environ["BASE_URL"] = "https://api-inference.modelscope.cn/v1/"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SiliconFlow(LLM):
    def __init__(self):
        super().__init__()

    @property
    def _llm_type(self) -> str:
        return "silicon_flow"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        try:
            client = OpenAI(
                api_key=os.environ.get("API_KEY"),
                base_url=os.environ.get("BASE_URL")  # 修改API路径
            )

            response = client.chat.completions.create(
                model='Qwen/Qwen2.5-Coder-32B-Instruct',
                messages=[
                    {'role': 'user', 'content': prompt}
                ],
            )

            content = ""
            if hasattr(response, 'choices') and response.choices:
                for choice in response.choices:
                    if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                        content += choice.message.content
            else:
                raise ValueError("Unexpected response structure")

            if stop is not None:
                content = enforce_stop_tokens(content, stop)

            return content
        except Exception as e:
            print(f"API调用出错: {str(e)}")
            print(f"完整错误: {e.__class__.__name__}")
            raise



from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.chains import create_sql_query_chain
from langchain_community.tools import QuerySQLDataBaseTool
# ================ 1. 定义组件 ================
# 假设以下组件已初始化

db = SQLDatabase.from_uri("sqlite:///data/order_database.db")
llm = SiliconFlow()

# SQL 生成链（原始输出含 "SQLQuery: " 前缀）
write_query = create_sql_query_chain(llm, db)
execute_query = QuerySQLDataBaseTool(db=db)

# ================ 2. 数据处理函数 ================
def clean_sql_response(response: str) -> str:
    """清洗 SQL 前缀"""
    if response.startswith("SQLQuery:"):
        return response.split("SQLQuery:", 1)[1].strip()
    return response

def format_result_wrapper(result: str) -> dict:
    """将执行结果包装为字典，保留原始 SQL 和结果"""
    return {"raw_result": result}

# ================ 3. 回答生成提示模板 ================
answer_prompt = PromptTemplate.from_template(
    """基于以下信息回答问题：
问题：{question}
生成的 SQL 查询：{clean_query}
数据库返回结果：{result}

请用自然语言给出简洁答案。如果结果中的数值为 0，明确说明“没有记录”"""
)

# ================ 4. 构建完整链 ================
chain = (
    # 第一步：接收原始输入，保留问题字段
    RunnablePassthrough.assign(question=lambda x: x["question"])
    # 第二步：生成并清洗 SQL
    .assign(
        clean_query=write_query | RunnableLambda(clean_sql_response)
    )
    # 第三步：执行 SQL 并包装结果
    .assign(
        result=itemgetter("clean_query") | execute_query | RunnableLambda(format_result_wrapper)
    )
    # 第四步：组合所有数据到提示模板
    | {
        "question": itemgetter("question"),
        "clean_query": itemgetter("clean_query"),
        "result": itemgetter("result")
    }
    | answer_prompt  # 填充模板
    | llm  # 生成自然语言回答
    | StrOutputParser()  # 解析输出
)

# ================ 5. 调用示例 ================
response = chain.invoke({"question": "2024-10-21 到 2024-10-25的平均每日销售额"})
print(response)
