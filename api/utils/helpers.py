# 工具函数

import hashlib
import sqlite3
from datetime import datetime, time
from functools import wraps
from flask import request, jsonify
import config


def get_db_connection():
    """
    获取数据库连接
    
    Returns:
        sqlite3.Connection: 数据库连接对象
    """
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
    return conn


def hash_password(password):
    """
    密码加密
    
    Args:
        password (str): 明文密码
    
    Returns:
        str: 加密后的密码
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, hashed):
    """
    验证密码
    
    Args:
        password (str): 明文密码
        hashed (str): 加密后的密码
    
    Returns:
        bool: 密码是否正确
    """
    return hash_password(password) == hashed


def get_current_datetime():
    """
    获取当前日期时间
    
    Returns:
        str: 格式化的日期时间字符串 (YYYY-MM-DD HH:MM:SS)
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_current_date():
    """
    获取当前日期
    
    Returns:
        str: 格式化的日期字符串 (YYYY-MM-DD)
    """
    return datetime.now().strftime('%Y-%m-%d')


def get_current_time():
    """
    获取当前时间
    
    Returns:
        str: 格式化的时间字符串 (HH:MM:SS)
    """
    return datetime.now().strftime('%H:%M:%S')


def check_time_limit(meal_type, order_date):
    """
    检查是否在点餐时间限制内
    
    Args:
        meal_type (str): 餐次类型 (breakfast/lunch/dinner)
        order_date (str): 订餐日期 (YYYY-MM-DD)
    
    Returns:
        bool: True表示在时间内，False表示超时
    """
    now = datetime.now()
    order_datetime = datetime.strptime(order_date, '%Y-%m-%d')
    
    # 如果是未来日期，允许预订
    if order_datetime.date() > now.date():
        return True
    
    # 如果是当天，检查截止时间
    if order_datetime.date() == now.date():
        limit_time_str = config.MEAL_TIME_LIMITS.get(meal_type)
        if limit_time_str:
            limit_hour, limit_minute = map(int, limit_time_str.split(':'))
            limit_time = time(limit_hour, limit_minute)
            
            if now.time() < limit_time:
                return True
    
    return False


def generate_order_no():
    """
    生成订单号
    
    Returns:
        str: 订单号 (格式: ORD + 时间戳)
    """
    return f"ORD{datetime.now().strftime('%Y%m%d%H%M%S%f')}"


def success_response(data=None, message='success'):
    """
    成功响应
    
    Args:
        data: 响应数据
        message (str): 响应消息
    
    Returns:
        dict: 响应字典
    """
    return {
        'code': config.ERROR_SUCCESS,
        'message': message,
        'data': data
    }


def error_response(code, message, data=None):
    """
    错误响应
    
    Args:
        code (int): 错误码
        message (str): 错误消息
        data: 额外数据
    
    Returns:
        dict: 响应字典
    """
    return {
        'code': code,
        'message': message,
        'data': data
    }


def require_auth(f):
    """
    认证装饰器：要求用户登录
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 从请求头获取用户ID（简化实现，实际应使用JWT等）
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            return jsonify(error_response(config.ERROR_UNAUTHORIZED, '未登录')), 401
        
        # 将用户ID添加到kwargs
        kwargs['current_user_id'] = int(user_id)
        return f(*args, **kwargs)
    
    return decorated_function


def require_role(*roles):
    """
    角色权限装饰器
    
    Args:
        *roles: 允许的角色列表
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = request.headers.get('X-User-Id')
            if not user_id:
                return jsonify(error_response(config.ERROR_UNAUTHORIZED, '未登录')), 401
            
            # 查询用户角色
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT role FROM users WHERE id = ? AND is_active = 1', (user_id,))
            user = cursor.fetchone()
            conn.close()
            
            if not user:
                return jsonify(error_response(config.ERROR_USER_NOT_FOUND, '用户不存在')), 404
            
            if user['role'] not in roles:
                return jsonify(error_response(config.ERROR_FORBIDDEN, '无权限访问')), 403
            
            kwargs['current_user_id'] = int(user_id)
            kwargs['current_user_role'] = user['role']
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def dict_from_row(row):
    """
    将sqlite3.Row对象转换为字典
    
    Args:
        row: sqlite3.Row对象
    
    Returns:
        dict: 字典对象
    """
    if row is None:
        return None
    return dict(zip(row.keys(), row))


def list_from_rows(rows):
    """
    将sqlite3.Row列表转换为字典列表
    
    Args:
        rows: sqlite3.Row对象列表
    
    Returns:
        list: 字典列表
    """
    return [dict_from_row(row) for row in rows]
