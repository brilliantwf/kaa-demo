// 管理端前端应用

const API_BASE_URL = 'http://localhost:8082/api';
let currentUser = null;

// 工具函数
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

// API请求封装
async function apiRequest(url, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (currentUser) {
        headers['X-User-Id'] = currentUser.id;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${url}`, {
            ...options,
            headers
        });
        
        const data = await response.json();
        
        if (data.code !== 0) {
            throw new Error(data.message);
        }
        
        return data.data;
    } catch (error) {
        alert(`请求失败: ${error.message}`);
        throw error;
    }
}

// 登录
$('#loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const employeeId = $('#employeeId').value;
    const password = $('#password').value;
    
    try {
        const user = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ employee_id: employeeId, password })
        });
        
        if (user.role !== 'admin' && user.role !== 'canteen_staff') {
            alert('只有管理员和食堂人员可以登录管理端');
            return;
        }
        
        currentUser = user;
        $('#userName').textContent = user.full_name;
        $('#logoutBtn').style.display = 'inline-block';
        $('#loginPage').style.display = 'none';
        $('#mainPage').style.display = 'flex';
        
        // 加载初始数据
        loadCanteens();
        loadCanteenFilters();
    } catch (error) {
        // 错误已在apiRequest中处理
    }
});

// 退出登录
$('#logoutBtn').addEventListener('click', () => {
    currentUser = null;
    $('#userName').textContent = '未登录';
    $('#logoutBtn').style.display = 'none';
    $('#loginPage').style.display = 'block';
    $('#mainPage').style.display = 'none';
    $('#loginForm').reset();
});

// 页面导航
$$('.sidebar a').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        
        // 移除所有active类
        $$('.sidebar a').forEach(a => a.classList.remove('active'));
        e.target.classList.add('active');
        
        // 隐藏所有内容页面
        $$('.content-page').forEach(page => page.style.display = 'none');
        
        // 显示对应页面
        const pageName = e.target.dataset.page;
        $(`#${pageName}Page`).style.display = 'block';
        
        // 加载对应数据
        switch(pageName) {
            case 'canteens':
                loadCanteens();
                break;
            case 'dishes':
                loadDishes();
                break;
            case 'menus':
                loadMenus();
                break;
            case 'orders':
                loadOrders();
                break;
            case 'statistics':
                break;
        }
    });
});

// 加载食堂列表
async function loadCanteens() {
    try {
        const canteens = await apiRequest('/canteens');
        
        const html = `
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>食堂名称</th>
                        <th>地址</th>
                        <th>联系电话</th>
                        <th>状态</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    ${canteens.map(c => `
                        <tr>
                            <td>${c.id}</td>
                            <td>${c.name}</td>
                            <td>${c.address || '-'}</td>
                            <td>${c.phone || '-'}</td>
                            <td><span class="status-badge status-${c.status}">${c.status === 'active' ? '启用' : '禁用'}</span></td>
                            <td>
                                <div class="action-buttons">
                                    <button class="btn-view" onclick="viewCanteen(${c.id})">查看</button>
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        $('#canteensList').innerHTML = canteens.length > 0 ? html : '<div class="empty-state">暂无食堂数据</div>';
    } catch (error) {
        // 错误已处理
    }
}

// 加载食堂过滤器
async function loadCanteenFilters() {
    try {
        const canteens = await apiRequest('/canteens?status=active');
        
        const options = canteens.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
        
        $('#canteenFilter').innerHTML = '<option value="">选择食堂</option>' + options;
        $('#menuCanteenFilter').innerHTML = '<option value="">选择食堂</option>' + options;
        $('#orderCanteenFilter').innerHTML = '<option value="">选择食堂</option>' + options;
        $('#statsCanteenFilter').innerHTML = '<option value="">选择食堂</option>' + options;
    } catch (error) {
        // 错误已处理
    }
}

