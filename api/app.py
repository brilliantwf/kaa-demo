# Flask API服务主程序

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# 导入配置和工具
import config
from utils.helpers import (success_response, error_response, require_auth, 
                           require_role, get_current_date)

# 导入服务
from services.auth_service import AuthService
from services.canteen_service import CanteenService
from services.dish_service import DishService
from services.menu_service import MenuService
from services.order_service import OrderService

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# ============================================
# 认证相关API
# ============================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.json
        employee_id = data.get('employee_id')
        password = data.get('password')
        
        if not employee_id or not password:
            return jsonify(error_response(config.ERROR_INVALID_PARAM, '员工工号和密码不能为空'))
        
        auth_service = AuthService()
        user = auth_service.login(employee_id, password)
        
        return jsonify(success_response(user, '登录成功'))
    
    except ValueError as e:
        return jsonify(error_response(config.ERROR_INVALID_PASSWORD, str(e)))
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


@app.route('/api/auth/user-info', methods=['GET'])
@require_auth
def get_user_info(current_user_id):
    """获取当前用户信息"""
    try:
        auth_service = AuthService()
        user = auth_service.get_user_info(current_user_id)
        
        if not user:
            return jsonify(error_response(config.ERROR_USER_NOT_FOUND, '用户不存在'))
        
        return jsonify(success_response(user))
    
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


# ============================================
# 食堂相关API
# ============================================

@app.route('/api/canteens', methods=['GET'])
def get_canteens():
    """获取食堂列表"""
    try:
        status = request.args.get('status')
        canteen_service = CanteenService()
        canteens = canteen_service.get_canteen_list(status)
        
        return jsonify(success_response(canteens))
    
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


@app.route('/api/canteens/<int:canteen_id>', methods=['GET'])
def get_canteen(canteen_id):
    """获取食堂详情"""
    try:
        canteen_service = CanteenService()
        canteen = canteen_service.get_canteen_by_id(canteen_id)
        
        if not canteen:
            return jsonify(error_response(config.ERROR_INVALID_PARAM, '食堂不存在'))
        
        return jsonify(success_response(canteen))
    
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


@app.route('/api/canteens', methods=['POST'])
@require_role(config.ROLE_ADMIN)
def create_canteen(current_user_id, current_user_role):
    """创建食堂"""
    try:
        data = request.json
        name = data.get('name')
        address = data.get('address', '')
        phone = data.get('phone', '')
        
        if not name:
            return jsonify(error_response(config.ERROR_INVALID_PARAM, '食堂名称不能为空'))
        
        canteen_service = CanteenService()
        canteen_id = canteen_service.create_canteen(name, address, phone)
        
        return jsonify(success_response({'canteen_id': canteen_id}, '创建成功'))
    
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


@app.route('/api/canteens/<int:canteen_id>', methods=['PUT'])
@require_role(config.ROLE_ADMIN)
def update_canteen(canteen_id, current_user_id, current_user_role):
    """更新食堂信息"""
    try:
        data = request.json
        name = data.get('name')
        address = data.get('address', '')
        phone = data.get('phone', '')
        
        if not name:
            return jsonify(error_response(config.ERROR_INVALID_PARAM, '食堂名称不能为空'))
        
        canteen_service = CanteenService()
        canteen_service.update_canteen(canteen_id, name, address, phone)
        
        return jsonify(success_response(None, '更新成功'))
    
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


@app.route('/api/canteens/<int:canteen_id>', methods=['DELETE'])
@require_role(config.ROLE_ADMIN)
def delete_canteen(canteen_id, current_user_id, current_user_role):
    """删除食堂"""
    try:
        canteen_service = CanteenService()
        canteen_service.delete_canteen(canteen_id)
        
        return jsonify(success_response(None, '删除成功'))
    
    except ValueError as e:
        return jsonify(error_response(config.ERROR_INVALID_PARAM, str(e)))
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


