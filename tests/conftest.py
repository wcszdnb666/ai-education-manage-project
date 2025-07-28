# tests/conftest.py

import pytest
import sys
import os
from app import app, load_model_and_data # 导入 Flask app 和初始化函数

# 确保 app.py 能找到 models 和 utils
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'models'))
sys.path.insert(0, os.path.join(project_root, 'utils'))

@pytest.fixture(scope='session')
def flask_app():
    """提供 Flask 应用实例的 fixture。"""
    # 配置应用为测试模式
    app.config.update({
        "TESTING": True,
    })
    # 确保在测试前加载模型和数据
    # 注意：这会在测试会话开始时运行一次
    with app.app_context():
        load_model_and_data()
    yield app

@pytest.fixture()
def client(flask_app):
    """提供一个测试客户端的 fixture。"""
    return flask_app.test_client()

# 如果你更喜欢使用 pytest-flask 的方式，可以使用 app 和 client fixtures
# 但上面的方式更明确地控制了初始化