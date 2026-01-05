#!/bin/bash
# 一键启动脚本

echo "========================================"
echo "集团员工内部用餐点餐平台 - 启动服务"
echo "========================================"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 创建pids目录
mkdir -p pids

# 激活Conda环境
echo "激活Conda环境: ordering-system"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate ordering-system

if [ $? -ne 0 ]; then
    echo "错误: 无法激活Conda环境 ordering-system"
    echo "请先创建环境: conda env create -f environment.yml"
    exit 1
fi

# 检查并初始化数据库
if [ ! -f "./data/ordering_system.db" ]; then
    echo "数据库不存在，开始初始化..."
    cd api && python init_db.py
    if [ $? -ne 0 ]; then
        echo "错误: 数据库初始化失败"
        exit 1
    fi
    cd ..
fi

# 启动API服务
echo "----------------------------------------"
echo "启动API服务 (端口: 5000)..."
cd api
nohup python app.py > ../logs/api.log 2>&1 &
API_PID=$!
echo $API_PID > ../pids/api.pid
echo "API服务已启动 (PID: $API_PID)"
cd ..

# 等待API服务启动
sleep 2

# 启动管理端Web服务
echo "----------------------------------------"
echo "启动管理端Web服务 (端口: 8080)..."
cd admin-web
nohup python -m http.server 8080 > ../logs/admin-web.log 2>&1 &
ADMIN_PID=$!
echo $ADMIN_PID > ../pids/admin.pid
echo "管理端Web服务已启动 (PID: $ADMIN_PID)"
cd ..

# 启动员工端Web服务
echo "----------------------------------------"
echo "启动员工端Web服务 (端口: 8081)..."
cd user-web
nohup python -m http.server 8081 > ../logs/user-web.log 2>&1 &
USER_PID=$!
echo $USER_PID > ../pids/user.pid
echo "员工端Web服务已启动 (PID: $USER_PID)"
cd ..

echo "========================================"
echo "所有服务已启动！"
echo "========================================"
echo "API服务:     http://localhost:5000"
echo "管理端:      http://localhost:8080"
echo "员工端:      http://localhost:8081"
echo "========================================"
echo "查看日志:"
echo "  API日志:      tail -f logs/api.log"
echo "  管理端日志:   tail -f logs/admin-web.log"
echo "  员工端日志:   tail -f logs/user-web.log"
echo "========================================"