# ============================================
# 菜品相关API
# ============================================

@app.route('/api/dishes', methods=['GET'])
def get_dishes():
    """获取菜品列表"""
    try:
        canteen_id = request.args.get('canteen_id', type=int)
        category_id = request.args.get('category_id', type=int)
        status = request.args.get('status')
        
        dish_service = DishService()
        dishes = dish_service.get_dish_list(canteen_id, category_id, status)
        
        return jsonify(success_response(dishes))
    
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


@app.route('/api/dishes/<int:dish_id>', methods=['GET'])
def get_dish(dish_id):
    """获取菜品详情"""
    try:
        dish_service = DishService()
        dish = dish_service.get_dish_by_id(dish_id)
        
        if not dish:
            return jsonify(error_response(config.ERROR_INVALID_PARAM, '菜品不存在'))
        
        return jsonify(success_response(dish))
    
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


@app.route('/api/dishes', methods=['POST'])
@require_role(config.ROLE_ADMIN, config.ROLE_CANTEEN_STAFF)
def create_dish(current_user_id, current_user_role):
    """创建菜品"""
    try:
        data = request.json
        name = data.get('name')
        category_id = data.get('category_id')
        canteen_id = data.get('canteen_id')
        price = data.get('price', 0)
        image_url = data.get('image_url', '')
        description = data.get('description', '')
        
        if not name or not category_id or not canteen_id:
            return jsonify(error_response(config.ERROR_INVALID_PARAM, '菜品名称、分类和食堂不能为空'))
        
        dish_service = DishService()
        dish_id = dish_service.create_dish(name, category_id, canteen_id, price, image_url, description)
        
        return jsonify(success_response({'dish_id': dish_id}, '创建成功'))
    
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


@app.route('/api/dishes/<int:dish_id>', methods=['PUT'])
@require_role(config.ROLE_ADMIN, config.ROLE_CANTEEN_STAFF)
def update_dish(dish_id, current_user_id, current_user_role):
    """更新菜品信息"""
    try:
        data = request.json
        name = data.get('name')
        category_id = data.get('category_id')
        price = data.get('price', 0)
        image_url = data.get('image_url', '')
        description = data.get('description', '')
        
        if not name or not category_id:
            return jsonify(error_response(config.ERROR_INVALID_PARAM, '菜品名称和分类不能为空'))
        
        dish_service = DishService()
        dish_service.update_dish(dish_id, name, category_id, price, image_url, description)
        
        return jsonify(success_response(None, '更新成功'))
    
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


@app.route('/api/dishes/<int:dish_id>/status', methods=['PUT'])
@require_role(config.ROLE_ADMIN, config.ROLE_CANTEEN_STAFF)
def update_dish_status(dish_id, current_user_id, current_user_role):
    """更新菜品状态（上架/下架）"""
    try:
        data = request.json
        status = data.get('status')
        
        if status not in ['active', 'inactive']:
            return jsonify(error_response(config.ERROR_INVALID_PARAM, '状态值无效'))
        
        dish_service = DishService()
        dish_service.update_dish_status(dish_id, status)
        
        return jsonify(success_response(None, '更新成功'))
    
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


@app.route('/api/dish-categories', methods=['GET'])
def get_dish_categories():
    """获取菜品分类列表"""
    try:
        dish_service = DishService()
        categories = dish_service.get_categories()
        
        return jsonify(success_response(categories))
    
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


# ============================================
# 菜单相关API
# ============================================

@app.route('/api/menus', methods=['GET'])
def get_menus():
    """获取菜单列表"""
    try:
        canteen_id = request.args.get('canteen_id', type=int)
        menu_date = request.args.get('menu_date')
        meal_type = request.args.get('meal_type')
        
        menu_service = MenuService()
        menus = menu_service.get_menu_list(canteen_id, menu_date, meal_type)
        
        return jsonify(success_response(menus))
    
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