// 加载菜品列表
async function loadDishes() {
    const canteenId = $('#canteenFilter').value;
    const status = $('#statusFilter').value;
    
    let url = '/dishes?';
    if (canteenId) url += `canteen_id=${canteenId}&`;
    if (status) url += `status=${status}&`;
    
    try {
        const dishes = await apiRequest(url);
        
        const html = `
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>菜品名称</th>
                        <th>分类</th>
                        <th>价格</th>
                        <th>状态</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    ${dishes.map(d => `
                        <tr>
                            <td>${d.id}</td>
                            <td>${d.name}</td>
                            <td>${d.category_name}</td>
                            <td>¥${d.price.toFixed(2)}</td>
                            <td><span class="status-badge status-${d.status}">${d.status === 'active' ? '已上架' : '已下架'}</span></td>
                            <td>
                                <div class="action-buttons">
                                    <button class="btn-view" onclick="viewDish(${d.id})">查看</button>
                                    ${d.status === 'inactive' 
                                        ? `<button class="btn-enable" onclick="enableDish(${d.id})">上架</button>`
                                        : `<button class="btn-disable" onclick="disableDish(${d.id})">下架</button>`
                                    }
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        $('#dishesList').innerHTML = dishes.length > 0 ? html : '<div class="empty-state">暂无菜品数据</div>';
    } catch (error) {
        // 错误已处理
    }
}

$('#filterDishesBtn').addEventListener('click', loadDishes);

// 加载菜单列表
async function loadMenus() {
    const canteenId = $('#menuCanteenFilter').value;
    const menuDate = $('#menuDateFilter').value;
    
    let url = '/menus?';
    if (canteenId) url += `canteen_id=${canteenId}&`;
    if (menuDate) url += `menu_date=${menuDate}&`;
    
    try {
        const menus = await apiRequest(url);
        
        const mealTypeMap = {
            'breakfast': '早餐',
            'lunch': '午餐',
            'dinner': '晚餐'
        };
        
        const html = `
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>食堂</th>
                        <th>日期</th>
                        <th>餐次</th>
                        <th>状态</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    ${menus.map(m => `
                        <tr>
                            <td>${m.id}</td>
                            <td>${m.canteen_name}</td>
                            <td>${m.menu_date}</td>
                            <td>${mealTypeMap[m.meal_type]}</td>
                            <td><span class="status-badge status-${m.status}">${m.status === 'active' ? '启用' : '禁用'}</span></td>
                            <td>
                                <div class="action-buttons">
                                    <button class="btn-view" onclick="viewMenu(${m.id})">查看详情</button>
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        $('#menusList').innerHTML = menus.length > 0 ? html : '<div class="empty-state">暂无菜单数据</div>';
    } catch (error) {
        // 错误已处理
    }
}

$('#filterMenusBtn').addEventListener('click', loadMenus);

// 查看菜单详情
async function viewMenu(menuId) {
    try {
        const menu = await apiRequest(`/menus/${menuId}`);
        
        const itemsHtml = menu.items.map(item => `
            <tr>
                <td>${item.dish_name}</td>
                <td>${item.category_name}</td>
                <td>${item.quantity}</td>
                <td>${item.available_quantity}</td>
            </tr>
        `).join('');
        
        const detailHtml = `
            <div class="stats-card">
                <h3>菜单详情</h3>
                <p>食堂: ${menu.canteen_name}</p>
                <p>日期: ${menu.menu_date}</p>
                <p>餐次: ${menu.meal_type}</p>
                <table>
                    <thead>
                        <tr>
                            <th>菜品名称</th>
                            <th>分类</th>
                            <th>总数量</th>
                            <th>剩余数量</th>
                        </tr>
                    </thead>
                    <tbody>${itemsHtml}</tbody>
                </table>
            </div>
        `;
        
        alert('菜单详情（简化显示）:\n' + JSON.stringify(menu, null, 2));
    } catch (error) {
        // 错误已处理
    }
}

// 加载订单列表
async function loadOrders() {
    const canteenId = $('#orderCanteenFilter').value;
    const orderDate = $('#orderDateFilter').value;
    const mealType = $('#orderMealTypeFilter').value;
    
    if (!canteenId) {
        $('#ordersList').innerHTML = '<div class="empty-state">请选择食堂</div>';
        return;
    }
    
    let url = `/orders/canteen/${canteenId}?`;
    if (orderDate) url += `order_date=${orderDate}&`;
    if (mealType) url += `meal_type=${mealType}&`;
    
    try {
        const orders = await apiRequest(url);
        
        const mealTypeMap = {
            'breakfast': '早餐',
            'lunch': '午餐',
            'dinner': '晚餐'
        };
        
        const statusMap = {
            'placed': '已下单',
            'cancelled': '已取消',
            'completed': '已完成'
        };
        
        const html = `
            <table>
                <thead>
                    <tr>
                        <th>订单号</th>
                        <th>员工</th>
                        <th>工号</th>
                        <th>日期</th>
                        <th>餐次</th>
                        <th>金额</th>
                        <th>状态</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    ${orders.map(o => `
                        <tr>
                            <td>${o.order_no}</td>
                            <td>${o.user_name}</td>
                            <td>${o.employee_id}</td>
                            <td>${o.order_date}</td>
                            <td>${mealTypeMap[o.meal_type]}</td>
                            <td>¥${o.total_amount.toFixed(2)}</td>
                            <td><span class="status-badge status-${o.status}">${statusMap[o.status]}</span></td>
                            <td>
                                <div class="action-buttons">
                                    <button class="btn-view" onclick="viewOrder(${o.id})">查看详情</button>
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        $('#ordersList').innerHTML = orders.length > 0 ? html : '<div class="empty-state">暂无订单数据</div>';
    } catch (error) {
        // 错误已处理
    }
}

