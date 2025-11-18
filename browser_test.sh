#!/bin/bash
# 瀏覽器自動化測試 - 快速啟動腳本

set -e  # 遇到錯誤立即退出

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印帶顏色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 打印標題
print_header() {
    echo ""
    echo "======================================================================"
    echo "  $1"
    echo "======================================================================"
    echo ""
}

# 檢查 Python
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 未安裝"
        exit 1
    fi
    print_success "Python 3 已安裝: $(python3 --version)"
}

# 檢查依賴
check_dependencies() {
    print_info "檢查依賴..."

    if ! python3 -c "import playwright" 2>/dev/null; then
        print_warning "Playwright 未安裝"
        read -p "是否安裝依賴？ (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "安裝依賴..."
            pip install -r requirements-browser-test.txt
            print_info "安裝瀏覽器..."
            playwright install chromium
            print_success "依賴安裝完成"
        else
            print_error "請先安裝依賴: pip install -r requirements-browser-test.txt"
            exit 1
        fi
    else
        print_success "依賴已安裝"
    fi
}

# 顯示幫助
show_help() {
    print_header "瀏覽器自動化測試 - 快速啟動"

    echo "用法: ./browser_test.sh [選項]"
    echo ""
    echo "選項:"
    echo "  -h, --help          顯示此幫助信息"
    echo "  -i, --install       安裝依賴"
    echo "  -v, --visible       顯示瀏覽器（可見模式）"
    echo "  -f, --fast          快速模式（不延遲）"
    echo "  -b, --browser BROWSER 選擇瀏覽器 (chromium|firefox|webkit)"
    echo "  -p, --port PORT     Web 服務器端口（默認 5000）"
    echo "  -s, --server-only   僅啟動服務器"
    echo "  -t, --test-only     僅運行測試"
    echo ""
    echo "示例:"
    echo "  ./browser_test.sh                 # 默認模式"
    echo "  ./browser_test.sh -v              # 顯示瀏覽器"
    echo "  ./browser_test.sh -f              # 快速模式"
    echo "  ./browser_test.sh -b firefox      # 使用 Firefox"
    echo "  ./browser_test.sh -p 8080         # 使用端口 8080"
    echo "  ./browser_test.sh -s              # 僅啟動服務器"
    echo ""
}

# 解析命令行參數
HEADLESS="--headless"
FAST=""
BROWSER="chromium"
PORT="5000"
SERVER_ONLY=""
TEST_ONLY=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -i|--install)
            print_info "安裝依賴..."
            pip install -r requirements-browser-test.txt
            playwright install
            print_success "依賴安裝完成"
            exit 0
            ;;
        -v|--visible)
            HEADLESS=""
            shift
            ;;
        -f|--fast)
            FAST="--fast"
            shift
            ;;
        -b|--browser)
            BROWSER="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -s|--server-only)
            SERVER_ONLY="--server-only"
            shift
            ;;
        -t|--test-only)
            TEST_ONLY="--test-only"
            shift
            ;;
        *)
            print_error "未知選項: $1"
            show_help
            exit 1
            ;;
    esac
done

# 主函數
main() {
    print_header "瀏覽器自動化測試"

    # 檢查環境
    check_python
    check_dependencies

    # 構建命令
    CMD="python3 run_browser_test.py"
    CMD="$CMD --browser $BROWSER"
    CMD="$CMD --port $PORT"
    CMD="$CMD $HEADLESS"
    CMD="$CMD $FAST"
    CMD="$CMD $SERVER_ONLY"
    CMD="$CMD $TEST_ONLY"

    # 顯示配置
    print_info "測試配置:"
    echo "  - 瀏覽器: $BROWSER"
    echo "  - 端口: $PORT"
    if [ -z "$HEADLESS" ]; then
        echo "  - 模式: 可見模式"
    else
        echo "  - 模式: 無頭模式"
    fi
    if [ -n "$FAST" ]; then
        echo "  - 速度: 快速模式"
    fi
    echo ""

    # 運行測試
    print_info "開始測試..."
    print_info "命令: $CMD"
    echo ""

    eval $CMD
    EXIT_CODE=$?

    echo ""
    if [ $EXIT_CODE -eq 0 ]; then
        print_success "測試完成！"
        print_info "查看結果:"
        echo "  - 截圖: tests/browser/screenshots/"
        echo "  - 報告: tests/browser/test_results.json"
    else
        print_error "測試失敗 (退出碼: $EXIT_CODE)"
    fi

    exit $EXIT_CODE
}

# 運行主函數
main
