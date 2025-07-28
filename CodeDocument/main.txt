import pandas as pd
import numpy as np
from utils.data_loader import load_data, create_user_item_matrix, display_full_matrix
from models.collaborative_filtering import CollaborativeFiltering


def display_recommendations(recommendations, courses_df, method_name):
    """
    显示推荐结果
    """
    print(f"\n=== {method_name} 推荐结果 ===")
    if not recommendations:
        print("没有找到推荐内容")
        return

    for i, (course_id, score) in enumerate(recommendations, 1):
        course_info = courses_df[courses_df['course_id'] == course_id]
        if not course_info.empty:
            title = course_info.iloc[0]['title']
            category = course_info.iloc[0]['category']
            difficulty = course_info.iloc[0]['difficulty']
            print(f"{i}. {title}")
            print(f"   类别: {category} | 难度: {difficulty} | 推荐分数: {score:.3f}")
        else:
            print(f"{i}. 课程ID: {course_id} | 推荐分数: {score:.3f}")


def display_user_profile(user_id, users_df, ratings_df, courses_df):
    """
    显示用户学习档案
    """
    user_info = users_df[users_df['user_id'] == user_id]
    if not user_info.empty:
        name = user_info.iloc[0]['name']
        age = user_info.iloc[0]['age']
        interests = user_info.iloc[0]['interests']
        print(f"\n--- 用户档案: {name} (ID: {user_id}) ---")
        print(f"年龄: {age}")
        print(f"兴趣: {interests}")

    # 显示用户已学习的课程
    user_ratings = ratings_df[ratings_df['user_id'] == user_id]
    print(f"已学习课程数量: {len(user_ratings)}")

    for _, rating in user_ratings.iterrows():
        course_info = courses_df[courses_df['course_id'] == rating['course_id']]
        if not course_info.empty:
            title = course_info.iloc[0]['title']
            print(f"  • {title} (评分: {rating['rating']}/5)")


def main():
    print("=== 学习内容推荐系统 ===")
    print("=" * 50)

    # 1. 加载数据
    print("正在加载数据...")
    users_df, courses_df, ratings_df = load_data()

    # 2. 创建用户-物品矩阵
    print("正在构建用户-课程矩阵...")
    user_item_matrix = create_user_item_matrix(ratings_df)
    print(f"矩阵维度: {user_item_matrix.shape}")

    # 显示完整的用户-课程评分矩阵
    print("\n=== 用户-课程评分矩阵 ===")
    print("行: 用户ID | 列: 课程ID | 值: 评分(0表示未评分)")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    print(user_item_matrix.round(1))

    # 3. 初始化推荐模型
    print("\n正在初始化协同过滤模型...")
    model = CollaborativeFiltering(user_item_matrix)

    # 4. 计算并显示完整的相似度矩阵
    print("\n正在计算相似度矩阵...")

    # 计算用户相似度矩阵
    user_similarity = model.compute_user_similarity()
    print("\n" + "=" * 60)
    print("用户相似度矩阵 (完整)")
    print("=" * 60)
    print("行和列: 用户ID | 值: 相似度 (0-1, 1表示完全相似)")
    print(user_similarity.round(4))

    # 计算课程相似度矩阵
    item_similarity = model.compute_item_similarity()
    print("\n" + "=" * 60)
    print("课程相似度矩阵 (完整)")
    print("=" * 60)
    print("行和列: 课程ID | 值: 相似度 (0-1, 1表示完全相似)")
    print(item_similarity.round(4))

    # 5. 为每个用户生成推荐
    print("\n" + "=" * 60)
    print("个性化推荐结果")
    print("=" * 60)

    for user_id in sorted(user_item_matrix.index):
        # 显示用户档案
        display_user_profile(user_id, users_df, ratings_df, courses_df)

        print(f"\n--- 为用户ID {user_id} 生成的推荐 ---")

        # 生成不同类型的推荐
        try:
            # 用户协同过滤推荐
            user_recs = model.user_based_recommend(user_id, n_recommendations=3)
            display_recommendations(user_recs, courses_df, "【用户协同过滤】")

            # 物品协同过滤推荐
            item_recs = model.item_based_recommend(user_id, n_recommendations=3)
            display_recommendations(item_recs, courses_df, "【物品协同过滤】")

            # 混合推荐
            hybrid_recs = model.hybrid_recommend(user_id, n_recommendations=3, user_weight=0.5)
            display_recommendations(hybrid_recs, courses_df, "【混合推荐】")

        except Exception as e:
            print(f"生成推荐时出错: {e}")

        print("-" * 50)

    # 6. 显示统计信息
    print("\n" + "=" * 60)
    print("系统统计信息")
    print("=" * 60)
    print(f"总用户数: {len(users_df)}")
    print(f"总课程数: {len(courses_df)}")
    print(f"总评分记录数: {len(ratings_df)}")
    print(f"评分密度: {len(ratings_df) / (len(users_df) * len(courses_df)) * 100:.1f}%")

    # 显示评分分布
    print(f"\n评分分布:")
    rating_counts = ratings_df['rating'].value_counts().sort_index()
    for rating, count in rating_counts.items():
        print(f"  {rating}分: {count}次 ({count / len(ratings_df) * 100:.1f}%)")

    print("\n" + "=" * 60)
    print("推荐系统运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()