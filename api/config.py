# API配置文件

import os

# 数据库配置
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'ordering_system.db')

# API配置
API_HOST = '0.0.0.0'
API_PORT = 8082
DEBUG = True

# 餐次时间限制
MEAL_TIME_LIMITS = {
    'breakfast': '07:30',
    'lunch': '11:00',
    'dinner': '17:00'
}

# 订单状态
ORDER_STATUS_PLACED = 'placed'      # 已下单
ORDER_STATUS_CANCELLED = 'cancelled'  # 已取消
ORDER_STATUS_COMPLETED = 'completed'  # 已完成

# 菜品状态
DISH_STATUS_ACTIVE = 'active'      # 已上架
DISH_STATUS_INACTIVE = 'inactive'  # 已下架

# 用户角色
ROLE_EMPLOYEE = 'employee'         # 员工
ROLE_CANTEEN_STAFF = 'canteen_staff'  # 食堂人员
ROLE_ADMIN = 'admin'               # 系统管理员

# 错误码
ERROR_SUCCESS = 0
ERROR_SYSTEM = 1000
ERROR_DATABASE = 1001
ERROR_INVALID_PARAM = 1002

ERROR_TIME_LIMIT = 2001  # 超过时间限制
ERROR_DUPLICATE_ORDER = 2002  # 重复订单
ERROR_INSUFFICIENT_STOCK = 2003  # 库存不足
ERROR_ORDER_NOT_FOUND = 2004  # 订单不存在
ERROR_CANNOT_MODIFY = 2005  # 不能修改

ERROR_UNAUTHORIZED = 3001  # 未授权
ERROR_FORBIDDEN = 3002  # 无权限
ERROR_USER_NOT_FOUND = 3003  # 用户不存在
ERROR_INVALID_PASSWORD = 3004  # 密码错误
