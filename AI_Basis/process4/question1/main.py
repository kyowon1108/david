import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
import platform

# 한글 폰트 설정
if platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.family'] = 'AppleGothic'
elif platform.system() == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'
else:  # Linux
    plt.rcParams['font.family'] = 'DejaVu Sans'

plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지


def calculate_correlation_with_transported(df):
    """
    Transported 항목과 각 항목의 상관관계 계산
    
    Args:
        df (pandas.DataFrame): 분석할 데이터프레임
        
    Returns:
        dict: 각 항목과 Transported의 상관관계
    """
    # Transported가 있는 데이터만 사용
    df_with_transported = df[df['Transported'].notna()].copy()
    
    # Transported를 boolean으로 변환
    df_with_transported['Transported'] = (
        df_with_transported['Transported'].astype(str).str.lower() == 'true'
    ).astype(int)
    
    correlations = {}
    
    # 수치형 컬럼들에 대해 상관관계 계산
    numeric_columns = ['Age', 'RoomService', 'FoodCourt', 'ShoppingMall', 'Spa', 'VRDeck']
    for col in numeric_columns:
        if col in df_with_transported.columns:
            df_col = pd.to_numeric(df_with_transported[col], errors='coerce')
            if df_col.notna().sum() > 0:
                corr = df_col.corr(df_with_transported['Transported'])
                if pd.notna(corr):
                    correlations[col] = abs(corr)
    
    # 범주형 변수들에 대해 카이제곱 통계량이나 다른 방법 사용
    # 간단하게 각 범주의 Transported 비율 차이를 측정
    categorical_columns = ['HomePlanet', 'CryoSleep', 'Destination', 'VIP']
    for col in categorical_columns:
        if col in df_with_transported.columns:
            # 각 범주의 Transported 비율 계산
            group_stats = df_with_transported.groupby(col)['Transported'].mean()
            # 비율의 분산을 상관성 지표로 사용
            if len(group_stats) > 1:
                variance = group_stats.var()
                correlations[col] = variance
    
    return correlations


def get_age_group(age):
    """
    나이를 연령대 그룹으로 분류
    
    Args:
        age: 나이 (문자열 또는 숫자)
        
    Returns:
        str: 연령대 그룹 ('10대', '20대', '30대', '40대', '50대', '60대', '70대', '기타')
    """
    try:
        age_float = float(age)
        if pd.isna(age_float):
            return '기타'
        
        if 10 <= age_float < 20:
            return '10대'
        elif 20 <= age_float < 30:
            return '20대'
        elif 30 <= age_float < 40:
            return '30대'
        elif 40 <= age_float < 50:
            return '40대'
        elif 50 <= age_float < 60:
            return '50대'
        elif 60 <= age_float < 70:
            return '60대'
        elif 70 <= age_float < 80:
            return '70대'
        else:
            return '기타'
    except (ValueError, TypeError):
        return '기타'


