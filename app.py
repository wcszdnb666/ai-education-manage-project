# app.py
import sys
import os
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np

# --- 假设你的项目结构是这样的 ---
# your_project/
#   app.py
#   models/
#     collaborative_filtering.py
#   utils/
#     data_loader.py (这个文件需要你自己提供，根据 main.txt 的 import 语句)
#   data/
#     users.csv
#     courses.csv
#     ratings.csv
# ------------------------------

# 将 models 和 utils 添加到 Python 路径，以便导入
# 注意：如果你的项目结构不同，需要调整这些路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'models'))
sys.path.insert(0, os.path.join(project_root, 'utils'))

# --- 关键修改 1: 导入 data_loader ---
# 你需要确保 utils/data_loader.py 存在并且有 load_data 和 create_user_item_matrix 函数
try:
    from collaborative_filtering import CollaborativeFiltering
    # 注意：data_loader 需要你自己实现，这里假设它在 utils 目录下
    # 如果它在根目录，就用 `import data_loader as data_loader_module`
    import data_loader as data_loader_module # 根据你的实际文件结构调整
    # from utils.data_loader import load_data, create_user_item_matrix # 备选方案
except ImportError as e:
    print(f"导入模块时出错: {e}")
    print("请检查你的项目结构和文件路径。")
    sys.exit(1)

app = Flask(__name__)

# 全局变量存储加载的数据和模型
users_df = None
courses_df = None
ratings_df = None
user_item_matrix = None
model = None


def format_recommendations(recommendations_list, courses_dataframe, method_name):
    """
    将推荐结果格式化为字典列表，方便转换为 JSON。
    修复 Object of type int64 is not JSON serializable 错误。
    """
    if not recommendations_list:
        return {method_name: []}

    formatted_recs = []
    for item in recommendations_list: # item 是一个元组 (course_id, score)
        # --- 关键修改 2: 更健壮的类型处理 ---
        try:
            # 确保元组解包正确
            course_id, score = item
        except ValueError:
            # 如果解包失败，跳过这个条目或记录错误
            app.logger.warning(f"无法解包推荐项: {item}")
            continue

        # 强制转换为 Python 原生类型
        try:
            course_id = int(course_id) # 转换 numpy.int64 to int
            score = float(score)       # 转换 numpy.float64 to float
        except (ValueError, TypeError) as e:
            app.logger.error(f"转换推荐项类型时出错 ({course_id}, {score}): {e}")
            continue # 跳过无法转换的项

        course_info = courses_dataframe[courses_dataframe['course_id'] == course_id]
        course_data = {
            "course_id": course_id,
            "title": "Unknown",
            "category": "Unknown",
            "difficulty": "Unknown",
            "score": round(score, 3) # round 返回 float
        }
        if not course_info.empty:
            # 安全地获取并转换 DataFrame 中的值
            try:
                course_data["title"] = str(course_info.iloc[0]['title'])
                course_data["category"] = str(course_info.iloc[0]['category'])
                course_data["difficulty"] = str(course_info.iloc[0]['difficulty'])
            except Exception as e:
                 app.logger.warning(f"获取课程 {course_id} 信息时出错: {e}")
                 # 保留默认的 "Unknown" 值

        formatted_recs.append(course_data)

    return {method_name: formatted_recs}


@app.route('/health', methods=['GET'])
def health_check():
    """简单的健康检查端点"""
    if model is not None:
        return jsonify({"status": "healthy", "message": "Model loaded"}), 200
    else:
        return jsonify({"status": "unhealthy", "message": "Model not loaded"}), 500


@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    """
    为指定用户生成推荐。
    请求体应为 JSON 格式，例如: {"user_id": 1}
    """
    global users_df, courses_df, ratings_df, user_item_matrix, model

    if model is None:
        return jsonify({"error": "Model not initialized. Please check server startup."}), 500

    # 1. 获取请求数据
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({"error": "Missing 'user_id' in request body"}), 400

    try:
        user_id = int(data['user_id'])
    except (ValueError, TypeError):
        return jsonify({"error": "'user_id' must be an integer"}), 400

    if user_id not in user_item_matrix.index:
        return jsonify({"error": f"User ID {user_id} not found"}), 404

    # 2. 生成推荐
    recommendations_response = {}
    try:
        # --- 关键修改 3: 确保传入的 user_id 也是 Python int ---
        user_id_int = int(user_id)

        # 用户协同过滤推荐
        user_recs = model.user_based_recommend(user_id_int, n_recommendations=3)
        recommendations_response.update(format_recommendations(user_recs, courses_df, "user_based"))

        # 物品协同过滤推荐
        item_recs = model.item_based_recommend(user_id_int, n_recommendations=3)
        recommendations_response.update(format_recommendations(item_recs, courses_df, "item_based"))

        # 混合推荐
        hybrid_recs = model.hybrid_recommend(user_id_int, n_recommendations=3, user_weight=0.5)
        recommendations_response.update(format_recommendations(hybrid_recs, courses_df, "hybrid"))

        # 可选：添加用户信息
        user_info = users_df[users_df['user_id'] == user_id_int]
        if not user_info.empty:
            # --- 关键修改 4: 用户信息也进行类型转换 ---
            user_profile = {
                "user_id": int(user_id_int), # 确保是 int
                "name": str(user_info.iloc[0]['name']), # 确保是 str
                # 根据你的 users.csv 结构调整字段
                # "age": int(user_info.iloc[0]['age']) if not pd.isna(user_info.iloc[0]['age']) else None,
                # "interests": str(user_info.iloc[0]['interests']) if not pd.isna(user_info.iloc[0]['interests']) else ""
            }
            # 添加更多用户信息字段...
            recommendations_response['user_profile'] = user_profile

        return jsonify(recommendations_response), 200

    except Exception as e:
        # 记录详细的错误日志
        app.logger.error(f"Error generating recommendations for user {user_id}: {e}", exc_info=True)
        return jsonify({"error": f"Internal server error while generating recommendations: {str(e)}"}), 500


def load_model_and_data():
    """
    在应用启动时加载数据和初始化模型。
    """
    global users_df, courses_df, ratings_df, user_item_matrix, model
    print("=== 初始化推荐系统 ===")
    try:
        print("正在加载数据...")
        # --- 关键修改 5: 调用 data_loader_module 的函数 ---
        users_df, courses_df, ratings_df = data_loader_module.load_data()
        print("正在构建用户-课程矩阵...")
        user_item_matrix = data_loader_module.create_user_item_matrix(ratings_df)
        print(f"矩阵维度: {user_item_matrix.shape}")

        print("正在初始化协同过滤模型...")
        model = CollaborativeFiltering(user_item_matrix)

        # 预计算相似度矩阵以提高效率（可选，但推荐）
        print("正在预计算用户相似度矩阵...")
        _ = model.compute_user_similarity()
        print("正在预计算课程相似度矩阵...")
        _ = model.compute_item_similarity()

        print("=== 推荐系统初始化完成 ===")

    except Exception as e:
        print(f"初始化过程中出错: {e}")
        app.logger.error(f"Model initialization failed: {e}", exc_info=True)
        # 可以选择在这里退出应用
        # sys.exit(1)


if __name__ == '__main__':
    # 在 Flask 开始监听请求之前加载模型和数据
    load_model_and_data()
    # 启动 Flask 应用
    # host='0.0.0.0' 允许外部访问 (重要，否则 Postman 可能无法访问)
    # debug=True 有助于开发时看到错误，生产环境应设为 False
    app.run(host='0.0.0.0', port=5000, debug=True)
