from langchain_core.runnables import RunnableLambda
from langchain.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain.chains import create_sql_query_chain

# 定义清洗函数：去除 "SQLQuery: " 前缀
def clean_sql_response(response: str) -> str:
    # 检查前缀是否存在
    if response.startswith("SQLQuery:"):
        # 提取前缀后的内容并去除首尾空格
        return response.split("SQLQuery:", 1)[1].strip()
    return response  # 若无前缀，直接返回

def setup_sql_chain(db_uri: str, openai_api_key: str):
    # 设置数据库连接
    db = SQLDatabase.from_uri(db_uri)

    # 设置 LLM
    llm = ChatOpenAI(api_key=openai_api_key)

    # 创建链的完整流程
    sql_chain = create_sql_query_chain(llm, db)
    execute_query = QuerySQLDataBaseTool(db=db)

    # 组合链：生成 SQL → 清洗 → 执行
    chain = sql_chain | RunnableLambda(clean_sql_response) | execute_query

    return chain

# 使用示例
if __name__ == "__main__":
    # 替换为你的实际数据库 URI 和 OpenAI API 密钥
    DB_URI = "your_database_uri"
    OPENAI_API_KEY = "your_openai_api_key"

    chain = setup_sql_chain(DB_URI, OPENAI_API_KEY)
    result = chain.invoke({"question": "what is the lowest sales"})
    print(result)
