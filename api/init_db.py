# 数据库初始化脚本

import sqlite3
import os
import sys

def init_database():
    """初始化数据库"""
    
    # 数据库文件路径
    db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    db_path = os.path.join(db_dir, 'ordering_system.db')
    
    # 创建data目录
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f'创建目录: {db_dir}')
    
    # 如果数据库已存在，删除
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f'删除旧数据库: {db_path}')
    
    # 读取SQL脚本
    sql_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'init-db.sql')
    
    if not os.path.exists(sql_file):
        print(f'错误: SQL脚本不存在: {sql_file}')
        return False
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # 执行SQL脚本
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 执行整个脚本
        cursor.executescript(sql_script)
        
        conn.commit()
        conn.close()
        
        print(f'数据库初始化成功: {db_path}')
        print('-' * 60)
        print('测试账号信息：')
        print('管理员 - 工号: ADMIN001, 密码: admin123')
        print('食堂人员 - 工号: STAFF001, 密码: staff123')
        print('员工 - 工号: EMP001-EMP010, 密码: user123')
        print('-' * 60)
        
        return True
    
    except Exception as e:
        print(f'数据库初始化失败: {str(e)}')
        return False


if __name__ == '__main__':
    print('=' * 60)
    print('集团员工内部用餐点餐平台 - 数据库初始化')
    print('=' * 60)
    
    if init_database():
        print('初始化完成！')
        sys.exit(0)
    else:
        print('初始化失败！')
        sys.exit(1)
