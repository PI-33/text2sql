# Text2SQL 自然语言查询工具

这个工具使用大型语言模型（LLM）将自然语言问题转换为 SQL 查询，并以自然语言方式返回结果。

## 功能特点

- 自然语言转 SQL：用户可以用普通语言提问，无需编写 SQL
- 格式化输出：结果以清晰易读的格式显示
- 简洁回答：返回简洁、直接的自然语言答案
- 方便的命令行界面：支持通过命令行直接查询

## 安装要求

确保已安装以下 Python 库：

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

- "2024-10-21 到 2024-10-25 的平均每日销售额"
- "10 月销售额最高的前 5 个产品是什么"
- "江苏省的销售总额是多少"
- "不同渠道的销售额比较"
- "10 月 21 日到 10 月 30 日每天的销售额趋势"

## 输出示例

```
==================================================
问题: 2024-10-21 到 2024-10-25的平均每日销售额
==================================================
2024-10-21到2024-10-25期间的平均每日销售额为213,076.16元。
==================================================
```

## 开发说明

- 该工具使用 ModelScope 的 Qwen 模型作为底层大语言模型
- 使用 LangChain 框架构建查询处理管道
- 数据库配置在`text2sql.py`文件的开头部分

## 自定义与扩展

如果您需要连接其他数据库，只需更改以下行：

```python
db = SQLDatabase.from_uri("sqlite:///data/order_database.db")
```

例如，连接 MySQL 数据库：

```python
db = SQLDatabase.from_uri("mysql+pymysql://username:password@localhost/database_name")
```

## 数据介绍

create_table_query = """
CREATE TABLE IF NOT EXISTS new_fact_order_detail (
order_no VARCHAR(255), -- 订单编号（核心主键）
order_time TIMESTAMP, -- 订单时间（精确到时间）
order_date DATE, -- 订单日期（分析趋势或聚合）
brand_code VARCHAR(255), -- 品牌代码（关键分类维度）
program_code VARCHAR(255), -- 项目代码（分类维度）
order_type INT, -- 订单类型（正单/退单等）
sales DECIMAL(18,2), -- 销售额（核心指标）
item_qty INT, -- 商品数量（核心指标）
item_price DECIMAL(18,2), -- 单价（单项分析）
channel VARCHAR(255), -- 渠道（一级分类）
subchannel VARCHAR(255), -- 子渠道（二级分类）
sub_subchannel VARCHAR(255), -- 子渠道-细分（三级分类）
material_code VARCHAR(255), -- 产品代码（SKU 分析）
material_name_cn VARCHAR(255), -- 产品名称（易读性）
material_type VARCHAR(255), -- 产品类型（分类维度）
merged_c_code VARCHAR(255), -- 顾客编号（客户行为分析）
tier_code VARCHAR(255), -- 会员等级代码（用户分层）
first_order_date DATE, -- 首单日期（客户生命周期）
is_mtd_active_member_flag INT, -- MTD 活跃客户标记（近期活跃分析）
ytd_active_arr VARCHAR(255), -- YTD 活跃标记（年度活跃分析）
r12_active_arr VARCHAR(255), -- R12 活跃标记（年度活跃分析）
manager_counter_code VARCHAR(255), -- 管理门店代码（业务归属）
ba_code VARCHAR(255), -- BA 编号（关联员工表现）
province_name VARCHAR(255), -- 省份（地理维度）
line_city_name VARCHAR(255), -- 城市名称（地理维度）
line_city_level VARCHAR(255), -- 城市等级（地理维度）
store_no VARCHAR(255), -- 柜台编号（销售点）
terminal_name VARCHAR(255), -- 门店名称（易读性）
terminal_code VARCHAR(255), -- 门店代码（具体标识）
terminal_region VARCHAR(255), -- 区域（业务区域维度）
default_flag INT -- 特殊订单标记（异常分析）
);
"""
