-- 集团员工内部用餐点餐平台 - 数据库初始化脚本

-- ============================================
-- 1. 部门表
-- ============================================
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (parent_id) REFERENCES departments(id)
);

-- ============================================
-- 2. 食堂表
-- ============================================
CREATE TABLE IF NOT EXISTS canteens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    address TEXT,
    phone TEXT,
    status TEXT DEFAULT 'active',  -- active: 启用, inactive: 禁用
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- ============================================
-- 3. 用户表
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    phone_number TEXT,
    department_id INTEGER,
    role TEXT NOT NULL,  -- employee: 员工, canteen_staff: 食堂人员, admin: 系统管理员
    is_active INTEGER DEFAULT 1,  -- 1: 启用, 0: 禁用
    wechat_openid TEXT,  -- 企业微信OpenID（预留）
    wechat_userid TEXT,  -- 企业微信UserID（预留）
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- ============================================
-- 4. 食堂人员关联表
-- ============================================
CREATE TABLE IF NOT EXISTS canteen_staff_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    canteen_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (canteen_id) REFERENCES canteens(id),
    UNIQUE(user_id, canteen_id)
);

-- ============================================
-- 5. 菜品分类表
-- ============================================
CREATE TABLE IF NOT EXISTS dish_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);

-- ============================================
-- 6. 菜品表
-- ============================================
CREATE TABLE IF NOT EXISTS dishes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    price REAL DEFAULT 0,
    image_url TEXT,
    description TEXT,
    status TEXT DEFAULT 'active',  -- active: 已上架, inactive: 已下架
    canteen_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES dish_categories(id),
    FOREIGN KEY (canteen_id) REFERENCES canteens(id)
);

-- ============================================
-- 7. 菜单表（每日菜单配置）
-- ============================================
CREATE TABLE IF NOT EXISTS menus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    canteen_id INTEGER NOT NULL,
    menu_date TEXT NOT NULL,  -- YYYY-MM-DD
    meal_type TEXT NOT NULL,  -- breakfast: 早餐, lunch: 午餐, dinner: 晚餐
    status TEXT DEFAULT 'active',  -- active: 启用, inactive: 禁用
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (canteen_id) REFERENCES canteens(id),
    UNIQUE(canteen_id, menu_date, meal_type)
);

-- ============================================
-- 8. 菜单项表（菜单中的菜品及数量）
-- ============================================
CREATE TABLE IF NOT EXISTS menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_id INTEGER NOT NULL,
    dish_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,  -- 总数量
    available_quantity INTEGER NOT NULL,  -- 可用数量
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE,
    FOREIGN KEY (dish_id) REFERENCES dishes(id),
    UNIQUE(menu_id, dish_id)
);

-- ============================================
-- 9. 订单表
-- ============================================
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_no TEXT NOT NULL UNIQUE,
    user_id INTEGER NOT NULL,
    canteen_id INTEGER NOT NULL,
    menu_id INTEGER NOT NULL,
    meal_type TEXT NOT NULL,  -- breakfast: 早餐, lunch: 午餐, dinner: 晚餐
    order_date TEXT NOT NULL,  -- YYYY-MM-DD
    status TEXT DEFAULT 'placed',  -- placed: 已下单, cancelled: 已取消, completed: 已完成
    total_amount REAL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (canteen_id) REFERENCES canteens(id),
    FOREIGN KEY (menu_id) REFERENCES menus(id)
);

-- ============================================
-- 10. 订单项表
-- ============================================
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    dish_id INTEGER NOT NULL,
    dish_name TEXT NOT NULL,
    dish_price REAL NOT NULL,
    quantity INTEGER NOT NULL,
    subtotal REAL NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (dish_id) REFERENCES dishes(id)
);

-- ============================================
-- 11. 菜品评分表
-- ============================================
CREATE TABLE IF NOT EXISTS dish_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    order_id INTEGER NOT NULL,
    dish_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (dish_id) REFERENCES dishes(id),
    UNIQUE(user_id, order_id, dish_id)
);

-- ============================================
-- 12. 意见反馈表
-- ============================================
CREATE TABLE IF NOT EXISTS feedbacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending: 待处理, processed: 已处理
    reply TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ============================================
