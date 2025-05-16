import pandas as pd
import matplotlib.pyplot as plt
from langchain_community.utilities import SQLDatabase
import seaborn as sns
from datetime import datetime
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.chains import create_sql_query_chain
from langchain_community.tools import QuerySQLDataBaseTool
from langchain.llms.base import LLM
from openai import OpenAI
from typing import Optional, List, Any
from langchain.callbacks.manager import CallbackManagerForLLMRun
import os
import logging
import ast
from langchain_community.llms.utils import enforce_stop_tokens
from langchain.llms.base import LLM
from openai import OpenAI
from typing import Optional, List, Any
from langchain.callbacks.manager import CallbackManagerForLLMRun

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


# 连接数据库

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ast
from operator import itemgetter
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.chains import create_sql_query_chain
from langchain.tools.sql_database.tool import QuerySQLDataBaseTool

def create_visualization_pipeline(llm, db):
    # SQL生成和执行组件
    write_query = create_sql_query_chain(llm, db)
    execute_query = QuerySQLDataBaseTool(db=db)

    # 数据处理函数
    def clean_sql_response(response: str) -> str:
        """清洗 SQL 前缀"""
        if response.startswith("SQLQuery:"):
            return response.split("SQLQuery:", 1)[1].strip()
        return response

    def convert_to_dataframe(result: str) -> pd.DataFrame:
        """将SQL结果转换为DataFrame，支持不同的列名和数据格式"""
        if result.startswith('[') and result.endswith(']'):
            try:
                parsed_data = ast.literal_eval(result)
                if parsed_data and isinstance(parsed_data[0], tuple):
                    # 动态创建DataFrame，不指定固定列名
                    df = pd.DataFrame(parsed_data)
                else:
                    df = pd.DataFrame(parsed_data)
            except:
                # 备用解析方法
                df = pd.DataFrame([item.strip("()").split(",") for item in result.strip("[]").split("), (")])
        else:
            # 如果结果不是列表格式，返回空DataFrame
            df = pd.DataFrame()

        # 尝试自动转换数据类型
        for col in df.columns:
            # 尝试转换为日期类型
            try:
                df[col] = pd.to_datetime(df[col])
                continue  # 如果成功转换为日期，则继续下一列
            except:
                pass

            # 尝试转换为数值类型
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except:
                pass  # 如果无法转换为数值，保持原样

        return df

    def create_visualization(df: pd.DataFrame) -> tuple:
        """创建可视化图表，支持不同的列名"""
        if len(df.columns) < 2 or df.empty:
            # 处理数据不足的情况
            return df, None

        # 推断x轴和y轴
        # 假设第一列是日期或分类变量作为x轴，第二列是数值作为y轴
        x_col = df.columns[0]
        y_col = df.columns[1]

        # 检查并确保y轴数据是数值型
        if not pd.api.types.is_numeric_dtype(df[y_col]):
            # 尝试转换为数值型
            df[y_col] = pd.to_numeric(df[y_col], errors='coerce')

        plt.figure(figsize=(12, 6))
        sns.set_style("whitegrid")

        # 根据x轴数据类型选择合适的图表类型
        if pd.api.types.is_datetime64_dtype(df[x_col]):
            # 时间序列图
            plt.plot(df[x_col], df[y_col], marker='o')
        else:
            # 对于分类数据使用条形图
            plt.bar(df[x_col], df[y_col])

        plt.title(f"{y_col} by {x_col}", fontsize=14)
        plt.xlabel(x_col, fontsize=12)
        plt.ylabel(y_col, fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # 保存图表
        output_file = 't1.png'
        plt.savefig(output_file)
        plt.close()

        return df, output_file

    # 构建完整链
    chain = (
        # 第一步：接收原始输入，保留问题字段
        RunnablePassthrough.assign(question=lambda x: x["question"])
        # 第二步：生成并清洗 SQL
        .assign(
            clean_query=write_query | RunnableLambda(clean_sql_response)
        )
        # 第三步：执行SQL并转换为DataFrame，生成可视化
        .assign(
            result=itemgetter("clean_query")
                  | execute_query
                  | RunnableLambda(convert_to_dataframe)
                  | RunnableLambda(create_visualization)
        )
        # 第四步：提取结果
        | itemgetter("result")
    )

    return chain

def main():
    # 首先完全禁用所有第三方库的DEBUG日志
    # 这需要在导入任何其他库之前完成
    logging.basicConfig(
        level=logging.WARNING,  # 仅显示WARNING及以上级别的日志
        format='%(message)s'    # 简化日志格式，只显示消息内容
    )

    # 特别禁用相关库的调试日志
    for logger_name in [
        "openai", "langchain", "langchain_core", "httpx",
        "urllib3", "matplotlib", "PIL", "requests"
    ]:
        logging.getLogger(logger_name).setLevel(logging.ERROR)  # 只显示错误信息

    # 禁用OpenAI客户端的请求日志
    import openai
    openai.log = "error"  # 只记录错误

    # 如果需要自定义日志，创建一个新的日志器
    app_logger = logging.getLogger("text2viz")
    app_logger.setLevel(logging.INFO)

    # 添加一个控制台处理器，带有自定义格式
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    app_logger.addHandler(console_handler)

    # 连接数据库和初始化模型
    db = SQLDatabase.from_uri("sqlite:///data/order_database.db")
    llm = SiliconFlow()

    chain = create_visualization_pipeline(llm, db)
    query = "查询2024-10-21到2024-10-27这段时间内sales的变化情况"

    try:
        app_logger.info(f"🔍 执行查询: {query}")

        # 使用自定义静默模式执行查询
        with contextlib.redirect_stdout(io.StringIO()):  # 临时重定向stdout
            df, viz_path = chain.invoke({"question": query})

        app_logger.info("\n📊 数据结果:")
        if len(df) <= 10:  # 数据量不大时直接输出
            app_logger.info(df.to_string(index=False))  # 更整洁的表格输出，无索引
        else:  # 数据量大时只输出摘要
            app_logger.info(f"共 {len(df)} 行数据。前5行:")
            app_logger.info(df.head().to_string(index=False))

        if viz_path:
            app_logger.info(f"\n📈 可视化结果已保存至: {viz_path}")

        # 根据数据类型输出合适的统计信息
        app_logger.info("\n📋 数据摘要:")
        app_logger.info(f"• 总行数: {len(df)}")

        # 动态检测并输出统计信息
        for col in df.columns:
            if pd.api.types.is_datetime64_dtype(df[col]):
                app_logger.info(f"• {col}范围: {df[col].min().date()} 到 {df[col].max().date()}")
            elif pd.api.types.is_numeric_dtype(df[col]):
                app_logger.info(f"• {col}统计: 总和={df[col].sum():.2f}, 平均值={df[col].mean():.2f}")

    except Exception as e:
        app_logger.error(f"❌ 查询执行失败: {str(e)}")
        import traceback
        app_logger.debug(traceback.format_exc())  # 仅在DEBUG级别显示完整堆栈跟踪

if __name__ == "__main__":
    # 导入需要的额外模块
    import io
    import contextlib
    main()
