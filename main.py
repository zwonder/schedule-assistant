"""
个人工作助理 - 启动入口
运行此文件将启动 Web 服务并自动打开浏览器
"""
import sys
import os
import threading
import webbrowser
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, init_services

HOST = "127.0.0.1"
PORT = 5001
URL  = f"http://{HOST}:{PORT}"


def open_browser():
    """延迟1秒后打开浏览器，确保服务已启动"""
    time.sleep(1.2)
    webbrowser.open(URL)


if __name__ == "__main__":
    # 初始化所有微服务
    init_services()

    print("\n" + "=" * 50)
    print("  个人工作助理 v1.0.0")
    print("=" * 50)
    print(f"  服务地址: {URL}")
    print("  按 Ctrl+C 停止服务")
    print("=" * 50 + "\n")

    # 在新线程中打开浏览器
    threading.Thread(target=open_browser, daemon=True).start()

    app.run(host=HOST, port=PORT, debug=False, use_reloader=False)
