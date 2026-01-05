#!/bin/bash
# 一键停止脚本

echo "========================================"
echo "集团员工内部用餐点餐平台 - 停止服务"
echo "========================================"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 停止API服务
if [ -f "./pids/api.pid" ]; then
    API_PID=$(cat ./pids/api.pid)
    if ps -p $API_PID > /dev/null 2>&1; then
        kill $API_PID
        echo "API服务已停止 (PID: $API_PID)"
    else
        echo "API服务未运行"
    fi
    rm ./pids/api.pid
fi

# 停止管理端Web服务
if [ -f "./pids/admin.pid" ]; then
    ADMIN_PID=$(cat ./pids/admin.pid)
    if ps -p $ADMIN_PID > /dev/null 2>&1; then
        kill $ADMIN_PID
        echo "管理端Web服务已停止 (PID: $ADMIN_PID)"
    else
        echo "管理端Web服务未运行"
    fi
    rm ./pids/admin.pid
fi

# 停止员工端Web服务
if [ -f "./pids/user.pid" ]; then
    USER_PID=$(cat ./pids/user.pid)
    if ps -p $USER_PID > /dev/null 2>&1; then
        kill $USER_PID
        echo "员工端Web服务已停止 (PID: $USER_PID)"
    else
        echo "员工端Web服务未运行"
    fi
    rm ./pids/user.pid
fi

echo "========================================"
echo "所有服务已停止！"
echo "========================================"
