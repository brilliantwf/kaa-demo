// 员工端H5前端应用

const API_BASE_URL = 'http://localhost:5000/api';
let currentUser = null;
let selectedCanteen = null;
let selectedMenuId = null;
let cart = {};

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
        
        if (user.role !== 'employee') {
            alert('只有员工可以登录员工端');
            return;
        }
        
        currentUser = user;
        $('#userName').textContent = user.full_name;
        $('#loginPage').style.display = 'none';
        $('#mainPage').style.display = 'block';
        
        // 加载首页数据
        loadHomePage();
    } catch (error) {
        // 错误已处理
    }
});

// 退出登录
$('#logoutBtn').addEventListener('click', () => {
    currentUser = null;
    selectedCanteen = null;
    cart = {};
    $('#loginPage').style.display = 'block';
    $('#mainPage').style.display = 'none';
    $('#loginForm').reset();
});

// 底部导航
$$('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        
        // 移除所有active类
        $$('.nav-item').forEach(nav => nav.classList.remove('active'));
        e.target.closest('.nav-item').classList.add('active');
        
        // 隐藏所有内容页面
        $$('.content-page').forEach(page => page.style.display = 'none');
        
        // 显示对应页面
        const pageName = e.target.closest('.nav-item').dataset.page;
        $(`#${pageName}Page`).style.display = 'block';
        
        // 加载对应数据
        switch(pageName) {
            case 'home':
                loadHomePage();
                break;
            case 'orders':
                loadMyOrders();
                break;
        }
    });
});

// 加载首页
async function loadHomePage() {
    // 显示当前日期
    const now = new Date();
    const dateStr = now.toLocaleDateString('zh-CN', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        weekday: 'long'
    });
    $('#currentDate').textContent = dateStr;
    
    // 加载食堂列表
    try {
        const canteens = await apiRequest('/canteens?status=active');
        
        const html = canteens.map(c => `
            <div class="canteen-card" onclick="selectCanteen(${c.id}, '${c.name}')">
                <h4>${c.name}</h4>
                <p>📍 ${c.address || '暂无地址'}</p>
                <p>📞 ${c.phone || '暂无电话'}</p>
            </div>
        `).join('');
        
        $('#canteenList').innerHTML = html;
        
        // 加载日历视图
        loadCalendarView();
    } catch (error) {
        // 错误已处理
    }
}

// 加载日历视图
async function loadCalendarView() {
    const dates = [];
    const today = new Date();
    
    // 显示今天和未来6天
    for (let i = 0; i < 7; i++) {
        const date = new Date(today);
        date.setDate(today.getDate() + i);
        dates.push(date);
    }
    
    const html = dates.map(date => {
        const dateStr = date.toISOString().split('T')[0];
        const dayStr = date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' });
        const weekday = ['日', '一', '二', '三', '四', '五', '六'][date.getDay()];
        
        return `
            <div class="calendar-item" onclick="selectDate('${dateStr}')">
                <div class="date">${dayStr} 周${weekday}</div>
                <div class="meals">可预订餐次</div>
            </div>
        `;
    }).join('');
    
    $('#calendarView').innerHTML = html;
}

// 选择食堂
function selectCanteen(canteenId, canteenName) {
    selectedCanteen = { id: canteenId, name: canteenName };
    
    // 切换到点餐页面
    $$('.nav-item').forEach(nav => nav.classList.remove('active'));
    $$('.nav-item')[1].classList.add('active');
    $$('.content-page').forEach(page => page.style.display = 'none');
    $('#orderPage').style.display = 'block';
    
    // 显示食堂名称
    $('#selectedCanteen').textContent = canteenName;
    
    // 设置默认日期为今天
    $('#orderDate').value = new Date().toISOString().split('T')[0];
}

// 选择日期
function selectDate(dateStr) {
    // 切换到点餐页面
    $$('.nav-item').forEach(nav => nav.classList.remove('active'));
    $$('.nav-item')[1].classList.add('active');
    $$('.content-page').forEach(page => page.style.display = 'none');
    $('#orderPage').style.display = 'block';
    
    // 设置日期
    $('#orderDate').value = dateStr;
}

// 返回首页
$('#backToHome').addEventListener('click', () => {
    $$('.nav-item').forEach(nav => nav.classList.remove('active'));
    $$('.nav-item')[0].classList.add('active');
    $$('.content-page').forEach(page => page.style.display = 'none');
    $('#homePage').style.display = 'block';
});

// 加载菜单
$('#loadMenuBtn').addEventListener('click', async () => {
    if (!selectedCanteen) {
        alert('请先选择食堂');
        return;
    }
    
    const orderDate = $('#orderDate').value;
    const mealType = $('#mealType').value;
    
    if (!orderDate || !mealType) {
        alert('请选择日期和餐次');
        return;
    }
    
    $('#selectedMeal').textContent = `${orderDate} - ${{'breakfast':'早餐','lunch':'午餐','dinner':'晚餐'}[mealType]}`;
    
    try {
        const menus = await apiRequest(`/menus?canteen_id=${selectedCanteen.id}&menu_date=${orderDate}&meal_type=${mealType}`);
        
        if (menus.length === 0) {
            $('#menuSection').style.display = 'none';
            alert('该餐次暂无菜单');
            return;
        }
        
        const menu = await apiRequest(`/menus/${menus[0].id}`);
        selectedMenuId = menu.id;
        
        // 清空购物车
        cart = {};
        
        const html = menu.items.map(item => `
            <div class="menu-item">
                <div class="menu-item-info">
                    <h4>${item.dish_name}</h4>
                    <p>${item.category_name} | 剩余: ${item.available_quantity}份</p>
                </div>
                <div class="menu-item-actions">
                    <div class="quantity-control">
                        <button onclick="decreaseQuantity(${item.dish_id})">-</button>
                        <span id="qty-${item.dish_id}">0</span>
                        <button onclick="increaseQuantity(${item.dish_id}, ${item.available_quantity})">+</button>
                    </div>
                </div>
            </div>
        `).join('');
        
        $('#menuItems').innerHTML = html;
        $('#menuSection').style.display = 'block';
        updateCartCount();
    } catch (error) {
        // 错误已处理
    }
});

