# 用户认证服务

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.helpers import get_db_connection, verify_password, dict_from_row
import config


class AuthService:
    """用户认证服务类"""
    
    def login(self, employee_id, password):
        """
        用户登录
        
        Args:
            employee_id (str): 员工工号
            password (str): 密码
        
        Returns:
            dict: 用户信息（不含密码）
        
        Raises:
            ValueError: 登录失败
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询用户
        cursor.execute('''
            SELECT id, employee_id, full_name, phone_number, department_id, role, is_active
            FROM users
            WHERE employee_id = ?
        ''', (employee_id,))
        
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            raise ValueError('用户不存在')
        
        # 检查用户状态
        if user['is_active'] != 1:
            conn.close()
            raise ValueError('用户已被禁用')
        
        # 验证密码
        cursor.execute('SELECT password FROM users WHERE employee_id = ?', (employee_id,))
        password_row = cursor.fetchone()
        conn.close()
        
        if not verify_password(password, password_row['password']):
            raise ValueError('密码错误')
        
        # 返回用户信息（不含密码）
        return dict_from_row(user)
    
    def get_user_info(self, user_id):
        """
        获取用户信息
        
        Args:
            user_id (int): 用户ID
        
        Returns:
            dict: 用户信息
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.employee_id, u.full_name, u.phone_number, 
                   u.department_id, d.name as department_name, u.role, u.is_active
            FROM users u
            LEFT JOIN departments d ON u.department_id = d.id
            WHERE u.id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        return dict_from_row(user)
