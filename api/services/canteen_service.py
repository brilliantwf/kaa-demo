# 食堂服务

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.helpers import get_db_connection, get_current_datetime, dict_from_row, list_from_rows
import config


class CanteenService:
    """食堂服务类"""
    
    def get_canteen_list(self, status=None):
        """
        获取食堂列表
        
        Args:
            status (str): 状态过滤 (active/inactive)
        
        Returns:
            list: 食堂列表
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute('SELECT * FROM canteens WHERE status = ? ORDER BY id', (status,))
        else:
            cursor.execute('SELECT * FROM canteens ORDER BY id')
        
        canteens = cursor.fetchall()
        conn.close()
        
        return list_from_rows(canteens)
    
    def get_canteen_by_id(self, canteen_id):
        """
        获取食堂详情
        
        Args:
            canteen_id (int): 食堂ID
        
        Returns:
            dict: 食堂信息
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM canteens WHERE id = ?', (canteen_id,))
        canteen = cursor.fetchone()
        conn.close()
        
        return dict_from_row(canteen)
    
    def create_canteen(self, name, address, phone):
        """
        创建食堂
        
        Args:
            name (str): 食堂名称
            address (str): 地址
            phone (str): 电话
        
        Returns:
            int: 新创建的食堂ID
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = get_current_datetime()
        
        try:
            cursor.execute('''
                INSERT INTO canteens (name, address, phone, status, created_at, updated_at)
                VALUES (?, ?, ?, 'active', ?, ?)
            ''', (name, address, phone, now, now))
            
            canteen_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return canteen_id
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
    
    def update_canteen(self, canteen_id, name, address, phone):
        """
        更新食堂信息
        
        Args:
            canteen_id (int): 食堂ID
            name (str): 食堂名称
            address (str): 地址
            phone (str): 电话
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = get_current_datetime()
        
        try:
            cursor.execute('''
                UPDATE canteens
                SET name = ?, address = ?, phone = ?, updated_at = ?
                WHERE id = ?
            ''', (name, address, phone, now, canteen_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
    
    def delete_canteen(self, canteen_id):
        """
        删除食堂
        
        Args:
            canteen_id (int): 食堂ID
        
        Raises:
            ValueError: 当食堂有关联数据时
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查是否有关联的菜品
        cursor.execute('SELECT COUNT(*) as count FROM dishes WHERE canteen_id = ?', (canteen_id,))
        dish_count = cursor.fetchone()['count']
        
        if dish_count > 0:
            conn.close()
            raise ValueError('该食堂有关联菜品，无法删除')
        
        # 检查是否有关联的菜单
        cursor.execute('SELECT COUNT(*) as count FROM menus WHERE canteen_id = ?', (canteen_id,))
        menu_count = cursor.fetchone()['count']
        
        if menu_count > 0:
            conn.close()
            raise ValueError('该食堂有关联菜单，无法删除')
        
        try:
            cursor.execute('DELETE FROM canteens WHERE id = ?', (canteen_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
    
    def get_staff_canteens(self, user_id):
        """
        获取食堂人员管理的食堂列表
        
        Args:
            user_id (int): 用户ID
        
        Returns:
            list: 食堂列表
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*
            FROM canteens c
            INNER JOIN canteen_staff_relations csr ON c.id = csr.canteen_id
            WHERE csr.user_id = ?
            ORDER BY c.id
        ''', (user_id,))
        
        canteens = cursor.fetchall()
        conn.close()
        
        return list_from_rows(canteens)
