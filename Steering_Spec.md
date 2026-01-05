# Steering Spec - 集团员工内部用餐点餐平台

## 1. 项目概述

### 1.1 项目名称
集团员工内部用餐点餐平台（Employee Meal Ordering System）

### 1.2 项目目标
为企业集团开发统一的员工用餐点餐平台，支持多食堂管理、在线点餐、菜单管理、订单管理等功能。

### 1.3 项目范围
- 菜单管理模块（菜品管理、菜单配置）
- 员工点餐模块（选择食堂、查看菜单、点餐、预订）
- 订单管理模块（订单查询、修改、取消、统计）
- 后厨备餐模块（备餐看板、库存管理）
- 评价反馈模块（菜品评分、意见反馈）
- 系统管理模块（食堂、人员、用户、部门管理）

---

## 2. 语言规范

### 2.1 文档语言规范
**规范**: 所有文档必须使用中文编写

**适用范围**:
- README.md
- 需求文档
- 设计文档
- API文档
- 用户手册
- 部署文档
- 其他所有项目文档

**示例**:
```markdown
# 集团员工内部用餐点餐平台

## 项目简介
本项目是一个为企业集团开发的员工用餐点餐平台...
```

### 2.2 代码注释语言规范
**规范**: 所有代码注释必须使用中文

**适用范围**:
- 函数注释
- 类注释
- 模块注释
- 行内注释
- TODO注释

**示例**:
```python
# 用户服务类
class UserService:
    """
    用户服务类，负责用户相关的业务逻辑处理
    
    Attributes:
        db_path: 数据库文件路径
    """
    
    def create_user(self, name, employee_id, department_id):
        """
        创建新用户
        
        Args:
            name: 用户姓名
            employee_id: 员工工号
            department_id: 部门ID
            
        Returns:
            int: 新创建用户的ID
        """
        # 验证员工工号是否已存在
        if self._check_employee_id_exists(employee_id):
            raise ValueError("员工工号已存在")
        
        # TODO: 添加更多验证逻辑
        pass
```

### 2.3 代码标识符语言规范
**规范**: 所有代码标识符必须使用英文

**适用范围**:
- 变量名
- 函数名
- 类名
- 模块名
- 常量名
- 数据库表名
- 数据库字段名

**命名规范**:
- 类名: PascalCase（如：UserService、OrderManager）
- 函数名: snake_case（如：create_user、get_order_list）
- 变量名: snake_case（如：user_id、order_status）
- 常量名: UPPER_SNAKE_CASE（如：MAX_ORDER_COUNT、DEFAULT_TIMEOUT）
- 模块名: snake_case（如：user_service.py、order_handler.py）

**示例**:
```python
# 正确示例
class CanteenService:
    MAX_CANTEEN_COUNT = 100
    
    def get_canteen_list(self, status=None):
        canteen_list = []
        return canteen_list

# 错误示例（不要使用中文标识符）
class 食堂服务:  # ❌ 错误
    最大食堂数量 = 100  # ❌ 错误
    
    def 获取食堂列表(self):  # ❌ 错误
        食堂列表 = []  # ❌ 错误
        return 食堂列表
```

### 2.4 数据库命名规范
**规范**: 数据库表名和字段名使用英文，采用snake_case命名

**示例**:
```sql
-- 表名使用英文复数形式
CREATE TABLE canteens (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    phone TEXT,
    created_at TEXT NOT NULL
);

-- 字段名使用snake_case
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    employee_id TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    department_id INTEGER,
    phone_number TEXT,
    wechat_openid TEXT,  -- 预留企业微信字段
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL
);
```

### 2.5 API端点命名规范
**规范**: API端点使用英文，采用RESTful风格

**示例**:
```
GET    /api/canteens           # 获取食堂列表
POST   /api/canteens           # 创建食堂
GET    /api/canteens/{id}      # 获取食堂详情
PUT    /api/canteens/{id}      # 更新食堂
DELETE /api/canteens/{id}      # 删除食堂

GET    /api/orders             # 获取订单列表
POST   /api/orders             # 创建订单
GET    /api/orders/{id}        # 获取订单详情
PUT    /api/orders/{id}        # 修改订单
DELETE /api/orders/{id}        # 取消订单
```

