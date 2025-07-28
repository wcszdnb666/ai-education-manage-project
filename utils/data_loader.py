import pandas as pd
import os


def load_data():
    """
    加载用户、课程和评分数据
    """
    # 获取当前文件的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_dir)
    data_dir = os.path.join(project_dir, 'data')

    # 加载数据
    users_df = pd.read_csv(os.path.join(data_dir, 'users.csv'))
    courses_df = pd.read_csv(os.path.join(data_dir, 'courses.csv'))
    ratings_df = pd.read_csv(os.path.join(data_dir, 'ratings.csv'))

    return users_df, courses_df, ratings_df


def create_user_item_matrix(ratings_df):
    """
    创建用户-物品评分矩阵
    """
    user_item_matrix = ratings_df.pivot_table(
        index='user_id',
        columns='course_id',
        values='rating'
    ).fillna(0)

    return user_item_matrix


def display_full_matrix(matrix, title, row_labels=None, col_labels=None):
    """
    显示完整的矩阵
    """
    print(f"\n=== {title} ===")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    if row_labels is not None:
        matrix.index = row_labels
    if col_labels is not None:
        matrix.columns = col_labels

    print(matrix.round(3))
    print(f"矩阵形状: {matrix.shape}")


if __name__ == "__main__":
    # 测试数据加载
    users, courses, ratings = load_data()
    print("用户数据:")
    print(users.head())
    print("\n课程数据:")
    print(courses.head())
    print("\n评分数据:")
    print(ratings.head())