$('#filterOrdersBtn').addEventListener('click', loadOrders);

// 查看订单详情
async function viewOrder(orderId) {
    try {
        const order = await apiRequest(`/orders/${orderId}`);
        alert('订单详情（简化显示）:\n' + JSON.stringify(order, null, 2));
    } catch (error) {
        // 错误已处理
    }
}

// 获取餐次统计
$('#getStatsBtn').addEventListener('click', async () => {
    const canteenId = $('#statsCanteenFilter').value;
    const orderDate = $('#statsDateFilter').value || new Date().toISOString().split('T')[0];
    const mealType = $('#statsMealTypeFilter').value;
    
    if (!canteenId || !mealType) {
        alert('请选择食堂和餐次');
        return;
    }
    
    try {
        const stats = await apiRequest(`/statistics/meal?canteen_id=${canteenId}&order_date=${orderDate}&meal_type=${mealType}`);
        
        const dishStatsHtml = `
            <table>
                <thead>
                    <tr>
                        <th>菜品名称</th>
                        <th>订单数</th>
                        <th>总数量</th>
                    </tr>
                </thead>
                <tbody>
                    ${stats.dish_statistics.map(d => `
                        <tr>
                            <td>${d.dish_name}</td>
                            <td>${d.order_count}</td>
                            <td>${d.total_quantity}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        const userStatsHtml = `
            <table>
                <thead>
                    <tr>
                        <th>工号</th>
                        <th>姓名</th>
                        <th>订单号</th>
                        <th>下单时间</th>
                    </tr>
                </thead>
                <tbody>
                    ${stats.user_statistics.map(u => `
                        <tr>
                            <td>${u.employee_id}</td>
                            <td>${u.full_name}</td>
                            <td>${u.order_no}</td>
                            <td>${u.created_at}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        const html = `
            <div class="stats-card">
                <h3>订单总数: ${stats.total_orders}</h3>
            </div>
            <div class="stats-section">
                <h3>按菜品统计</h3>
                ${dishStatsHtml}
            </div>
            <div class="stats-section">
                <h3>按员工统计</h3>
                ${userStatsHtml}
            </div>
        `;
        
        $('#statisticsContent').innerHTML = html;
    } catch (error) {
        // 错误已处理
    }
});

// 设置默认日期
const today = new Date().toISOString().split('T')[0];
$('#menuDateFilter').value = today;
$('#orderDateFilter').value = today;
$('#statsDateFilter').value = today;

// 占位函数
function viewCanteen(id) {
    alert(`查看食堂 ID: ${id}`);
}

function viewDish(id) {
    alert(`查看菜品 ID: ${id}`);
}

// 上架菜品
async function enableDish(dishId) {
    if (!confirm('确认要上架该菜品吗？')) {
        return;
    }
    
    try {
        await apiRequest(`/dishes/${dishId}/status`, {
            method: 'PUT',
            body: JSON.stringify({ status: 'active' })
        });
        
        alert('菜品上架成功！');
        loadDishes(); // 刷新菜品列表
    } catch (error) {
        // 错误已在apiRequest中处理
    }
}

// 下架菜品
async function disableDish(dishId) {
    if (!confirm('确认要下架该菜品吗？')) {
        return;
    }
    
    try {
        await apiRequest(`/dishes/${dishId}/status`, {
            method: 'PUT',
            body: JSON.stringify({ status: 'inactive' })
        });
        
        alert('菜品下架成功！');
        loadDishes(); // 刷新菜品列表
    } catch (error) {
        // 错误已在apiRequest中处理
    }
}