---

## 3. 环境规范

### 3.1 Python版本规范
**规范**: 必须使用Python 3.12版本

**验证命令**:
```bash
python --version
# 输出: Python 3.12.x
```

### 3.2 虚拟环境规范
**规范**: 必须使用Conda创建名为"ordering-system"的虚拟环境

**环境名称**: ordering-system

**创建命令**:
```bash
conda create -n ordering-system python=3.12 -y
```

**激活命令**:
```bash
conda activate ordering-system
```

**环境配置文件**: environment.yml
```yaml
name: ordering-system
channels:
  - defaults
dependencies:
  - python=3.12
  - pip
  - pip:
    - flask>=3.0.0
    - flask-cors>=4.0.0
    - 其他依赖...
```

### 3.3 数据库规范
**规范**: 必须使用SQLite数据库

**数据库文件位置**: `./data/ordering_system.db`

**操作方式**: 使用原生SQL，不使用ORM

**示例**:
```python
import sqlite3

# 连接数据库
conn = sqlite3.connect('./data/ordering_system.db')
cursor = conn.cursor()

# 执行查询（使用原生SQL）
cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
user = cursor.fetchone()

# 关闭连接
conn.close()
```

**禁止使用**: SQLAlchemy、Django ORM、Peewee等ORM框架

### 3.4 缓存规范
**规范**: 不使用任何缓存机制

**说明**: 为简化架构，本项目不使用Redis、Memcached等缓存系统

---

## 4. 架构规范

### 4.1 服务架构
**规范**: 系统分为3个独立服务

**服务列表**:
1. **api**: 后端API服务
   - 端口: 5000
   - 职责: 提供RESTful API
   - 技术: Python + Flask

2. **admin-web**: 管理端前端服务
   - 端口: 8080
   - 职责: 提供管理员和食堂人员使用的Web界面
   - 技术: HTML + CSS + JavaScript
   - 访问方式: PC浏览器

3. **user-web**: 员工端前端服务
   - 端口: 8081
   - 职责: 提供员工使用的H5页面
   - 技术: HTML + CSS + JavaScript
   - 访问方式: 移动端浏览器

**目录结构**:
```
ordering-system/
├── api/                    # 后端API服务
│   ├── app.py             # 应用入口
│   ├── services/          # 业务逻辑层
│   ├── handlers/          # 请求处理层
│   ├── utils/             # 工具函数
│   └── config.py          # 配置文件
├── admin-web/             # 管理端前端
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── assets/
├── user-web/              # 员工端前端
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── assets/
├── data/                  # 数据目录
│   └── ordering_system.db
├── init-db.sql            # 数据库初始化脚本
├── quick-start.sh         # 一键启动脚本
├── quick-stop.sh          # 一键停止脚本
├── environment.yml        # Conda环境配置
└── README.md              # 项目文档
```

### 4.2 代码分层规范
**规范**: 后端API采用分层架构

**层次结构**:
```
API层 (handlers) -> 业务逻辑层 (services) -> 数据访问层 (database)
```

**示例**:
```python
# handlers/order_handler.py - API层
@app.route('/api/orders', methods=['POST'])
def create_order():
    """创建订单接口"""
    data = request.json
    order_service = OrderService()
    order_id = order_service.create_order(data)
    return jsonify({'order_id': order_id})

# services/order_service.py - 业务逻辑层
class OrderService:
    """订单业务逻辑"""
    
    def create_order(self, data):
        """创建订单"""
        # 1. 验证数据
        self._validate_order_data(data)
        
        # 2. 检查时间限制
        self._check_time_limit(data['meal_type'])
        
        # 3. 检查库存
        self._check_stock(data['items'])
        
        # 4. 创建订单并扣减库存（事务）
        return self._save_order_and_update_stock(data)
```

### 4.3 错误处理规范
**规范**: 统一的错误处理和响应格式

**成功响应格式**:
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "order_id": 123
    }
}
```

**错误响应格式**:
```json
{
    "code": 1001,
    "message": "已超过点餐时间",
    "data": null
}
```

**错误码定义**:
```python
# 系统错误 (1000-1999)
ERROR_SYSTEM = 1000
ERROR_DATABASE = 1001

