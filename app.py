import os
import sys
import pandas as pd
from text2sql import Text2SQL
from text2viz import Text2Viz
from dialogue_context import DialogueContext
import re
import logging
import gradio as gr

# 初始化实例
text2sql = Text2SQL()
text2viz = Text2Viz()
dialogue_context = DialogueContext()


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
    # 使用外部CSS文件
    custom_css = """
    @import url('static/css/style.css');
    """

    with gr.Blocks(title="🔍 L'Oréal 数据洞察助手", theme=gr.themes.Soft(), css=custom_css) as interface:
        # 主标题区域 - 紧凑设计
        with gr.Row():
            with gr.Column():
                gr.HTML("""
                <div class="main-header">
                    <h1 style="margin: 0; font-size: 2rem; font-weight: 700;">🔍 L'Oréal 数据洞察助手</h1>
                    <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;">用对话替代 SQL，让数据分析触手可及</p>
                </div>
                """)

        # 功能介绍卡片 - 简洁设计
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="feature-card">
                    <h3 style="margin-top: 0; margin-bottom: 0.5rem; font-size: 1.1rem;">💎 智能查询</h3>
                    <p style="margin: 0; font-size: 0.9rem;">自然语言转SQL，智能数据查询</p>
                </div>
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="feature-card">
                    <h3 style="margin-top: 0; margin-bottom: 0.5rem; font-size: 1.1rem;">📊 数据可视化</h3>
                    <p style="margin: 0; font-size: 0.9rem;">多样图表类型，直观数据展示</p>
                </div>
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="feature-card">
                    <h3 style="margin-top: 0; margin-bottom: 0.5rem; font-size: 1.1rem;">🎯 智能洞察</h3>
                    <p style="margin: 0; font-size: 0.9rem;">深度分析，专业商业洞察</p>
                </div>
                """)

        # 主要交互区域
        with gr.Row():
            with gr.Column(scale=2):
                # 聊天组件 - 紧凑设计
                chatbot = gr.Chatbot(
                    height=400,
                    label="💬 对话历史",
                    type="messages"
                )

                # 输入区域 - 紧凑设计
                with gr.Group():
                    msg = gr.Textbox(
                        placeholder="💭 请输入您的数据查询问题...",
                        label="",
                        lines=2,
                        max_lines=4,
                        show_label=False,
                        container=False
                    )
                    with gr.Row():
                        submit_btn = gr.Button(
                            "🚀 发送查询",
                            variant="primary",
                            scale=1
                        )
                        clear_btn = gr.Button(
                            "🗑️ 清空对话",
                            variant="secondary",
                            scale=1
                        )

            with gr.Column(scale=1):
                # 技术详情面板
                with gr.Accordion("🔧 技术详情", open=False):
                    sql_display = gr.Textbox(
                        label="📝 生成的SQL查询",
                        lines=6,
                        interactive=False,
                        placeholder="SQL查询将在这里显示..."
                    )
                    result_display = gr.Textbox(
                        label="📋 数据库返回结果",
                        lines=10,
                        interactive=False,
                        placeholder="查询结果将在这里显示..."
                    )

        # 示例查询区域 - 优化设计
        with gr.Row():
            with gr.Column():
                pass

                # 示例查询 - 保留必要示例
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML(
                            "<h4 style='margin-bottom: 1rem; color: var(--loreal-gold); font-size: 1.1rem;'>💎 精准查询</h4>")
                        gr.Examples(
                            examples=[
                                "查询订单号3c5db3f9729998569150adceca0fc0ad的详细信息",
                                "显示2024-10-30这天的所有订单信息",
                                "查询'芝麻开门男士滋养紧致眼部精华露'的所有销售记录",
                                "统计每个产品在10月份的销售总额和销售数量"
                            ],
                            inputs=msg
                        )

                    with gr.Column(scale=1):
                        gr.HTML(
                            "<h4 style='margin-bottom: 1rem; color: var(--loreal-gold); font-size: 1.1rem;'>🎨 视觉呈现</h4>")
                        gr.Examples(
                            examples=[
                                "绘制2024年10月21日到10月30日的每日销售额趋势图",
                                "可视化展示芝麻开门男士滋养紧致眼部精华露2024年10月的销量变化趋势",
                                "绘制各销售渠道的销售额占比饼图",
                                "展示销售额前15的城市销售情况"
                            ],
                            inputs=msg
                        )

                    with gr.Column(scale=1):
                        gr.HTML(
                            "<h4 style='margin-bottom: 1rem; color: var(--loreal-gold); font-size: 1.1rem;'>🔮 智慧洞察</h4>")
                        gr.Examples(
                            examples=[
                                "显示苏州狮山天街店铺的所有交易记录",
                                "统计江苏省苏州市的所有销售数据",
                                "查询一线城市的销售情况",
                                "展示不同城市等级的销售额对比柱状图"
                            ],
                            inputs=msg
                        )

        # 定义回调函数
        def user_input(user_message, history):
            # 处理用户输入 - 使用messages格式
            return "", history + [{"role": "user", "content": user_message}]

        # 定义回调函数
        def bot_response(history):
            # 获取最后一条用户消息
            user_message = history[-1]["content"]

            # 获取对话上下文
            context = dialogue_context.get_context_window()
            
            # 使用LLM判断对话类型并获取回答
            conv_type, answer = text2sql.llm.classify_conversation(user_message)

            # 记录用户消息到上下文
            dialogue_context.add_message(
                role="user",
                content=user_message,
                metadata={"type": conv_type}
            )

            # 如果是普通对话，直接返回回答
            if conv_type == "general":
                dialogue_context.add_message(
                    role="assistant",
                    content=answer,
                    metadata={"type": "general_response"}
                )
                history.append({"role": "assistant", "content": answer})
                return history, "", ""

            # 如果是数据查询，继续原有的处理逻辑
            if is_visualization_query(user_message):
                # 处理可视化查询
                df, viz_path, sql_query = text2viz.visualize(user_message)

                if viz_path and os.path.exists(viz_path):
                    summary = generate_data_summary(df)
                    db_result = df.head(10).to_string(index=False) if not df.empty else "无数据"

                    # 添加文本摘要回复
                    history.append({"role": "assistant", "content": summary})

                    # 追加图片消息
                    history.append({"role": "assistant", "content": {"path": viz_path}})

                    return history, sql_query, db_result
                else:
                    # 可视化失败，使用Text2SQL回退
                    response, sql_query, db_result = text2sql.query(user_message)
                    # 添加文本回复
                    history.append({"role": "assistant", "content": response})
                    return history, sql_query, db_result
            else:
                # 处理普通文本查询
                response, sql_query, db_result = text2sql.query(user_message)
                # 添加回复
                history.append({"role": "assistant", "content": response})
                return history, sql_query, db_result

        # 清空对话功能
        def clear_conversation():
            return [], "", "", ""

        # 设置事件处理
        msg.submit(user_input, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot_response, chatbot, [chatbot, sql_display, result_display]
        )
        submit_btn.click(user_input, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot_response, chatbot, [chatbot, sql_display, result_display]
        )
        clear_btn.click(
            clear_conversation,
            outputs=[chatbot, msg, sql_display, result_display]
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