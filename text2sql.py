import os
import logging
from typing import Optional, List, Any, Tuple, Dict
from langchain_community.utilities import SQLDatabase
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.chains import create_sql_query_chain
from langchain_community.tools import QuerySQLDataBaseTool
from llm_client import SiliconFlow
from dialogue_context import DialogueContext
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Text2SQL:
    def __init__(self, db_path="sqlite:///data/order_database.db"):
        """初始化Text2SQL类
        
        Args:
            db_path: 数据库连接URI
        """
        self.db = SQLDatabase.from_uri(db_path)
        self.llm = SiliconFlow()
        self.dialogue_context = DialogueContext()
        self.chain = self._build_chain()
        logger.info(f"Text2SQL initialized with db_path: {db_path}")
    
    def _clean_sql_response(self, response: str) -> str:
        """清洗和规范化SQL响应"""
        # 如果已经是标准格式，直接提取SQL
        if "SQLQuery:" in response:
            cleaned_response = response.split("SQLQuery:", 1)[1].strip()
        # 如果包含SELECT语句，提取完整的SQL
        elif "SELECT" in response.upper():
            start_idx = response.upper().find("SELECT")
            cleaned_response = response[start_idx:].split("\n")[0].strip()
        else:
            logger.warning(f"无法识别SQL格式，尝试从响应中提取: {response[:100]}...")
            # 尝试从对话历史中获取最近的有效SQL
            context = self.dialogue_context.get_context_window()
            for msg in reversed(context):
                if msg.get("metadata", {}).get("sql_query"):
                    cleaned_response = msg["metadata"]["sql_query"]
                    logger.info("使用上下文中的最近SQL查询")
                    break
            else:
                logger.error("无法提取SQL且无历史SQL可用")
                cleaned_response = ""
        
        if cleaned_response:
            logger.debug(f"清洗后的SQL: {cleaned_response}")
            # 保存到上下文中
            self.dialogue_context.add_message(
                role="system",
                content="SQL查询已生成",
                metadata={"type": "sql_query", "sql": cleaned_response}
            )
        return cleaned_response
    
    def _format_result_wrapper(self, result: Any) -> dict:
        """将执行结果包装为字典，保留原始 SQL 和结果"""
        if not isinstance(result, str):
            try:
                result_str = str(result)
            except Exception as e:
                logger.error(f"Could not convert SQL result to string: {e}")
                result_str = "Error: Could not format SQL result."
        else:
            result_str = result
        logger.debug(f"Formatted SQL result: {result_str[:200]}...")
        return {"raw_result": result_str}
    
    def _build_chain(self):
        """构建完整的处理链"""
        # SQL 生成链
        write_query = create_sql_query_chain(self.llm, self.db)
        execute_query = QuerySQLDataBaseTool(db=self.db)
        
        # 回答生成提示模板，包含上下文信息
        answer_prompt = PromptTemplate.from_template(
            """基于以下信息回答问题：

对话历史：
{context}

当前问题：{question}
生成的 SQL 查询：{clean_query}
数据库返回结果：{result}

请用自然语言给出简洁答案，同时考虑对话历史上下文。如果结果中的数值为 0，明确说明"没有记录"。"""
        )
        
        # 构建完整链
        chain = (
            # 第一步：接收原始输入，保留问题字段和上下文
            RunnablePassthrough.assign(
                question=lambda x: x["question"],
                context=lambda x: self._format_context(x.get("context", []))
            )
            # 第二步：生成并清洗 SQL
            .assign(
                clean_query=write_query | RunnableLambda(self._clean_sql_response)
            )
            # 第三步：执行 SQL 并包装结果
            .assign(
                result=itemgetter("clean_query") | execute_query | RunnableLambda(self._format_result_wrapper)
            )
            # 第四步：组合所有数据到提示模板并生成回答
            .assign(
                response={
                    "question": itemgetter("question"),
                    "context": itemgetter("context"),
                    "clean_query": itemgetter("clean_query"),
                    "result": itemgetter("result")
                }
                | answer_prompt
                | self.llm
                | StrOutputParser()
            )
            # 第五步：返回包含回答、SQL查询和执行结果的字典
            | {
                "response": itemgetter("response"),
                "clean_query": itemgetter("clean_query"),
                "sql_result": itemgetter("result")
            }
        )
        
        return chain
    
    def _format_context(self, context: List[Dict[str, Any]]) -> str:
        """格式化对话历史上下文"""
        if not context:
            return "无历史对话"
            
        formatted_messages = []
        for msg in context:
            role = "用户" if msg["role"] == "user" else "助手"
            formatted_messages.append(f"{role}: {msg['content']}")
        
        return "\n".join(formatted_messages)
    
    def query(self, question: str, include_context: bool = True) -> tuple[str, str, str]:
        """处理自然语言问题并返回回答、SQL查询和SQL执行结果
        
        Args:
            question: 用户的自然语言问题
            include_context: 是否包含对话历史上下文
            
        Returns:
            tuple[str, str, str]: 返回一个元组，包含(自然语言回答, SQL查询, SQL执行结果)
        """
        logger.info(f"Processing query: {question}")
        try:
            # 获取对话上下文
            context = self.dialogue_context.get_context_window() if include_context else []
            
            # 执行chain并获取结果
            result = self.chain.invoke({
                "question": question,
                "context": context
            })
            
            # 从result中获取response、clean_query和sql_result
            answer = result["response"]
            clean_query = result["clean_query"]
            sql_result = result["sql_result"]["raw_result"]
            
            # 更新对话历史
            self.dialogue_context.add_message(
                role="user",
                content=question,
                metadata={"type": "query"}
            )
            self.dialogue_context.add_message(
                role="assistant",
                content=answer,
                metadata={
                    "type": "response",
                    "sql_query": clean_query,
                    "sql_result": sql_result
                }
            )
            
            return answer, clean_query, sql_result
        except Exception as e:
            logger.error(f"Error during query processing for '{question}': {str(e)}", exc_info=True)
            error_message = "抱歉，处理您的请求时发生错误。"
            self.dialogue_context.add_message(
                role="user",
                content=question,
                metadata={"type": "query", "error": str(e)}
            )
            self.dialogue_context.add_message(
                role="assistant",
                content=error_message,
                metadata={"type": "error", "error": str(e)}
            )
            return error_message, "", ""
    
    def clear_context(self):
        """清空对话上下文"""
        self.dialogue_context.clear_context()
        
    def get_context(self) -> List[Dict[str, Any]]:
        """获取当前对话上下文"""
        return self.dialogue_context.get_all_messages()

# 调用示例 (生产环境中通常不会直接在模块底部执行)
if __name__ == "__main__":
    pass