# 业务错误 (2000-2999)
ERROR_TIME_LIMIT = 2001  # 超过时间限制
ERROR_DUPLICATE_ORDER = 2002  # 重复订单
ERROR_INSUFFICIENT_STOCK = 2003  # 库存不足

# 权限错误 (3000-3999)
ERROR_UNAUTHORIZED = 3001  # 未授权
ERROR_FORBIDDEN = 3002  # 无权限
```

---

## 5. 角色与权限规范

### 5.1 角色定义
**规范**: 系统支持3种角色

**角色列表**:
1. **员工（Employee）**
   - 角色代码: `employee`
   - 权限: 点餐、查看订单、修改/取消订单、评价、反馈

2. **食堂人员（Canteen Staff）**
   - 角色代码: `canteen_staff`
   - 权限: 管理菜品、管理菜单、查看订单、查看统计、备餐看板
   - 限制: 只能管理所属食堂的数据

3. **系统管理员（System Admin）**
   - 角色代码: `admin`
   - 权限: 所有功能
   - 包括: 系统管理、用户管理、食堂管理、查看所有数据

### 5.2 权限检查规范
**规范**: 所有需要权限的接口必须进行权限检查

**示例**:
```python
from functools import wraps

def require_role(*roles):
    """角色权限装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 获取当前用户角色
            current_role = get_current_user_role()
            
            # 检查角色
            if current_role not in roles:
                return jsonify({
                    'code': ERROR_FORBIDDEN,
                    'message': '无权限访问',
                    'data': None
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 使用示例
@app.route('/api/admin/users', methods=['GET'])
@require_role('admin')
def get_users():
    """获取用户列表（仅管理员）"""
    pass
```

---

## 6. 业务规则规范

### 6.1 时间规则
**规范**: 点餐截止时间

| 餐次 | 截止时间 | 说明 |
|------|---------|------|
| 早餐 | 07:30 | 当天早餐7:30前可点 |
| 午餐 | 11:00 | 当天午餐11:00前可点 |
| 晚餐 | 17:00 | 当天晚餐17:00前可点 |

**预订规则**: 只能预订明天或之后的餐次

**实现示例**:
```python
from datetime import datetime, time

def check_order_time_limit(meal_type, order_date):
    """
    检查是否在点餐时间内
    
    Args:
        meal_type: 餐次类型（breakfast/lunch/dinner）
        order_date: 订餐日期（YYYY-MM-DD）
    
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
        time_limits = {
            'breakfast': time(7, 30),
            'lunch': time(11, 0),
            'dinner': time(17, 0)
        }
        
        limit_time = time_limits.get(meal_type)
        if limit_time and now.time() < limit_time:
            return True
    
    return False
```

### 6.2 订单规则
**规范**: 订单业务规则

1. **唯一性规则**: 每个员工每个餐次只能有一个有效订单
2. **修改规则**: 只能在截止时间前修改订单
3. **取消规则**: 只能在截止时间前取消订单
4. **状态流转规则**: 已下单 -> 已取消 或 已完成

**订单状态**:
```python
ORDER_STATUS_PLACED = 'placed'      # 已下单
ORDER_STATUS_CANCELLED = 'cancelled'  # 已取消
ORDER_STATUS_COMPLETED = 'completed'  # 已完成
```

### 6.3 库存规则
**规范**: 库存管理规则

1. **实时扣减**: 下单时立即扣减库存
2. **退回规则**: 取消订单时退回库存
3. **调整规则**: 修改订单时先退回再扣减
4. **售罄规则**: 库存为0时标记为"已售罄"

**实现要求**: 使用数据库事务保证原子性

---

## 7. 数据规范

### 7.1 日期时间格式
**规范**: 统一使用ISO 8601格式

**格式定义**:
- 日期: `YYYY-MM-DD` (如: 2025-01-15)
- 时间: `HH:MM:SS` (如: 14:30:00)
- 日期时间: `YYYY-MM-DD HH:MM:SS` (如: 2025-01-15 14:30:00)

**示例**:
```python
from datetime import datetime

# 获取当前时间
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 获取当前日期
today = datetime.now().strftime('%Y-%m-%d')
```

### 7.2 状态字段规范
**规范**: 状态字段使用字符串类型，采用英文小写加下划线

**示例**:
```python
# 订单状态
ORDER_STATUS = {
    'placed': '已下单',
    'cancelled': '已取消',
    'completed': '已完成'
}

