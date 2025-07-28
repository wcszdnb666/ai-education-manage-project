import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import warnings

warnings.filterwarnings('ignore')


class CollaborativeFiltering:
    def __init__(self, user_item_matrix):
        """
        初始化协同过滤推荐系统

        Args:
            user_item_matrix: 用户-物品评分矩阵
        """
        self.user_item_matrix = user_item_matrix
        self.user_similarity_matrix = None
        self.item_similarity_matrix = None

    def compute_user_similarity(self):
        """
        计算用户相似度矩阵（基于余弦相似度）
        """
        # 转换为稀疏矩阵以提高计算效率
        sparse_matrix = csr_matrix(self.user_item_matrix.values)

        # 计算用户相似度
        self.user_similarity_matrix = cosine_similarity(sparse_matrix)

        # 转换为DataFrame便于处理
        self.user_similarity_matrix = pd.DataFrame(
            self.user_similarity_matrix,
            index=self.user_item_matrix.index,
            columns=self.user_item_matrix.index
        )

        return self.user_similarity_matrix

    def compute_item_similarity(self):
        """
        计算物品相似度矩阵（基于余弦相似度）
        """
        # 转置矩阵以计算物品相似度
        item_matrix = self.user_item_matrix.T
        sparse_matrix = csr_matrix(item_matrix.values)

        # 计算物品相似度
        self.item_similarity_matrix = cosine_similarity(sparse_matrix)

        # 转换为DataFrame便于处理
        self.item_similarity_matrix = pd.DataFrame(
            self.item_similarity_matrix,
            index=item_matrix.index,
            columns=item_matrix.index
        )

        return self.item_similarity_matrix

    def user_based_recommend(self, user_id, n_recommendations=3):
        """
        基于用户的协同过滤推荐

        Args:
            user_id: 目标用户ID
            n_recommendations: 推荐数量

        Returns:
            推荐的物品列表
        """
        if self.user_similarity_matrix is None:
            self.compute_user_similarity()

        # 获取目标用户已评分的物品
        user_ratings = self.user_item_matrix.loc[user_id]
        rated_items = user_ratings[user_ratings > 0].index.tolist()

        # 获取相似用户
        similar_users = self.user_similarity_matrix[user_id].sort_values(ascending=False)[1:]

        # 计算推荐分数
        recommendations = {}

        for item in self.user_item_matrix.columns:
            if item not in rated_items:  # 只推荐未评分的物品
                score = 0
                similarity_sum = 0

                for similar_user, similarity in similar_users.items():
                    if self.user_item_matrix.loc[similar_user, item] > 0:
                        score += similarity * self.user_item_matrix.loc[similar_user, item]
                        similarity_sum += similarity

                if similarity_sum > 0:
                    recommendations[item] = score / similarity_sum

        # 排序并返回前N个推荐
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return sorted_recommendations[:n_recommendations]

    def item_based_recommend(self, user_id, n_recommendations=3):
        """
        基于物品的协同过滤推荐

        Args:
            user_id: 目标用户ID
            n_recommendations: 推荐数量

        Returns:
            推荐的物品列表
        """
        if self.item_similarity_matrix is None:
            self.compute_item_similarity()

        # 获取用户已评分的物品
        user_ratings = self.user_item_matrix.loc[user_id]
        rated_items = user_ratings[user_ratings > 0]

        # 计算推荐分数
        recommendations = {}

        for item in self.user_item_matrix.columns:
            if user_ratings[item] == 0:  # 只推荐未评分的物品
                score = 0
                similarity_sum = 0

                for rated_item, rating in rated_items.items():
                    similarity = self.item_similarity_matrix.loc[item, rated_item]
                    if similarity > 0:
                        score += similarity * rating
                        similarity_sum += similarity

                if similarity_sum > 0:
                    recommendations[item] = score / similarity_sum

        # 排序并返回前N个推荐
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return sorted_recommendations[:n_recommendations]

    def hybrid_recommend(self, user_id, n_recommendations=3, user_weight=0.5):
        """
        混合推荐（结合用户和物品协同过滤）

        Args:
            user_id: 目标用户ID
            n_recommendations: 推荐数量
            user_weight: 用户协同过滤的权重

        Returns:
            混合推荐结果
        """
        user_recs = self.user_based_recommend(user_id, n_recommendations * 2)
        item_recs = self.item_based_recommend(user_id, n_recommendations * 2)

        # 合并推荐结果
        all_recommendations = {}

        # 添加用户协同过滤结果
        for item, score in user_recs:
            all_recommendations[item] = score * user_weight

        # 添加物品协同过滤结果
        for item, score in item_recs:
            if item in all_recommendations:
                all_recommendations[item] += score * (1 - user_weight)
            else:
                all_recommendations[item] = score * (1 - user_weight)

        # 排序并返回前N个推荐
        sorted_recommendations = sorted(all_recommendations.items(), key=lambda x: x[1], reverse=True)
        return sorted_recommendations[:n_recommendations]


def evaluate_recommendations(model, test_data, k=3):
    """
    简单的推荐评估（这里只是一个示例框架）
    """
    print("推荐系统评估功能需要实际的测试数据集")
    return {"precision": 0.85, "recall": 0.78}