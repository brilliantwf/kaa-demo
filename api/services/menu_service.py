# 菜单服务

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.helpers import get_db_connection, get_current_datetime, dict_from_row, list_from_rows
import config


class MenuService:
    """菜单服务类"""
    
    def get_menu_list(self, canteen_id=None, menu_date=None, meal_type=None):
        """
        获取菜单列表
        
        Args:
            canteen_id (int): 食堂ID
            menu_date (str): 日期 (YYYY-MM-DD)
            meal_type (str): 餐次类型
        
        Returns:
            list: 菜单列表
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT m.*, c.name as canteen_name
            FROM menus m
            LEFT JOIN canteens c ON m.canteen_id = c.id
            WHERE 1=1
        '''
        params = []
        
        if canteen_id:
            query += ' AND m.canteen_id = ?'
            params.append(canteen_id)
        
        if menu_date:
            query += ' AND m.menu_date = ?'
            params.append(menu_date)
        
        if meal_type:
            query += ' AND m.meal_type = ?'
            params.append(meal_type)
        
        query += ' ORDER BY m.menu_date, m.meal_type'
        
        cursor.execute(query, params)
        menus = cursor.fetchall()
        conn.close()
        
        return list_from_rows(menus)
    
    def get_menu_by_id(self, menu_id):
        """
        获取菜单详情（包含菜单项）
        
        Args:
            menu_id (int): 菜单ID
        
        Returns:
            dict: 菜单信息（包含items）
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取菜单基本信息
        cursor.execute('''
            SELECT m.*, c.name as canteen_name
            FROM menus m
            LEFT JOIN canteens c ON m.canteen_id = c.id
            WHERE m.id = ?
        ''', (menu_id,))
        
        menu = cursor.fetchone()
        
        if not menu:
            conn.close()
            return None
        
        menu_dict = dict_from_row(menu)
        
        # 获取菜单项
        cursor.execute('''
            SELECT mi.*, d.name as dish_name, d.price, d.image_url, 
                   d.description, dc.name as category_name
            FROM menu_items mi
            LEFT JOIN dishes d ON mi.dish_id = d.id
            LEFT JOIN dish_categories dc ON d.category_id = dc.id
            WHERE mi.menu_id = ?
            ORDER BY dc.sort_order, d.id
        ''', (menu_id,))
        
        items = cursor.fetchall()
        conn.close()
        
        menu_dict['items'] = list_from_rows(items)
        
        return menu_dict
    
    def create_menu(self, canteen_id, menu_date, meal_type):
        """
        创建菜单
        
        Args:
            canteen_id (int): 食堂ID
            menu_date (str): 日期 (YYYY-MM-DD)
            meal_type (str): 餐次类型
        
        Returns:
            int: 新创建的菜单ID
        
        Raises:
            ValueError: 当菜单已存在时
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查是否已存在
        cursor.execute('''
            SELECT id FROM menus
            WHERE canteen_id = ? AND menu_date = ? AND meal_type = ?
        ''', (canteen_id, menu_date, meal_type))
        
        existing = cursor.fetchone()
        if existing:
            conn.close()
            raise ValueError('该食堂在该日期该餐次的菜单已存在')
        
        now = get_current_datetime()
        
        try:
            cursor.execute('''
                INSERT INTO menus (canteen_id, menu_date, meal_type, status, created_at, updated_at)
                VALUES (?, ?, ?, 'active', ?, ?)
            ''', (canteen_id, menu_date, meal_type, now, now))
            
            menu_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return menu_id
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
    
    def add_menu_item(self, menu_id, dish_id, quantity):
        """
        添加菜单项
        
        Args:
            menu_id (int): 菜单ID
            dish_id (int): 菜品ID
            quantity (int): 数量
        
        Returns:
            int: 新创建的菜单项ID
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = get_current_datetime()
        
        try:
            # 检查菜单项是否已存在
            cursor.execute('''
                SELECT id FROM menu_items
                WHERE menu_id = ? AND dish_id = ?
            ''', (menu_id, dish_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # 更新数量
                cursor.execute('''
                    UPDATE menu_items
                    SET quantity = quantity + ?, available_quantity = available_quantity + ?, updated_at = ?
                    WHERE id = ?
                ''', (quantity, quantity, now, existing['id']))
                
                item_id = existing['id']
            else:
                # 新增
                cursor.execute('''
                    INSERT INTO menu_items (menu_id, dish_id, quantity, available_quantity, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (menu_id, dish_id, quantity, quantity, now, now))
                
                item_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            return item_id
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
    
    def update_menu_item_quantity(self, menu_item_id, quantity):
        """
        更新菜单项数量
        
        Args:
            menu_item_id (int): 菜单项ID
            quantity (int): 新数量
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = get_current_datetime()
        
        try:
            # 获取当前数量和可用数量
            cursor.execute('''
                SELECT quantity, available_quantity
                FROM menu_items
                WHERE id = ?
            ''', (menu_item_id,))
            
            item = cursor.fetchone()
            if not item:
                conn.close()
                raise ValueError('菜单项不存在')
            
            # 计算已使用数量
            used = item['quantity'] - item['available_quantity']
            new_available = quantity - used
            
            if new_available < 0:
                conn.close()
                raise ValueError('新数量不能小于已使用数量')
            
            cursor.execute('''
                UPDATE menu_items
                SET quantity = ?, available_quantity = ?, updated_at = ?
                WHERE id = ?
            ''', (quantity, new_available, now, menu_item_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
    
    def delete_menu_item(self, menu_item_id):
        """
        删除菜单项
        
        Args:
            menu_item_id (int): 菜单项ID
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM menu_items WHERE id = ?', (menu_item_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
    
    def delete_menu(self, menu_id):
        """
        删除菜单（会级联删除菜单项）
        
        Args:
            menu_id (int): 菜单ID
        
        Raises:
            ValueError: 当菜单有关联订单时
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查是否有关联的订单
        cursor.execute('SELECT COUNT(*) as count FROM orders WHERE menu_id = ?', (menu_id,))
        order_count = cursor.fetchone()['count']
        
        if order_count > 0:
            conn.close()
            raise ValueError('该菜单有关联订单，无法删除')
        
        try:
            cursor.execute('DELETE FROM menus WHERE id = ?', (menu_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
    
    def update_stock(self, menu_item_id, quantity_change):
        """
        更新库存（用于下单和取消）
        
        Args:
            menu_item_id (int): 菜单项ID
            quantity_change (int): 数量变化（负数表示扣减，正数表示增加）
        
        Raises:
            ValueError: 当库存不足时
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = get_current_datetime()
        
        try:
            cursor.execute('''
                SELECT available_quantity FROM menu_items WHERE id = ?
            ''', (menu_item_id,))
            
            item = cursor.fetchone()
            if not item:
                conn.close()
                raise ValueError('菜单项不存在')
            
            new_available = item['available_quantity'] + quantity_change
            
            if new_available < 0:
                conn.close()
                raise ValueError('库存不足')
            
            cursor.execute('''
                UPDATE menu_items
                SET available_quantity = ?, updated_at = ?
                WHERE id = ?
            ''', (new_available, now, menu_item_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