@app.route('/api/menus/<int:menu_id>', methods=['GET'])
def get_menu(menu_id):
    """获取菜单详情（包含菜单项）"""
    try:
        menu_service = MenuService()
        menu = menu_service.get_menu_by_id(menu_id)
        
        if not menu:
            return jsonify(error_response(config.ERROR_INVALID_PARAM, '菜单不存在'))
        
        return jsonify(success_response(menu))
    
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


@app.route('/api/menus', methods=['POST'])
@require_role(config.ROLE_ADMIN, config.ROLE_CANTEEN_STAFF)
def create_menu(current_user_id, current_user_role):
    """创建菜单"""
    try:
        data = request.json
        canteen_id = data.get('canteen_id')
        menu_date = data.get('menu_date')
        meal_type = data.get('meal_type')
        
        if not canteen_id or not menu_date or not meal_type:
            return jsonify(error_response(config.ERROR_INVALID_PARAM, '食堂、日期和餐次不能为空'))
        
        menu_service = MenuService()
        menu_id = menu_service.create_menu(canteen_id, menu_date, meal_type)
        
        return jsonify(success_response({'menu_id': menu_id}, '创建成功'))
    
    except ValueError as e:
        return jsonify(error_response(config.ERROR_INVALID_PARAM, str(e)))
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


@app.route('/api/menus/<int:menu_id>/items', methods=['POST'])
@require_role(config.ROLE_ADMIN, config.ROLE_CANTEEN_STAFF)
def add_menu_item(menu_id, current_user_id, current_user_role):
    """添加菜单项"""
    try:
        data = request.json
        dish_id = data.get('dish_id')
        quantity = data.get('quantity')
        
        if not dish_id or not quantity or quantity <= 0:
            return jsonify(error_response(config.ERROR_INVALID_PARAM, '菜品ID和数量必须有效'))
        
        menu_service = MenuService()
        item_id = menu_service.add_menu_item(menu_id, dish_id, quantity)
        
        return jsonify(success_response({'item_id': item_id}, '添加成功'))
    
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


# ============================================
# 订单相关API
# ============================================

@app.route('/api/orders', methods=['POST'])
@require_role(config.ROLE_EMPLOYEE)
def create_order(current_user_id, current_user_role):
    """创建订单"""
    try:
        data = request.json
        canteen_id = data.get('canteen_id')
        menu_id = data.get('menu_id')
        meal_type = data.get('meal_type')
        order_date = data.get('order_date')
        items = data.get('items', [])
        
        if not canteen_id or not menu_id or not meal_type or not order_date or not items:
            return jsonify(error_response(config.ERROR_INVALID_PARAM, '订单信息不完整'))
        
        order_service = OrderService()
        order_id = order_service.create_order(
            current_user_id, canteen_id, menu_id, meal_type, order_date, items
        )
        
        return jsonify(success_response({'order_id': order_id}, '下单成功'))
    
    except ValueError as e:
        if '已超过点餐时间' in str(e):
            return jsonify(error_response(config.ERROR_TIME_LIMIT, str(e)))
        elif '已有订单' in str(e):
            return jsonify(error_response(config.ERROR_DUPLICATE_ORDER, str(e)))
        elif '库存不足' in str(e):
            return jsonify(error_response(config.ERROR_INSUFFICIENT_STOCK, str(e)))
        else:
            return jsonify(error_response(config.ERROR_INVALID_PARAM, str(e)))
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


@app.route('/api/orders/<int:order_id>', methods=['GET'])
@require_auth
def get_order(order_id, current_user_id):
    """获取订单详情"""
    try:
        order_service = OrderService()
        order = order_service.get_order_by_id(order_id)
        
        if not order:
            return jsonify(error_response(config.ERROR_ORDER_NOT_FOUND, '订单不存在'))
        
        return jsonify(success_response(order))
    
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


