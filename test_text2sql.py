#!/usr/bin/env python3
import sys
from text2sql import run_query

def main():
    """
    简单的测试脚本，用于演示改进后的text2sql功能
    """
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 从命令行获取查询
        query = " ".join(sys.argv[1:])
    else:
        # 预设的示例查询
        print("未提供查询参数，使用默认查询示例...")
        print("使用方法: python test_text2sql.py \"你的SQL问题\"")
        print("\n示例查询:")
        queries = [
            "2024-10-21 到 2024-10-25的平均每日销售额",
            "10月销售额最高的前5个产品是什么",
            "江苏省的销售总额是多少"
        ]

        # 让用户选择一个示例查询
        print("选择一个示例查询:")
        for i, q in enumerate(queries, 1):
            print(f"{i}. {q}")

        try:
            choice = int(input("\n请输入选择 (1-3): ").strip())
            if 1 <= choice <= len(queries):
                query = queries[choice-1]
            else:
                print("无效选择，使用第一个示例查询")
                query = queries[0]
        except ValueError:
            print("无效输入，使用第一个示例查询")
            query = queries[0]

    # 运行查询
    print(f"\n正在处理查询: {query}")
    run_query(query)

if __name__ == "__main__":
    main()