# 菜品状态
DISH_STATUS = {
    'active': '已上架',
    'inactive': '已下架'
}

# 用户状态
USER_STATUS = {
    'active': '启用',
    'inactive': '禁用'
}
```

### 7.3 布尔值规范
**规范**: 数据库中布尔值使用INTEGER类型（0/1）

**示例**:
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    is_active INTEGER DEFAULT 1,  -- 1表示启用，0表示禁用
    is_deleted INTEGER DEFAULT 0  -- 1表示已删除，0表示未删除
);
```

```python
# Python中的处理
is_active = 1 if user_active else 0
```

---

## 8. 安全规范

### 8.1 SQL注入防护
**规范**: 必须使用参数化查询

**正确示例**:
```python
# ✅ 正确：使用参数化查询
cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))

# ✅ 正确：多个参数
cursor.execute(
    'INSERT INTO orders (user_id, canteen_id, meal_type) VALUES (?, ?, ?)',
    (user_id, canteen_id, meal_type)
)
```

**错误示例**:
```python
# ❌ 错误：字符串拼接（存在SQL注入风险）
cursor.execute(f'SELECT * FROM users WHERE id = {user_id}')

# ❌ 错误：格式化字符串
cursor.execute('SELECT * FROM users WHERE name = "%s"' % name)
```

### 8.2 密码安全规范
**规范**: 密码必须加密存储

**示例**:
```python
import hashlib

def hash_password(password):
    """密码加密"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """密码验证"""
    return hash_password(password) == hashed
```

### 8.3 输入验证规范
**规范**: 所有用户输入必须进行验证

**示例**:
```python
def validate_order_data(data):
    """验证订单数据"""
    # 必填字段检查
    required_fields = ['canteen_id', 'meal_type', 'order_date', 'items']
    for field in required_fields:
        if field not in data:
            raise ValueError(f'缺少必填字段: {field}')
    
    # 数据类型检查
    if not isinstance(data['canteen_id'], int):
        raise ValueError('食堂ID必须是整数')
    
    # 数据范围检查
    if data['meal_type'] not in ['breakfast', 'lunch', 'dinner']:
        raise ValueError('无效的餐次类型')
    
    return True
```

---

## 9. 测试规范

### 9.1 测试要求
**规范**: 完成基本的功能测试验证

**测试范围**:
1. 菜品管理功能测试
2. 菜单管理功能测试
3. 点餐功能测试（包括时间限制）
4. 订单管理功能测试（查看、修改、取消）
5. 权限控制测试
6. 库存扣减和退回测试

### 9.2 测试数据
**规范**: 提供初始测试数据

**测试数据包括**:
- 3个测试食堂
- 10个测试员工
- 2个食堂人员
- 1个系统管理员
- 20个测试菜品
- 当天和未来3天的测试菜单

---

## 10. 部署规范

### 10.1 部署脚本规范
**规范**: 提供一键启动和停止脚本

**quick-start.sh**: 启动所有服务
```bash
#!/bin/bash
# 启动所有服务

# 激活Conda环境
source $(conda info --base)/etc/profile.d/conda.sh
conda activate ordering-system

# 初始化数据库（如果不存在）
if [ ! -f "./data/ordering_system.db" ]; then
    python api/init_db.py
fi

# 启动API服务
cd api && python app.py &
API_PID=$!

# 启动管理端
cd ../admin-web && python -m http.server 8080 &
ADMIN_PID=$!

# 启动员工端
cd ../user-web && python -m http.server 8081 &
USER_PID=$!

# 保存进程ID
echo $API_PID > ../pids/api.pid
echo $ADMIN_PID > ../pids/admin.pid
echo $USER_PID > ../pids/user.pid

echo "所有服务已启动"
```

**quick-stop.sh**: 停止所有服务
```bash
#!/bin/bash
# 停止所有服务

# 读取进程ID并终止
if [ -f "./pids/api.pid" ]; then
    kill $(cat ./pids/api.pid)
    rm ./pids/api.pid
fi

if [ -f "./pids/admin.pid" ]; then
    kill $(cat ./pids/admin.pid)
    rm ./pids/admin.pid
fi

if [ -f "./pids/user.pid" ]; then
    kill $(cat ./pids/user.pid)
    rm ./pids/user.pid
fi

echo "所有服务已停止"
```

