import sqlite3
import pandas as pd

# 连接到SQLite数据库（如果数据库不存在，则会自动创建）
conn = sqlite3.connect('./data/order_database.db')
cursor = conn.cursor()

# 创建表结构
create_table_query = """
CREATE TABLE IF NOT EXISTS new_fact_order_detail (
    order_no VARCHAR(255),               -- 订单编号（核心主键）
    order_time TIMESTAMP,                -- 订单时间（精确到时间）
    order_date DATE,                     -- 订单日期（分析趋势或聚合）
    brand_code VARCHAR(255),             -- 品牌代码（关键分类维度）
    program_code VARCHAR(255),           -- 项目代码（分类维度）
    order_type INT,                      -- 订单类型（正单/退单等）
    sales DECIMAL(18,2),                 -- 销售额（核心指标）
    item_qty INT,                        -- 商品数量（核心指标）
    item_price DECIMAL(18,2),            -- 单价（单项分析）
    channel VARCHAR(255),                -- 渠道（一级分类）
    subchannel VARCHAR(255),             -- 子渠道（二级分类）
    sub_subchannel VARCHAR(255),         -- 子渠道-细分（三级分类）
    material_code VARCHAR(255),          -- 产品代码（SKU分析）
    material_name_cn VARCHAR(255),       -- 产品名称（易读性）
    material_type VARCHAR(255),          -- 产品类型（分类维度）
    merged_c_code VARCHAR(255),          -- 顾客编号（客户行为分析）
    tier_code VARCHAR(255),              -- 会员等级代码（用户分层）
    first_order_date DATE,               -- 首单日期（客户生命周期）
    is_mtd_active_member_flag INT,       -- MTD活跃客户标记（近期活跃分析）
    ytd_active_arr VARCHAR(255),         -- YTD活跃标记（年度活跃分析）
    r12_active_arr VARCHAR(255),         -- R12活跃标记（年度活跃分析）
    manager_counter_code VARCHAR(255),   -- 管理门店代码（业务归属）
    ba_code VARCHAR(255),                -- BA编号（关联员工表现）
    province_name VARCHAR(255),          -- 省份（地理维度）
    line_city_name VARCHAR(255),         -- 城市名称（地理维度）
    line_city_level VARCHAR(255),        -- 城市等级（地理维度）
    store_no VARCHAR(255),               -- 柜台编号（销售点）
    terminal_name VARCHAR(255),          -- 门店名称（易读性）
    terminal_code VARCHAR(255),          -- 门店代码（具体标识）
    terminal_region VARCHAR(255),        -- 区域（业务区域维度）
    default_flag INT                     -- 特殊订单标记（异常分析）
);
"""

# 执行创建表的SQL语句
cursor.execute(create_table_query)
conn.commit()

# 读取CSV文件
csv_file_path = './data/data.csv'  # 替换为你的CSV文件路径
# 定义列名
column_names = [
    "order_no", "order_time", "order_date", "brand_code", "program_code", "order_type",
    "sales", "item_qty", "item_price", "channel", "subchannel", "sub_subchannel",
    "material_code", "material_name_cn", "material_type", "merged_c_code", "tier_code",
    "first_order_date", "is_mtd_active_member_flag", "ytd_active_arr", "r12_active_arr",
    "manager_counter_code", "ba_code", "province_name", "line_city_name", "line_city_level",
    "store_no", "terminal_name", "terminal_code", "terminal_region", "default_flag"
]

# 读取CSV文件，指定列名
df = pd.read_csv(csv_file_path, encoding='gbk', sep=';', header=None, names=column_names)

# 将数据插入到SQLite表中
df.to_sql('new_fact_order_detail', conn, if_exists='append', index=False)

# 关闭数据库连接
conn.close()

print("数据已成功导入到SQLite数据库中。")
