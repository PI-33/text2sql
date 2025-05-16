# Text2SQL 自然语言查询工具

这个工具使用大型语言模型（LLM）将自然语言问题转换为SQL查询，并以自然语言方式返回结果。

## 功能特点

- 自然语言转SQL：用户可以用普通语言提问，无需编写SQL
- 格式化输出：结果以清晰易读的格式显示
- 简洁回答：返回简洁、直接的自然语言答案
- 方便的命令行界面：支持通过命令行直接查询

## 安装要求

确保已安装以下Python库：
```
langchain
langchain_core
langchain_community
openai
pandas
```

您可以使用以下命令安装所需依赖：
```
pip install langchain langchain-core langchain-community openai pandas
```

## 使用方法

### 直接在脚本中使用

```python
from text2sql import run_query

# 运行查询并获取结果
response = run_query("2024-10-21 到 2024-10-25的平均每日销售额")
print(response)
```

### 使用测试脚本

我们提供了一个测试脚本，让您可以方便地尝试不同查询：

1. 直接运行测试脚本并选择预设查询：
```
python test_text2sql.py
```

2. 传入自定义查询：
```
python test_text2sql.py "2024年10月销售额最高的产品是什么"
```

## 示例查询

以下是一些您可以尝试的示例查询：

- "2024-10-21 到 2024-10-25的平均每日销售额"
- "10月销售额最高的前5个产品是什么"
- "江苏省的销售总额是多少"
- "不同渠道的销售额比较"
- "10月21日到10月30日每天的销售额趋势"

## 输出示例

```
==================================================
问题: 2024-10-21 到 2024-10-25的平均每日销售额
==================================================
2024-10-21到2024-10-25期间的平均每日销售额为213,076.16元。
==================================================
```

## 开发说明

- 该工具使用ModelScope的Qwen模型作为底层大语言模型
- 使用LangChain框架构建查询处理管道
- 数据库配置在`text2sql.py`文件的开头部分

## 自定义与扩展

如果您需要连接其他数据库，只需更改以下行：

```python
db = SQLDatabase.from_uri("sqlite:///data/order_database.db")
```

例如，连接MySQL数据库：

```python
db = SQLDatabase.from_uri("mysql+pymysql://username:password@localhost/database_name")
```
