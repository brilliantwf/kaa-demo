# 菜品服务

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.helpers import get_db_connection, get_current_datetime, dict_from_row, list_from_rows
import config


class DishService:
    """菜品服务类"""
    
    def get_dish_list(self, canteen_id=None, category_id=None, status=None):
        """
        获取菜品列表
        
        Args:
            canteen_id (int): 食堂ID
            category_id (int): 分类ID
            status (str): 状态 (active/inactive)
        
        Returns:
            list: 菜品列表
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT d.*, c.name as category_name
            FROM dishes d
            LEFT JOIN dish_categories c ON d.category_id = c.id
            WHERE 1=1
        '''
        params = []
        
        if canteen_id:
            query += ' AND d.canteen_id = ?'
            params.append(canteen_id)
        
        if category_id:
            query += ' AND d.category_id = ?'
            params.append(category_id)
        
        if status:
            query += ' AND d.status = ?'
            params.append(status)
        
        query += ' ORDER BY d.category_id, d.id'
        
        cursor.execute(query, params)
        dishes = cursor.fetchall()
        conn.close()
        
        return list_from_rows(dishes)
    
    def get_dish_by_id(self, dish_id):
        """
        获取菜品详情
        
        Args:
            dish_id (int): 菜品ID
        
        Returns:
            dict: 菜品信息
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.*, c.name as category_name
            FROM dishes d
            LEFT JOIN dish_categories c ON d.category_id = c.id
            WHERE d.id = ?
        ''', (dish_id,))
        
        dish = cursor.fetchone()
        conn.close()
        
        return dict_from_row(dish)
    
    def create_dish(self, name, category_id, canteen_id, price=0, image_url='', description=''):
        """
        创建菜品
        
        Args:
            name (str): 菜品名称
            category_id (int): 分类ID
            canteen_id (int): 食堂ID
            price (float): 价格
            image_url (str): 图片URL
            description (str): 描述
        
        Returns:
            int: 新创建的菜品ID
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = get_current_datetime()
        
        try:
            cursor.execute('''
                INSERT INTO dishes (name, category_id, price, image_url, description, 
                                   status, canteen_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'active', ?, ?, ?)
            ''', (name, category_id, price, image_url, description, canteen_id, now, now))
            
            dish_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return dish_id
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
    
    def update_dish(self, dish_id, name, category_id, price, image_url, description):
        """
        更新菜品信息
        
        Args:
            dish_id (int): 菜品ID
            name (str): 菜品名称
            category_id (int): 分类ID
            price (float): 价格
            image_url (str): 图片URL
            description (str): 描述
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = get_current_datetime()
        
        try:
            cursor.execute('''
                UPDATE dishes
                SET name = ?, category_id = ?, price = ?, image_url = ?, 
                    description = ?, updated_at = ?
                WHERE id = ?
            ''', (name, category_id, price, image_url, description, now, dish_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
    
    def update_dish_status(self, dish_id, status):
        """
        更新菜品状态（上架/下架）
        
        Args:
            dish_id (int): 菜品ID
            status (str): 状态 (active/inactive)
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = get_current_datetime()
        
        try:
            cursor.execute('''
                UPDATE dishes
                SET status = ?, updated_at = ?
                WHERE id = ?
            ''', (status, now, dish_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
    
    def delete_dish(self, dish_id):
        """
        删除菜品
        
        Args:
            dish_id (int): 菜品ID
        
        Raises:
            ValueError: 当菜品有关联数据时
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查是否有关联的菜单项
        cursor.execute('SELECT COUNT(*) as count FROM menu_items WHERE dish_id = ?', (dish_id,))
        menu_item_count = cursor.fetchone()['count']
        
        if menu_item_count > 0:
            conn.close()
            raise ValueError('该菜品已被使用，无法删除')
        
        try:
            cursor.execute('DELETE FROM dishes WHERE id = ?', (dish_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
    
    def get_categories(self):
        """
        获取菜品分类列表
        
        Returns:
            list: 分类列表
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM dish_categories ORDER BY sort_order, id')
        categories = cursor.fetchall()
        conn.close()
        
        return list_from_rows(categories)