def visualize_transported_by_age(df):
    """
    연령대별 Transported 여부를 시각화
    
    Args:
        df (pandas.DataFrame): 분석할 데이터프레임
    """
    # Transported가 있는 데이터만 사용
    df_with_transported = df[df['Transported'].notna()].copy()
    
    # Transported를 boolean으로 변환
    df_with_transported['Transported'] = (
        df_with_transported['Transported'].astype(str).str.lower() == 'true'
    )
    
    # 나이 그룹 추가
    df_with_transported['AgeGroup'] = (
        df_with_transported['Age'].apply(get_age_group)
    )
    
    # 연령대별 Transported 비율 계산
    age_groups = ['10대', '20대', '30대', '40대', '50대', '60대', '70대']
    transported_rates = []
    total_counts = []
    
    for age_group in age_groups:
        group_data = df_with_transported[df_with_transported['AgeGroup'] == age_group]
        if len(group_data) > 0:
            transported_rate = group_data['Transported'].mean() * 100
            transported_rates.append(transported_rate)
            total_counts.append(len(group_data))
        else:
            transported_rates.append(0)
            total_counts.append(0)
    
    # 그래프 그리기
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 첫 번째 그래프: Transported 비율
    ax1.bar(age_groups, transported_rates, color='steelblue')
    ax1.set_xlabel('연령대')
    ax1.set_ylabel('Transported 비율 (%)')
    ax1.set_title('연령대별 Transported 비율')
    ax1.set_ylim(0, 100)
    ax1.grid(axis='y', alpha=0.3)
    
    # 두 번째 그래프: 각 연령대별 Transported 여부 분포
    transported_by_age = []
    not_transported_by_age = []
    
    for age_group in age_groups:
        group_data = df_with_transported[df_with_transported['AgeGroup'] == age_group]
        if len(group_data) > 0:
            transported_count = group_data['Transported'].sum()
            not_transported_count = len(group_data) - transported_count
            transported_by_age.append(transported_count)
            not_transported_by_age.append(not_transported_count)
        else:
            transported_by_age.append(0)
            not_transported_by_age.append(0)
    
    x = range(len(age_groups))
    width = 0.35
    
    ax2.bar([i - width/2 for i in x], transported_by_age, width,
            label='Transported', color='green', alpha=0.7)
    ax2.bar([i + width/2 for i in x], not_transported_by_age, width,
            label='Not Transported', color='red', alpha=0.7)
    ax2.set_xlabel('연령대')
    ax2.set_ylabel('인원 수')
    ax2.set_title('연령대별 Transported 여부 분포')
    ax2.set_xticks(x)
    ax2.set_xticklabels(age_groups)
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('transported_by_age.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print('연령대별 Transported 분석 그래프 저장 완료')


def visualize_age_by_destination(df):
    """
    Destination별 연령대 분포 시각화
    
    Args:
        df (pandas.DataFrame): 분석할 데이터프레임
    """
    # 나이 그룹 추가
    df['AgeGroup'] = df['Age'].apply(get_age_group)
    
    # Destination별 연령대 분포 계산
    destination_age_dist = {}
    
    for destination in df['Destination'].dropna().unique():
        dest_data = df[df['Destination'] == destination]
        age_groups = ['10대', '20대', '30대', '40대', '50대', '60대', '70대']
        age_counts = []
        
        for age_group in age_groups:
            count = len(dest_data[dest_data['AgeGroup'] == age_group])
            age_counts.append(count)
        
        destination_age_dist[destination] = age_counts
    
    # 그래프 그리기
    fig, axes = plt.subplots(len(destination_age_dist), 1,
                             figsize=(12, 4 * len(destination_age_dist)))
    
    if len(destination_age_dist) == 1:
        axes = [axes]
    
    age_groups = ['10대', '20대', '30대', '40대', '50대', '60대', '70대']
    
    for idx, (destination, age_counts) in enumerate(destination_age_dist.items()):
        ax = axes[idx]
        ax.bar(age_groups, age_counts, color='skyblue', alpha=0.7)
        ax.set_xlabel('연령대')
        ax.set_ylabel('인원 수')
        ax.set_title(f'Destination: {destination} - 연령대별 분포')
        ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('age_by_destination.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print('Destination별 연령대 분포 그래프 저장 완료')


def main():

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'spaceship-titanic')
    
    train_file = os.path.join(data_dir, 'train.csv')
    test_file = os.path.join(data_dir, 'test.csv')
    
    # CSV 파일 읽기
    print('CSV 파일 읽는 중...')
    train_data = []
    with open(train_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            train_data.append(row)
    
    test_data = []
    with open(test_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            test_data.append(row)
    
    print(f'Train 데이터 개수: {len(train_data)}')
    print(f'Test 데이터 개수: {len(test_data)}')
    
    # 데이터 병합 (test 데이터에는 Transported 컬럼이 없으므로 None으로 채움)
    print('\n데이터 병합 중...')
    merged_data = train_data.copy()
    for row in test_data:
        row_copy = row.copy()
        row_copy['Transported'] = None
        merged_data.append(row_copy)
    
    print(f'병합된 전체 데이터 개수: {len(merged_data)}')
    
    # DataFrame으로 변환
    df = pd.DataFrame(merged_data)
    
    # Transported와 가장 관련성이 높은 항목 찾기
    print('\nTransported와의 관련성 분석 중...')
    correlations = calculate_correlation_with_transported(df)
    
    if correlations:
        sorted_correlations = sorted(correlations.items(),
                                     key=lambda x: x[1], reverse=True)
        print('\nTransported와 가장 관련성이 높은 항목들:')
        for col, corr_value in sorted_correlations:
            print(f'  {col}: {corr_value:.4f}')
        
        max_corr_col = sorted_correlations[0][0]
        print(f'\n가장 관련성이 높은 항목: {max_corr_col}')
    
    # 연령대별 Transported 여부 시각화
    print('\n연령대별 Transported 여부 시각화 중...')
    visualize_transported_by_age(df)
    
    # 보너스: Destination별 연령대 분포 시각화
    print('\nDestination별 연령대 분포 시각화 중...')
    visualize_age_by_destination(df)
    
    print('\n모든 분석이 완료되었습니다!')


if __name__ == '__main__':
    main()