-- 索引创建
-- ============================================
CREATE INDEX IF NOT EXISTS idx_users_employee_id ON users(employee_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_dishes_canteen_id ON dishes(canteen_id);
CREATE INDEX IF NOT EXISTS idx_dishes_status ON dishes(status);
CREATE INDEX IF NOT EXISTS idx_menus_canteen_date_meal ON menus(canteen_id, menu_date, meal_type);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_canteen_id ON orders(canteen_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_date_meal ON orders(order_date, meal_type);

-- ============================================
-- 初始化数据
-- ============================================

-- 1. 初始化部门数据
INSERT INTO departments (name, parent_id, created_at, updated_at) VALUES
('总裁办', NULL, datetime('now'), datetime('now')),
('技术中心', NULL, datetime('now'), datetime('now')),
('市场部', NULL, datetime('now'), datetime('now')),
('财务部', NULL, datetime('now'), datetime('now')),
('人力资源部', NULL, datetime('now'), datetime('now')),
('研发部', 2, datetime('now'), datetime('now')),
('测试部', 2, datetime('now'), datetime('now')),
('产品部', 2, datetime('now'), datetime('now'));

-- 2. 初始化食堂数据
INSERT INTO canteens (name, address, phone, status, created_at, updated_at) VALUES
('总部食堂', '北京市朝阳区总部大楼1层', '010-12345678', 'active', datetime('now'), datetime('now')),
('研发中心食堂', '北京市海淀区研发中心2层', '010-23456789', 'active', datetime('now'), datetime('now')),
('分公司食堂', '上海市浦东新区分公司3层', '021-34567890', 'active', datetime('now'), datetime('now'));

-- 3. 初始化管理员账号（密码: admin123）
INSERT INTO users (employee_id, password, full_name, phone_number, department_id, role, is_active, created_at, updated_at) VALUES
('ADMIN001', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', '系统管理员', '13800138000', 1, 'admin', 1, datetime('now'), datetime('now'));

-- 4. 初始化食堂人员（密码: staff123）
INSERT INTO users (employee_id, password, full_name, phone_number, department_id, role, is_active, created_at, updated_at) VALUES
('STAFF001', '1d72706551d7aef90268f8e7ea2f992e0ae3f1ca6e3c0ff68e84a8e3c6a6e0d2', '张师傅', '13800138001', 5, 'canteen_staff', 1, datetime('now'), datetime('now')),
('STAFF002', '1d72706551d7aef90268f8e7ea2f992e0ae3f1ca6e3c0ff68e84a8e3c6a6e0d2', '李师傅', '13800138002', 5, 'canteen_staff', 1, datetime('now'), datetime('now'));

-- 5. 关联食堂人员到食堂
INSERT INTO canteen_staff_relations (user_id, canteen_id, created_at) VALUES
(2, 1, datetime('now')),  -- 张师傅 -> 总部食堂
(3, 2, datetime('now'));  -- 李师傅 -> 研发中心食堂

-- 6. 初始化测试员工（密码: user123）
INSERT INTO users (employee_id, password, full_name, phone_number, department_id, role, is_active, created_at, updated_at) VALUES
('EMP001', 'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae', '王小明', '13900139001', 6, 'employee', 1, datetime('now'), datetime('now')),
('EMP002', 'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae', '李小红', '13900139002', 6, 'employee', 1, datetime('now'), datetime('now')),
('EMP003', 'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae', '张小刚', '13900139003', 7, 'employee', 1, datetime('now'), datetime('now')),
('EMP004', 'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae', '刘小丽', '13900139004', 7, 'employee', 1, datetime('now'), datetime('now')),
('EMP005', 'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae', '陈小华', '13900139005', 8, 'employee', 1, datetime('now'), datetime('now')),
('EMP006', 'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae', '赵小强', '13900139006', 8, 'employee', 1, datetime('now'), datetime('now')),
('EMP007', 'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae', '孙小芳', '13900139007', 3, 'employee', 1, datetime('now'), datetime('now')),
('EMP008', 'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae', '周小军', '13900139008', 4, 'employee', 1, datetime('now'), datetime('now')),
('EMP009', 'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae', '吴小梅', '13900139009', 5, 'employee', 1, datetime('now'), datetime('now')),
('EMP010', 'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae', '郑小龙', '13900139010', 2, 'employee', 1, datetime('now'), datetime('now'));

-- 7. 初始化菜品分类
INSERT INTO dish_categories (name, sort_order, created_at) VALUES
('主食', 1, datetime('now')),
('热菜', 2, datetime('now')),
('凉菜', 3, datetime('now')),
('汤类', 4, datetime('now')),
('小吃', 5, datetime('now')),
('水果', 6, datetime('now'));

-- 8. 初始化菜品（总部食堂）
INSERT INTO dishes (name, category_id, price, image_url, description, status, canteen_id, created_at, updated_at) VALUES
('米饭', 1, 0, '/images/rice.jpg', '优质大米', 'active', 1, datetime('now'), datetime('now')),
('馒头', 1, 0, '/images/mantou.jpg', '手工馒头', 'active', 1, datetime('now'), datetime('now')),
('红烧肉', 2, 0, '/images/hongshaorou.jpg', '经典红烧肉', 'active', 1, datetime('now'), datetime('now')),
('宫保鸡丁', 2, 0, '/images/gongbaojiding.jpg', '川味经典', 'active', 1, datetime('now'), datetime('now')),
('清蒸鱼', 2, 0, '/images/qingzhengyu.jpg', '鲜嫩可口', 'active', 1, datetime('now'), datetime('now')),
('麻婆豆腐', 2, 0, '/images/mapodoufu.jpg', '麻辣鲜香', 'active', 1, datetime('now'), datetime('now')),
('青菜炒香菇', 2, 0, '/images/qingcai.jpg', '清淡健康', 'active', 1, datetime('now'), datetime('now')),
('凉拌黄瓜', 3, 0, '/images/huangua.jpg', '清爽开胃', 'active', 1, datetime('now'), datetime('now')),
('拍黄瓜', 3, 0, '/images/paihuangua.jpg', '酸辣可口', 'active', 1, datetime('now'), datetime('now')),
('紫菜蛋花汤', 4, 0, '/images/zicaitang.jpg', '营养美味', 'active', 1, datetime('now'), datetime('now')),
('西红柿鸡蛋汤', 4, 0, '/images/xihongshitang.jpg', '家常美味', 'active', 1, datetime('now'), datetime('now')),
('包子', 5, 0, '/images/baozi.jpg', '鲜肉包子', 'active', 1, datetime('now'), datetime('now')),
('油条', 5, 0, '/images/youtiao.jpg', '香脆油条', 'active', 1, datetime('now'), datetime('now')),
('豆浆', 5, 0, '/images/doujiang.jpg', '营养豆浆', 'active', 1, datetime('now'), datetime('now')),
('苹果', 6, 0, '/images/apple.jpg', '新鲜苹果', 'active', 1, datetime('now'), datetime('now'));

-- 9. 初始化菜品（研发中心食堂）
INSERT INTO dishes (name, category_id, price, image_url, description, status, canteen_id, created_at, updated_at) VALUES
('米饭', 1, 0, '/images/rice.jpg', '优质大米', 'active', 2, datetime('now'), datetime('now')),
('花卷', 1, 0, '/images/huajuan.jpg', '手工花卷', 'active', 2, datetime('now'), datetime('now')),
('糖醋里脊', 2, 0, '/images/tangculiji.jpg', '酸甜可口', 'active', 2, datetime('now'), datetime('now')),
('鱼香肉丝', 2, 0, '/images/yuxiangrousi.jpg', '经典川菜', 'active', 2, datetime('now'), datetime('now')),
('西兰花炒虾仁', 2, 0, '/images/xilanhua.jpg', '营养丰富', 'active', 2, datetime('now'), datetime('now'));

-- 10. 初始化当天和未来3天的菜单（总部食堂）
-- 今天午餐
INSERT INTO menus (canteen_id, menu_date, meal_type, status, created_at, updated_at) VALUES
(1, date('now'), 'lunch', 'active', datetime('now'), datetime('now'));

-- 今天午餐菜单项
INSERT INTO menu_items (menu_id, dish_id, quantity, available_quantity, created_at, updated_at) VALUES
(1, 1, 100, 100, datetime('now'), datetime('now')),  -- 米饭
(1, 3, 30, 30, datetime('now'), datetime('now')),   -- 红烧肉
(1, 4, 30, 30, datetime('now'), datetime('now')),   -- 宫保鸡丁
(1, 7, 40, 40, datetime('now'), datetime('now')),   -- 青菜炒香菇
(1, 8, 50, 50, datetime('now'), datetime('now')),   -- 凉拌黄瓜
(1, 10, 50, 50, datetime('now'), datetime('now'));  -- 紫菜蛋花汤

-- 今天晚餐
INSERT INTO menus (canteen_id, menu_date, meal_type, status, created_at, updated_at) VALUES
(1, date('now'), 'dinner', 'active', datetime('now'), datetime('now'));

INSERT INTO menu_items (menu_id, dish_id, quantity, available_quantity, created_at, updated_at) VALUES
(2, 1, 100, 100, datetime('now'), datetime('now')),
(2, 5, 30, 30, datetime('now'), datetime('now')),   -- 清蒸鱼
(2, 6, 30, 30, datetime('now'), datetime('now')),   -- 麻婆豆腐
(2, 7, 40, 40, datetime('now'), datetime('now')),
(2, 9, 50, 50, datetime('now'), datetime('now')),   -- 拍黄瓜
(2, 11, 50, 50, datetime('now'), datetime('now'));  -- 西红柿鸡蛋汤

-- 明天早餐
INSERT INTO menus (canteen_id, menu_date, meal_type, status, created_at, updated_at) VALUES
(1, date('now', '+1 day'), 'breakfast', 'active', datetime('now'), datetime('now'));

INSERT INTO menu_items (menu_id, dish_id, quantity, available_quantity, created_at, updated_at) VALUES
(3, 2, 100, 100, datetime('now'), datetime('now')),  -- 馒头
(3, 12, 50, 50, datetime('now'), datetime('now')),   -- 包子
(3, 13, 50, 50, datetime('now'), datetime('now')),   -- 油条
(3, 14, 80, 80, datetime('now'), datetime('now'));   -- 豆浆

-- 明天午餐
INSERT INTO menus (canteen_id, menu_date, meal_type, status, created_at, updated_at) VALUES
(1, date('now', '+1 day'), 'lunch', 'active', datetime('now'), datetime('now'));

INSERT INTO menu_items (menu_id, dish_id, quantity, available_quantity, created_at, updated_at) VALUES
(4, 1, 100, 100, datetime('now'), datetime('now')),
(4, 3, 30, 30, datetime('now'), datetime('now')),
(4, 4, 30, 30, datetime('now'), datetime('now')),
(4, 5, 30, 30, datetime('now'), datetime('now')),
(4, 8, 50, 50, datetime('now'), datetime('now')),
(4, 10, 50, 50, datetime('now'), datetime('now'));

-- 明天晚餐
INSERT INTO menus (canteen_id, menu_date, meal_type, status, created_at, updated_at) VALUES
(1, date('now', '+1 day'), 'dinner', 'active', datetime('now'), datetime('now'));

INSERT INTO menu_items (menu_id, dish_id, quantity, available_quantity, created_at, updated_at) VALUES
(5, 1, 100, 100, datetime('now'), datetime('now')),
(5, 6, 30, 30, datetime('now'), datetime('now')),
(5, 7, 40, 40, datetime('now'), datetime('now')),
(5, 9, 50, 50, datetime('now'), datetime('now')),
(5, 11, 50, 50, datetime('now'), datetime('now'));

-- 后天午餐
INSERT INTO menus (canteen_id, menu_date, meal_type, status, created_at, updated_at) VALUES
(1, date('now', '+2 days'), 'lunch', 'active', datetime('now'), datetime('now'));

INSERT INTO menu_items (menu_id, dish_id, quantity, available_quantity, created_at, updated_at) VALUES
(6, 1, 100, 100, datetime('now'), datetime('now')),
(6, 4, 30, 30, datetime('now'), datetime('now')),
(6, 5, 30, 30, datetime('now'), datetime('now')),
(6, 7, 40, 40, datetime('now'), datetime('now')),
(6, 8, 50, 50, datetime('now'), datetime('now')),
(6, 10, 50, 50, datetime('now'), datetime('now'));

-- 完成
SELECT '数据库初始化完成！' AS message;
SELECT '测试账号信息：' AS message;
SELECT '管理员 - 工号: ADMIN001, 密码: admin123' AS message;
SELECT '食堂人员 - 工号: STAFF001, 密码: staff123' AS message;
SELECT '员工 - 工号: EMP001-EMP010, 密码: user123' AS message;