### 10.2 环境配置规范
**规范**: 提供environment.yml配置文件

**文件内容**:
```yaml
name: ordering-system
channels:
  - defaults
  - conda-forge
dependencies:
  - python=3.12
  - pip
  - pip:
    - flask>=3.0.0
    - flask-cors>=4.0.0
```

---

## 11. 文档规范

### 11.1 README.md规范
**规范**: README.md必须包含以下内容

**必需章节**:
1. 项目简介
2. 功能特性
3. 技术架构
4. 环境要求
5. 安装部署
6. 使用说明
7. 目录结构
8. API文档
9. 常见问题

### 11.2 代码注释规范
**规范**: 关键函数和类必须有注释

**函数注释示例**:
```python
def create_order(user_id, canteen_id, meal_type, order_date, items):
    """
    创建订单
    
    Args:
        user_id (int): 用户ID
        canteen_id (int): 食堂ID
        meal_type (str): 餐次类型（breakfast/lunch/dinner）
        order_date (str): 订餐日期（YYYY-MM-DD）
        items (list): 订单项列表，每项包含dish_id和quantity
    
    Returns:
        int: 新创建的订单ID
    
    Raises:
        ValueError: 当数据验证失败时
        RuntimeError: 当创建订单失败时
    """
    pass
```

---

## 12. 企业微信集成预留

### 12.1 数据库字段预留
**规范**: 预留企业微信相关字段，本期不实现

**预留字段**:
```sql
CREATE TABLE users (
    -- 基本字段
    id INTEGER PRIMARY KEY,
    employee_id TEXT NOT NULL,
    
    -- 企业微信字段（预留）
    wechat_openid TEXT,      -- 企业微信OpenID
    wechat_userid TEXT,      -- 企业微信UserID
    wechat_department TEXT,  -- 企业微信部门
    
    -- 其他字段...
);
```

### 12.2 接口预留
**规范**: 预留企业微信登录接口，本期返回模拟数据

**接口定义**:
```
POST /api/auth/wechat/login
```

---

## 13. 版本控制规范

### 13.1 Git提交规范
**规范**: Git提交信息使用中文，遵循以下格式

**格式**: `[类型] 简短描述`

**类型定义**:
- `[功能]`: 新增功能
- `[修复]`: Bug修复
- `[文档]`: 文档更新
- `[重构]`: 代码重构
- `[测试]`: 测试相关
- `[配置]`: 配置文件修改

**示例**:
```
[功能] 实现订单创建功能
[修复] 修复库存扣减并发问题
[文档] 更新README部署说明
[重构] 优化订单服务代码结构
```

---

## 14. 质量检查清单

### 14.1 代码质量
- ✅ 所有代码标识符使用英文
- ✅ 所有注释使用中文
- ✅ 遵循Python PEP 8规范
- ✅ 无硬编码的敏感信息
- ✅ 使用参数化查询防止SQL注入

### 14.2 功能完整性
- ✅ 所有CSV中的功能已实现
- ✅ 三种角色的权限控制正确
- ✅ 时间限制逻辑正确
- ✅ 库存管理逻辑正确

### 14.3 文档完整性
- ✅ README.md完整
- ✅ 数据库初始化脚本完整
- ✅ 一键启动停止脚本可用
- ✅ Conda环境配置文件正确

### 14.4 部署可用性
- ✅ 可以在Conda环境中正常启动
- ✅ 数据库初始化正常
- ✅ 三个服务都可以正常访问
- ✅ 基本功能测试通过

---

## 附录

### A. 技术栈总览
- **后端**: Python 3.12 + Flask
- **前端**: HTML + CSS + JavaScript
- **数据库**: SQLite
- **环境**: Conda (ordering-system)

### B. 端口分配
- API服务: 5000
- 管理端: 8080
- 员工端: 8081

### C. 关键约束
- 不使用ORM
- 不使用缓存
- 不实现支付
- 不实现取餐核销
- 不实现企业微信集成（仅预留）