@app.route('/api/orders/my', methods=['GET'])
@require_role(config.ROLE_EMPLOYEE)
def get_my_orders(current_user_id, current_user_role):
    """获取我的订单列表"""
    try:
        status = request.args.get('status')
        
        order_service = OrderService()
        orders = order_service.get_user_orders(current_user_id, status)
        
        return jsonify(success_response(orders))
    
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


@app.route('/api/orders/<int:order_id>', methods=['PUT'])
@require_role(config.ROLE_EMPLOYEE)
def update_order(order_id, current_user_id, current_user_role):
    """修改订单"""
    try:
        data = request.json
        items = data.get('items', [])
        
        if not items:
            return jsonify(error_response(config.ERROR_INVALID_PARAM, '订单项不能为空'))
        
        order_service = OrderService()
        order_service.update_order(order_id, current_user_id, items)
        
        return jsonify(success_response(None, '修改成功'))
    
    except ValueError as e:
        if '已超过修改时间' in str(e):
            return jsonify(error_response(config.ERROR_TIME_LIMIT, str(e)))
        elif '库存不足' in str(e):
            return jsonify(error_response(config.ERROR_INSUFFICIENT_STOCK, str(e)))
        else:
            return jsonify(error_response(config.ERROR_INVALID_PARAM, str(e)))
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


@app.route('/api/orders/<int:order_id>/cancel', methods=['POST'])
@require_role(config.ROLE_EMPLOYEE)
def cancel_order(order_id, current_user_id, current_user_role):
    """取消订单"""
    try:
        order_service = OrderService()
        order_service.cancel_order(order_id, current_user_id)
        
        return jsonify(success_response(None, '取消成功'))
    
    except ValueError as e:
        if '已超过取消时间' in str(e):
            return jsonify(error_response(config.ERROR_TIME_LIMIT, str(e)))
        else:
            return jsonify(error_response(config.ERROR_INVALID_PARAM, str(e)))
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


@app.route('/api/orders/canteen/<int:canteen_id>', methods=['GET'])
@require_role(config.ROLE_ADMIN, config.ROLE_CANTEEN_STAFF)
def get_canteen_orders(canteen_id, current_user_id, current_user_role):
    """获取食堂订单列表"""
    try:
        order_date = request.args.get('order_date')
        meal_type = request.args.get('meal_type')
        status = request.args.get('status')
        
        order_service = OrderService()
        orders = order_service.get_canteen_orders(canteen_id, order_date, meal_type, status)
        
        return jsonify(success_response(orders))
    
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


@app.route('/api/statistics/meal', methods=['GET'])
@require_role(config.ROLE_ADMIN, config.ROLE_CANTEEN_STAFF)
def get_meal_statistics(current_user_id, current_user_role):
    """获取餐次统计"""
    try:
        canteen_id = request.args.get('canteen_id', type=int)
        order_date = request.args.get('order_date', get_current_date())
        meal_type = request.args.get('meal_type')
        
        if not canteen_id or not meal_type:
            return jsonify(error_response(config.ERROR_INVALID_PARAM, '食堂ID和餐次类型不能为空'))
        
        order_service = OrderService()
        stats = order_service.get_meal_statistics(canteen_id, order_date, meal_type)
        
        return jsonify(success_response(stats))
    
    except Exception as e:
        return jsonify(error_response(config.ERROR_SYSTEM, f'系统错误: {str(e)}'))


# ============================================
# 健康检查
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify(success_response({'status': 'ok'}))


# ============================================
# 启动服务
# ============================================

if __name__ == '__main__':
    print('=' * 60)
    print('集团员工内部用餐点餐平台 API 服务')
    print('=' * 60)
    print(f'服务地址: http://{config.API_HOST}:{config.API_PORT}')
    print(f'数据库路径: {config.DB_PATH}')
    print('=' * 60)
    
    app.run(
        host=config.API_HOST,
        port=config.API_PORT,
        debug=config.DEBUG
    )
