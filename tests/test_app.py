# tests/test_app.py

import pytest
import json
import numpy as np
import pandas as pd

# --- 健康检查测试 ---

def test_health_check(client):
    """测试 /health 端点是否正常工作。"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'message' in data

# --- 推荐接口测试 ---

def test_recommendations_valid_user(client):
    """测试使用有效的用户 ID 请求推荐。"""
    user_id = 1 # 假设用户 1 存在
    response = client.post('/recommendations', json={'user_id': user_id})
    assert response.status_code == 200
    data = json.loads(response.data)

    # 检查返回的数据结构
    assert 'user_based' in data
    assert 'item_based' in data
    assert 'hybrid' in data
    # assert 'user_profile' in data # 如果你添加了用户信息

    # 检查每个推荐列表的结构
    for method in ['user_based', 'item_based', 'hybrid']:
        recommendations = data[method]
        assert isinstance(recommendations, list)
        # 检查列表不为空（对于小数据集可能为空，但通常不为空）
        # assert len(recommendations) > 0, f"{method} 推荐列表为空"

        if recommendations: # 如果列表不为空，则检查内容
            for rec in recommendations:
                assert 'course_id' in rec
                assert 'title' in rec
                assert 'category' in rec
                assert 'difficulty' in rec
                assert 'score' in rec
                # 检查类型是否为 Python 原生类型，避免序列化错误
                assert isinstance(rec['course_id'], int), f"course_id should be int, got {type(rec['course_id'])}"
                assert isinstance(rec['score'], (int, float)), f"score should be int or float, got {type(rec['score'])}"
                assert isinstance(rec['title'], str), f"title should be str, got {type(rec['title'])}"
                assert isinstance(rec['category'], str), f"category should be str, got {type(rec['category'])}"
                assert isinstance(rec['difficulty'], str), f"difficulty should be str, got {type(rec['difficulty'])}"

    # 可选：检查用户信息（如果返回）
    # if 'user_profile' in data:
    #     profile = data['user_profile']
    #     assert 'user_id' in profile
    #     assert 'name' in profile
    #     # ... 检查其他字段

def test_recommendations_invalid_user_id(client):
    """测试使用不存在的用户 ID 请求推荐。"""
    invalid_user_id = 999999 # 假设这个用户不存在
    response = client.post('/recommendations', json={'user_id': invalid_user_id})
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert str(invalid_user_id) in data['error'] # 错误信息应包含用户ID

def test_recommendations_missing_user_id(client):
    """测试请求体中缺少 user_id。"""
    response = client.post('/recommendations', json={}) # 空的 JSON
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'user_id' in data['error']

def test_recommendations_invalid_user_id_type(client):
    """测试 user_id 类型无效（非整数）。"""
    response = client.post('/recommendations', json={'user_id': 'invalid_string'})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'integer' in data['error']

    response = client.post('/recommendations', json={'user_id': 1.5}) # 浮点数
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'integer' in data['error']

def test_recommendations_wrong_http_method(client):
    """测试使用错误的 HTTP 方法访问端点。"""
    response = client.get('/recommendations') # 应该是 POST
    assert response.status_code == 405 # Method Not Allowed

    response = client.put('/recommendations', json={'user_id': 1})
    assert response.status_code == 405 # Method Not Allowed

# --- 数据加载和模型初始化测试 (集成测试的一部分) ---
# 这些测试依赖于 conftest.py 中的初始化

def test_model_and_data_loaded(flask_app):
    """测试模型和数据是否在应用启动时正确加载。"""
    with flask_app.app_context():
        # 从 app.py 导入全局变量 (需要在 app.py 中定义为 global)
        # 注意：直接访问全局变量可能需要 app.app_context()
        # 这里我们假设 app.py 有办法访问到这些变量，或者我们测试初始化函数的结果
        # 一个更直接的方法是在 app.py 中提供一个获取状态的函数
        # 但在这里，我们假设 load_model_and_data 已经在 conftest.py 中调用

        # 我们可以通过健康检查间接验证
        health_response = flask_app.test_client().get('/health')
        assert health_response.status_code == 200
        health_data = json.loads(health_response.data)
        assert health_data['status'] == 'healthy'

# --- 边界情况和鲁棒性测试 ---

# 为了测试这些，你可能需要一个特定的测试数据集
# 例如，一个用户没有任何评分记录的极端情况
# 这通常需要 mock 数据或一个专门的测试数据集
# 这里提供一个思路，但具体实现取决于你的 data_loader

# def test_recommendations_user_no_ratings(client, monkeypatch):
#     """测试用户没有任何评分记录的情况。"""
#     # 这需要 mock user_item_matrix 或 ratings_df
#     # 例如，可以 monkeypatch data_loader.load_data 返回一个特殊的数据集
#     # 或者在测试环境中使用不同的数据文件
#     pass

# --- 性能测试 (可选，使用 pytest-benchmark) ---
# 如果你需要性能测试，可以安装 pytest-benchmark
# pip install pytest-benchmark
#
# def test_recommendation_performance(client, benchmark):
#     """基准测试推荐生成的性能。"""
#     def fetch_recommendations():
#         response = client.post('/recommendations', json={'user_id': 1})
#         assert response.status_code == 200
#     # 运行基准测试
#     benchmark(fetch_recommendations)