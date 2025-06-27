import gradio as gr
import os
import sys
import pandas as pd
from text2sql import Text2SQL
from text2viz import Text2Viz
import re
import logging

# 初始化实例
text2sql = Text2SQL()
text2viz = Text2Viz()

# 检测是否是可视化请求的函数
def is_visualization_query(query):
    """检测查询是否是可视化请求"""
    viz_keywords = [
        "可视化", "图表", "图形", "绘制", "画图", "展示", "趋势", "变化", 
        "统计图", "柱状图", "折线图", "饼图", "直方图", "散点图", "分布图",
        "visualize", "visualization", "chart", "plot", "graph", "trend", "变化情况"
    ]
    
    # 检查查询中是否包含可视化关键词
    for keyword in viz_keywords:
        if keyword in query.lower():
            return True
    return False

# 定义回调函数
def process_query(message, history):
    """处理用户查询并返回回答"""
    if is_visualization_query(message):
        # 使用Text2Viz处理可视化查询
        df, viz_path = text2viz.visualize(message)
        
        if viz_path and os.path.exists(viz_path):
            # 生成数据摘要
            summary = generate_data_summary(df)
            # 返回带图片的回答 - 确保这里返回的是正确的格式
            return [(message, (summary, viz_path))]
        else:
            # 可视化失败，使用Text2SQL回退
            response = text2sql.query(message)
            return [(message, response)]
    else:
        # 使用Text2SQL处理普通查询
        response = text2sql.query(message)
        return [(message, response)]

# 生成数据摘要
def generate_data_summary(df):
    """生成数据摘要信息"""
    if df.empty:
        return "无法生成数据可视化，请尝试其他查询。"
    
    summary = "以下是查询结果的可视化：\n\n"
    
    # 添加基本统计信息
    summary += f"数据包含 {len(df)} 行记录。\n"
    
    # 根据数据类型添加更多统计信息
    for col in df.columns:
        if pd.api.types.is_datetime64_dtype(df[col]):
            summary += f"• {col} 范围: {df[col].min().date()} 到 {df[col].max().date()}\n"
        elif pd.api.types.is_numeric_dtype(df[col]):
            summary += f"• {col} 统计: 总和={df[col].sum():.2f}, 平均值={df[col].mean():.2f}\n"
    
    return summary

# 创建Gradio界面
def create_combined_interface():
    """创建集成Text2SQL和Text2Viz的Gradio界面"""
    with gr.Blocks(title="Text2SQL & Text2Viz 智能助手", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# Text2SQL & Text2Viz 智能助手")
        gr.Markdown("输入您的数据查询问题，我会将其转换为SQL并返回结果。添加可视化相关词汇（如'可视化'、'图表'、'趋势'等）将生成数据可视化。")
        
        with gr.Row():
            with gr.Column(scale=2):
                # 聊天组件 - 支持图片输出
                chatbot = gr.Chatbot(height=500, label="对话历史")
                msg = gr.Textbox(placeholder="输入您的查询问题...", label="查询")
                submit_btn = gr.Button("提交")
            
            with gr.Column(scale=1):
                # SQL和结果显示区域
                sql_display = gr.Textbox(label="生成的SQL查询", lines=4, interactive=False)
                result_display = gr.Textbox(label="数据库返回结果", lines=8, interactive=False)
        
        # 示例查询
        gr.Examples(
            examples=[
                "2024-10-21 到 2024-10-25的平均每日销售额",
                "10月销售额最高的前5个产品是什么",
                "江苏省的销售总额是多少",
                "可视化2024-10-21到2024-10-27这段时间内sales的变化情况",
                "绘制10月份各省份销售额的对比图表"
            ],
            inputs=msg
        )
        
        # 定义回调函数
        def user_input(user_message, history):
            # 处理用户输入
            return "", history + [[user_message, None]]
        
        # 定义回调函数
        def bot_response(history):
            # 获取最后一条用户消息
            user_message = history[-1][0]
            
            # 使用LLM判断对话类型并获取回答
            conv_type, answer = text2sql.llm.classify_conversation(user_message)
            
            # 如果是普通对话，直接返回回答
            if conv_type == "general":
                history[-1][1] = answer
                return history, "", ""
            
            # 如果是数据查询，继续原有的处理逻辑
            if is_visualization_query(user_message):
                # 处理可视化查询
                df, viz_path, sql_query = text2viz.visualize(user_message)
                
                if viz_path and os.path.exists(viz_path):
                    summary = generate_data_summary(df)
                    db_result = df.head(10).to_string(index=False) if not df.empty else "无数据"
                    
                    # 文本摘要作为当前回复
                    history[-1][1] = summary
                    
                    # 追加图片消息作为新的 assistant 气泡
                    history.append(["", {"path": viz_path}])
                    
                    return history, sql_query, db_result
                else:
                    # 可视化失败，使用Text2SQL回退
                    response, sql_query, db_result = text2sql.query(user_message)
                    # 更新历史 - 纯文本
                    history[-1][1] = response
                    return history, sql_query, db_result
            else:
                # 处理普通文本查询
                response, sql_query, db_result = text2sql.query(user_message)
                # 更新历史
                history[-1][1] = response
                return history, sql_query, db_result
        
        # 设置事件处理
        msg.submit(user_input, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot_response, chatbot, [chatbot, sql_display, result_display]
        )
        submit_btn.click(user_input, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot_response, chatbot, [chatbot, sql_display, result_display]
        )
    
    return interface

# 主函数
# 修改main函数中的日志配置
def main():
    # 设置基本日志级别 - 只在控制台显示INFO级别以上的日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    logging.info("=== 应用启动 ===")
    
    # 创建界面
    interface = create_combined_interface()
    # 启动服务
    interface.launch(share=False)

if __name__ == "__main__":
    main()