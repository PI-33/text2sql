# L'Oréal 数据洞察助手 (L'Oréal Data Insight Assistant)

一个基于自然语言的智能数据分析和可视化系统，让数据分析变得简单直观。

[![在 ModelScope 中体验](https://img.shields.io/badge/在_ModelScope_中体验-blue)](https://www.modelscope.cn/studios/Pi33ymym/Loreal_Insight_Agent)

## 🌟 功能特点

- 💬 自然语言查询：使用日常语言进行数据查询，无需编写 SQL
- 📊 智能可视化：自动生成数据可视化图表
- 🎯 深度分析：提供专业的数据分析和商业洞察
- 🔄 上下文理解：支持多轮对话，实现连续查询
- 📱 友好界面：简洁直观的用户界面，支持移动端访问

## 🚀 快速开始

### 环境要求

- Python 3.10.x
- SQLite3
- 其他依赖见 requirements.txt

### 安装步骤

1. 克隆项目

```bash
git clone https://www.modelscope.cn/studios/Pi33ymym/Loreal_Insight_Agent.git
cd Loreal_Insight_Agent
```

2. 创建并激活虚拟环境（推荐）

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

4. 配置环境变量
   创建 `.env` 文件并配置以下变量：

```
OPENAI_API_KEY=your_api_key_here
```

### 启动应用

```bash
python app.py
```

启动后访问 http://localhost:7860 即可使用。

### 使用 Docker（可选）

1. 构建镜像

```bash
docker-compose build
```

2. 启动服务

```bash
docker-compose up -d
```

## 📝 使用示例

### 精准查询

- 查询特定订单：`查询订单号3c5db3f9729998569150adceca0fc0ad的详细信息`
- 查询日期数据：`显示2024-10-30这天的所有订单信息`
- 产品查询：`查询'芝麻开门男士滋养紧致眼部精华露'的所有销售记录`

### 数据可视化

- 趋势分析：`绘制2024年10月21日到10月30日的每日销售额趋势图`
- 产品分析：`可视化展示芝麻开门男士滋养紧致眼部精华露2024年10月的销量变化趋势`
- 渠道分析：`绘制各销售渠道的销售额占比饼图`

## 🔗 在线体验

访问我们的 [ModelScope 体验页面](https://www.modelscope.cn/studios/Pi33ymym/Loreal_Insight_Agent) 立即开始使用！
