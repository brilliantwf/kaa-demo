# 订单服务

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.helpers import (get_db_connection, get_current_datetime, generate_order_no,
                           check_time_limit, dict_from_row, list_from_rows)
import config


class OrderService:
    """订单服务类"""
    
    def create_order(self, user_id, canteen_id, menu_id, meal_type, order_date, items):
        """
        创建订单
        
        Args:
            user_id (int): 用户ID
            canteen_id (int): 食堂ID
            menu_id (int): 菜单ID
            meal_type (str): 餐次类型
            order_date (str): 订餐日期 (YYYY-MM-DD)
            items (list): 订单项列表 [{'dish_id': 1, 'quantity': 2}, ...]
        
        Returns:
            int: 新创建的订单ID
        
        Raises:
            ValueError: 各种业务逻辑错误
        """
        # 检查时间限制
        if not check_time_limit(meal_type, order_date):
            raise ValueError('已超过点餐时间')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 检查是否已有订单
            cursor.execute('''
                SELECT id FROM orders
                WHERE user_id = ? AND order_date = ? AND meal_type = ? 
                  AND status IN ('placed', 'completed')
            ''', (user_id, order_date, meal_type))
            
            existing = cursor.fetchone()
            if existing:
                conn.close()
                raise ValueError('该餐次已有订单，不能重复下单')
            
            # 检查菜单项库存
            for item in items:
                cursor.execute('''
                    SELECT mi.available_quantity, d.name, d.price
                    FROM menu_items mi
                    LEFT JOIN dishes d ON mi.dish_id = d.id
                    WHERE mi.menu_id = ? AND mi.dish_id = ?
                ''', (menu_id, item['dish_id']))
                
                menu_item = cursor.fetchone()
                if not menu_item:
                    conn.close()
                    raise ValueError(f'菜品ID {item["dish_id"]} 不在菜单中')
                
                if menu_item['available_quantity'] < item['quantity']:
                    conn.close()
                    raise ValueError(f'菜品 {menu_item["name"]} 库存不足')
            
            # 创建订单
            order_no = generate_order_no()
            now = get_current_datetime()
            total_amount = 0
            
            cursor.execute('''
                INSERT INTO orders (order_no, user_id, canteen_id, menu_id, meal_type, 
                                   order_date, status, total_amount, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, 'placed', 0, ?, ?)
            ''', (order_no, user_id, canteen_id, menu_id, meal_type, order_date, now, now))
            
            order_id = cursor.lastrowid
            
            # 创建订单项并扣减库存
            for item in items:
                # 获取菜品信息
                cursor.execute('''
                    SELECT d.name, d.price, mi.id as menu_item_id
                    FROM dishes d
                    LEFT JOIN menu_items mi ON d.id = mi.dish_id
                    WHERE d.id = ? AND mi.menu_id = ?
                ''', (item['dish_id'], menu_id))
                
                dish = cursor.fetchone()
                subtotal = dish['price'] * item['quantity']
                total_amount += subtotal
                
                # 插入订单项
                cursor.execute('''
                    INSERT INTO order_items (order_id, dish_id, dish_name, dish_price, quantity, subtotal, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (order_id, item['dish_id'], dish['name'], dish['price'], 
                     item['quantity'], subtotal, now))
                
                # 扣减库存
                cursor.execute('''
                    UPDATE menu_items
                    SET available_quantity = available_quantity - ?, updated_at = ?
                    WHERE id = ?
                ''', (item['quantity'], now, dish['menu_item_id']))
            
            # 更新订单总金额
            cursor.execute('''
                UPDATE orders SET total_amount = ? WHERE id = ?
            ''', (total_amount, order_id))
            
            conn.commit()
            conn.close()
            
            return order_id
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
    
    def get_order_by_id(self, order_id):
        """
        获取订单详情
        
        Args:
            order_id (int): 订单ID
        
        Returns:
            dict: 订单信息（包含items）
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取订单基本信息
        cursor.execute('''
            SELECT o.*, u.full_name as user_name, u.employee_id, c.name as canteen_name
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.id
            LEFT JOIN canteens c ON o.canteen_id = c.id
            WHERE o.id = ?
        ''', (order_id,))
        
        order = cursor.fetchone()
        
        if not order:
            conn.close()
            return None
        
        order_dict = dict_from_row(order)
        
        # 获取订单项
        cursor.execute('''
            SELECT * FROM order_items WHERE order_id = ? ORDER BY id
        ''', (order_id,))
        
        items = cursor.fetchall()
        conn.close()
        
        order_dict['items'] = list_from_rows(items)
        
        return order_dict
    
    def get_user_orders(self, user_id, status=None):
        """
        获取用户订单列表
        
        Args:
            user_id (int): 用户ID
            status (str): 状态过滤
        
        Returns:
            list: 订单列表
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT o.*, c.name as canteen_name
            FROM orders o
            LEFT JOIN canteens c ON o.canteen_id = c.id
            WHERE o.user_id = ?
        '''
        params = [user_id]
        
        if status:
            query += ' AND o.status = ?'
            params.append(status)
        
        query += ' ORDER BY o.order_date DESC, o.meal_type DESC, o.created_at DESC'
        
        cursor.execute(query, params)
        orders = cursor.fetchall()
        conn.close()
        
        return list_from_rows(orders)
    
    def get_canteen_orders(self, canteen_id, order_date=None, meal_type=None, status=None):
        """
        获取食堂订单列表
        
        Args:
            canteen_id (int): 食堂ID
            order_date (str): 日期过滤
            meal_type (str): 餐次过滤
            status (str): 状态过滤
        
        Returns:
            list: 订单列表
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT o.*, u.full_name as user_name, u.employee_id
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.id
            WHERE o.canteen_id = ?
        '''
        params = [canteen_id]
        
        if order_date:
            query += ' AND o.order_date = ?'
            params.append(order_date)
        
        if meal_type:
            query += ' AND o.meal_type = ?'
            params.append(meal_type)
        
        if status:
            query += ' AND o.status = ?'
            params.append(status)
        
        query += ' ORDER BY o.order_date DESC, o.meal_type, o.created_at'
        
        cursor.execute(query, params)
        orders = cursor.fetchall()
        conn.close()
        
        return list_from_rows(orders)
    
    def update_order(self, order_id, user_id, items):
        """
        修改订单
        
        Args:
            order_id (int): 订单ID
            user_id (int): 用户ID
            items (list): 新的订单项列表
        
        Raises:
            ValueError: 各种业务逻辑错误
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 获取订单信息
            cursor.execute('''
                SELECT * FROM orders WHERE id = ? AND user_id = ?
            ''', (order_id, user_id))
            
            order = cursor.fetchone()
            if not order:
                conn.close()
                raise ValueError('订单不存在')
            
            if order['status'] != config.ORDER_STATUS_PLACED:
                conn.close()
                raise ValueError('只能修改已下单状态的订单')
            
            # 检查时间限制
            if not check_time_limit(order['meal_type'], order['order_date']):
                conn.close()
                raise ValueError('已超过修改时间')
            
            now = get_current_datetime()
            
            # 获取原订单项并退回库存
            cursor.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,))
            old_items = cursor.fetchall()
            
            for old_item in old_items:
                cursor.execute('''
                    UPDATE menu_items mi
                    SET available_quantity = available_quantity + ?, updated_at = ?
                    WHERE mi.menu_id = ? AND mi.dish_id = ?
                ''', (old_item['quantity'], now, order['menu_id'], old_item['dish_id']))
            
            # 删除原订单项
            cursor.execute('DELETE FROM order_items WHERE order_id = ?', (order_id,))
            
            # 检查新订单项库存
            for item in items:
                cursor.execute('''
                    SELECT mi.available_quantity, d.name
                    FROM menu_items mi
                    LEFT JOIN dishes d ON mi.dish_id = d.id
                    WHERE mi.menu_id = ? AND mi.dish_id = ?
                ''', (order['menu_id'], item['dish_id']))
                
                menu_item = cursor.fetchone()
                if not menu_item:
                    conn.close()
                    raise ValueError(f'菜品ID {item["dish_id"]} 不在菜单中')
                
                if menu_item['available_quantity'] < item['quantity']:
                    conn.close()
                    raise ValueError(f'菜品 {menu_item["name"]} 库存不足')
            
            # 创建新订单项并扣减库存
            total_amount = 0
            for item in items:
                cursor.execute('''
                    SELECT d.name, d.price, mi.id as menu_item_id
                    FROM dishes d
                    LEFT JOIN menu_items mi ON d.id = mi.dish_id
                    WHERE d.id = ? AND mi.menu_id = ?
                ''', (item['dish_id'], order['menu_id']))
                
                dish = cursor.fetchone()
                subtotal = dish['price'] * item['quantity']
                total_amount += subtotal
                
                cursor.execute('''
                    INSERT INTO order_items (order_id, dish_id, dish_name, dish_price, quantity, subtotal, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (order_id, item['dish_id'], dish['name'], dish['price'], 
                     item['quantity'], subtotal, now))
                
                cursor.execute('''
                    UPDATE menu_items
                    SET available_quantity = available_quantity - ?, updated_at = ?
                    WHERE id = ?
                ''', (item['quantity'], now, dish['menu_item_id']))
            
            # 更新订单
            cursor.execute('''
                UPDATE orders
                SET total_amount = ?, updated_at = ?
                WHERE id = ?
            ''', (total_amount, now, order_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
    
    def cancel_order(self, order_id, user_id):
        """
        取消订单
        
        Args:
            order_id (int): 订单ID
            user_id (int): 用户ID
        
        Raises:
            ValueError: 各种业务逻辑错误
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 获取订单信息
            cursor.execute('''
                SELECT * FROM orders WHERE id = ? AND user_id = ?
            ''', (order_id, user_id))
            
            order = cursor.fetchone()
            if not order:
                conn.close()
                raise ValueError('订单不存在')
            
            if order['status'] != config.ORDER_STATUS_PLACED:
                conn.close()
                raise ValueError('只能取消已下单状态的订单')
            
            # 检查时间限制
            if not check_time_limit(order['meal_type'], order['order_date']):
                conn.close()
                raise ValueError('已超过取消时间')
            
            now = get_current_datetime()
            
            # 获取订单项并退回库存
            cursor.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,))
            items = cursor.fetchall()
            
            for item in items:
                cursor.execute('''
                    UPDATE menu_items mi
                    SET available_quantity = available_quantity + ?, updated_at = ?
                    WHERE mi.menu_id = ? AND mi.dish_id = ?
                ''', (item['quantity'], now, order['menu_id'], item['dish_id']))
            
            # 更新订单状态
            cursor.execute('''
                UPDATE orders
                SET status = 'cancelled', updated_at = ?
                WHERE id = ?
            ''', (now, order_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
    
    def get_meal_statistics(self, canteen_id, order_date, meal_type):
        """
        获取餐次统计
        
        Args:
            canteen_id (int): 食堂ID
            order_date (str): 日期
            meal_type (str): 餐次类型
        
        Returns:
            dict: 统计信息
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 按菜品统计
        cursor.execute('''
            SELECT oi.dish_name, SUM(oi.quantity) as total_quantity, COUNT(DISTINCT o.id) as order_count
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE o.canteen_id = ? AND o.order_date = ? AND o.meal_type = ? 
              AND o.status IN ('placed', 'completed')
            GROUP BY oi.dish_id, oi.dish_name
            ORDER BY total_quantity DESC
        ''', (canteen_id, order_date, meal_type))
        
        dish_stats = cursor.fetchall()
        
        # 按员工统计
        cursor.execute('''
            SELECT u.employee_id, u.full_name, o.order_no, o.created_at
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.id
            WHERE o.canteen_id = ? AND o.order_date = ? AND o.meal_type = ? 
              AND o.status IN ('placed', 'completed')
            ORDER BY o.created_at
        ''', (canteen_id, order_date, meal_type))
        
        user_stats = cursor.fetchall()
        
        # 总订单数
        cursor.execute('''
            SELECT COUNT(*) as total_orders
            FROM orders
            WHERE canteen_id = ? AND order_date = ? AND meal_type = ? 
              AND status IN ('placed', 'completed')
        ''', (canteen_id, order_date, meal_type))
        
        total = cursor.fetchone()
        conn.close()
        
        return {
            'dish_statistics': list_from_rows(dish_stats),
            'user_statistics': list_from_rows(user_stats),
            'total_orders': total['total_orders']
        }