// 增加数量
function increaseQuantity(dishId, maxQty) {
    const current = cart[dishId] || 0;
    if (current >= maxQty) {
        alert('已达到最大可选数量');
        return;
    }
    cart[dishId] = current + 1;
    $(`#qty-${dishId}`).textContent = cart[dishId];
    updateCartCount();
}

// 减少数量
function decreaseQuantity(dishId) {
    const current = cart[dishId] || 0;
    if (current <= 0) return;
    cart[dishId] = current - 1;
    if (cart[dishId] === 0) {
        delete cart[dishId];
    }
    $(`#qty-${dishId}`).textContent = cart[dishId] || 0;
    updateCartCount();
}

// 更新购物车数量
function updateCartCount() {
    const totalCount = Object.values(cart).reduce((sum, qty) => sum + qty, 0);
    $('#cartCount').textContent = totalCount;
}

// 提交订单
$('#submitOrderBtn').addEventListener('click', async () => {
    const items = Object.entries(cart).map(([dishId, quantity]) => ({
        dish_id: parseInt(dishId),
        quantity
    }));
    
    if (items.length === 0) {
        alert('请至少选择一个菜品');
        return;
    }
    
    const orderDate = $('#orderDate').value;
    const mealType = $('#mealType').value;
    
    try {
        await apiRequest('/orders', {
            method: 'POST',
            body: JSON.stringify({
                canteen_id: selectedCanteen.id,
                menu_id: selectedMenuId,
                meal_type: mealType,
                order_date: orderDate,
                items
            })
        });
        
        alert('下单成功！');
        
        // 清空购物车
        cart = {};
        updateCartCount();
        
        // 切换到订单页面
        $$('.nav-item').forEach(nav => nav.classList.remove('active'));
        $$('.nav-item')[2].classList.add('active');
        $$('.content-page').forEach(page => page.style.display = 'none');
        $('#ordersPage').style.display = 'block';
        
        loadMyOrders();
    } catch (error) {
        // 错误已处理
    }
});

// 订单过滤
$$('.filter-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        $$('.filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        
        const status = e.target.dataset.status;
        loadMyOrders(status);
    });
});

// 加载我的订单
async function loadMyOrders(status = '') {
    try {
        let url = '/orders/my';
        if (status) url += `?status=${status}`;
        
        const orders = await apiRequest(url);
        
        if (orders.length === 0) {
            $('#ordersList').innerHTML = '<div class="empty-state"><p>暂无订单</p></div>';
            return;
        }
        
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
        
        const html = orders.map(order => {
            const canCancel = order.status === 'placed';
            
            return `
                <div class="order-card">
                    <div class="order-header-info">
                        <span class="order-no">订单号: ${order.order_no}</span>
                        <span class="order-status status-${order.status}">${statusMap[order.status]}</span>
                    </div>
                    <div class="order-details">
                        <p>📍 ${order.canteen_name}</p>
                        <p>📅 ${order.order_date} ${mealTypeMap[order.meal_type]}</p>
                        <p>💰 金额: ¥${order.total_amount.toFixed(2)}</p>
                        <p>🕐 下单时间: ${order.created_at}</p>
                    </div>
                    ${canCancel ? `
                        <div class="order-actions">
                            <button onclick="viewOrderDetail(${order.id})">查看详情</button>
                            <button class="btn-cancel" onclick="cancelOrder(${order.id})">取消订单</button>
                        </div>
                    ` : `
                        <div class="order-actions">
                            <button onclick="viewOrderDetail(${order.id})">查看详情</button>
                        </div>
                    `}
                </div>
            `;
        }).join('');
        
        $('#ordersList').innerHTML = html;
    } catch (error) {
        // 错误已处理
    }
}

// 查看订单详情
async function viewOrderDetail(orderId) {
    try {
        const order = await apiRequest(`/orders/${orderId}`);
        
        const itemsText = order.items.map(item => 
            `${item.dish_name} x ${item.quantity}`
        ).join('\n');
        
        alert(`订单详情\n\n${itemsText}\n\n总金额: ¥${order.total_amount.toFixed(2)}`);
    } catch (error) {
        // 错误已处理
    }
}

// 取消订单
async function cancelOrder(orderId) {
    if (!confirm('确定要取消这个订单吗？')) {
        return;
    }
    
    try {
        await apiRequest(`/orders/${orderId}/cancel`, {
            method: 'POST'
        });
        
        alert('订单已取消');
        loadMyOrders();
    } catch (error) {
        // 错误已处理
    }
}

// 设置默认日期
$('#orderDate').value = new Date().toISOString().split('T')[0];
