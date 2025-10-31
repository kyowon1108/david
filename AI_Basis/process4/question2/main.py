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


def read_population_data(file_path):
    """
    인구 데이터 CSV 파일을 읽어서 DataFrame으로 변환
    
    Args:
        file_path (str): CSV 파일 경로
        
    Returns:
        pandas.DataFrame: 읽은 데이터
    """
    df = pd.read_csv(file_path, encoding='utf-8')
    return df


def filter_general_household_member(df):
    """
    일반가구원 컬럼만 남기고 나머지 컬럼 삭제
    
    Args:
        df (pandas.DataFrame): 원본 데이터
        
    Returns:
        pandas.DataFrame: 일반가구원 컬럼만 남은 데이터
    """
    # 필요한 컬럼만 선택 (시점, 성별, 연령별, 일반가구원)
    required_columns = ['시점', '성별', '연령별', '일반가구원']
    filtered_df = df[required_columns].copy()
    return filtered_df


def get_year_by_gender_stats(df):
    """
    2015년 이후 남자 및 여자의 연도별 일반가구원 데이터 통계
    
    Args:
        df (pandas.DataFrame): 필터링된 데이터
        
    Returns:
        pandas.DataFrame: 연도별 성별 통계
    """
    # 2015년 이후 데이터만 선택
    df_filtered = df[df['시점'] >= 2015].copy()
    
    # 합계와 연령별 합계 제외하고 남자, 여자만 선택
    df_gender = df_filtered[
        (df_filtered['성별'].isin(['남자', '여자'])) &
        (df_filtered['연령별'] == '합계')
    ].copy()
    
    # 일반가구원을 숫자로 변환 (X나 결측치 처리)
    df_gender['일반가구원'] = pd.to_numeric(
        df_gender['일반가구원'], errors='coerce'
    )
    
    # 연도별, 성별로 그룹화하여 집계
    result = df_gender.pivot_table(
        values='일반가구원',
        index='시점',
        columns='성별',
        aggfunc='sum'
    )
    
    return result


def get_age_stats(df):
    """
    2015년 이후 연령별 일반가구원 데이터 통계
    
    Args:
        df (pandas.DataFrame): 필터링된 데이터
        
    Returns:
        pandas.DataFrame: 연령별 통계
    """
    # 2015년 이후 데이터만 선택
    df_filtered = df[df['시점'] >= 2015].copy()
    
    # 성별이 '계'이고 연령별이 합계가 아닌 것만 선택
    # 연령별 합계(15~64세, 65세이상)는 제외
    exclude_ages = ['합계', '15~64세', '65세이상']
    df_age = df_filtered[
        (df_filtered['성별'] == '계') &
        (~df_filtered['연령별'].isin(exclude_ages))
    ].copy()
    
    # 일반가구원을 숫자로 변환
    df_age['일반가구원'] = pd.to_numeric(
        df_age['일반가구원'], errors='coerce'
    )
    
    # 연도별, 연령별로 그룹화하여 집계
    result = df_age.pivot_table(
        values='일반가구원',
        index='시점',
        columns='연령별',
        aggfunc='sum'
    )
    
    return result


def get_age_by_gender_stats(df):
    """
    2015년 이후 남자 및 여자의 연령별 일반가구원 데이터
    
    Args:
        df (pandas.DataFrame): 필터링된 데이터
        
    Returns:
        dict: {'남자': DataFrame, '여자': DataFrame}
    """
    # 2015년 이후 데이터만 선택
    df_filtered = df[df['시점'] >= 2015].copy()
    
    # 연령별 합계는 제외
    exclude_ages = ['합계', '15~64세', '65세이상']
    df_age_gender = df_filtered[
        (df_filtered['성별'].isin(['남자', '여자'])) &
        (~df_filtered['연령별'].isin(exclude_ages))
    ].copy()
    
    # 일반가구원을 숫자로 변환
    df_age_gender['일반가구원'] = pd.to_numeric(
        df_age_gender['일반가구원'], errors='coerce'
    )
    
    result = {}
    for gender in ['남자', '여자']:
        df_gender = df_age_gender[df_age_gender['성별'] == gender].copy()
        
        # 연도별, 연령별로 피벗
        pivot_table = df_gender.pivot_table(
            values='일반가구원',
            index='시점',
            columns='연령별',
            aggfunc='sum'
        )
        
        result[gender] = pivot_table
    
    return result


def visualize_age_by_gender(df):
    """
    2015년 이후 남자 및 여자의 연령별 일반가구원 데이터를 꺽은선 그래프로 표현
    
    Args:
        df (pandas.DataFrame): 필터링된 데이터
    """
    age_by_gender = get_age_by_gender_stats(df)
    
    # 연령대 목록 (정렬된 순서)
    age_order = [
        '15세미만', '15~19세', '20~24세', '25~29세', '30~34세',
        '35~39세', '40~44세', '45~49세', '50~54세', '55~59세',
        '60~64세', '65~69세', '70~74세', '75~79세', '80~84세', '85세이상'
    ]
    
    # 존재하는 연령대만 필터링
    available_ages = []
    for age in age_order:
        if age in age_by_gender['남자'].columns:
            available_ages.append(age)
    
    # 그래프 생성
    fig, axes = plt.subplots(2, 1, figsize=(14, 12))
    
    for idx, gender in enumerate(['남자', '여자']):
        ax = axes[idx]
        df_gender = age_by_gender[gender]
        
        # 각 연령대별로 꺽은선 그래프 그리기
        for age in available_ages:
            if age in df_gender.columns:
                ax.plot(
                    df_gender.index,
                    df_gender[age],
                    marker='o',
                    label=age,
                    linewidth=1.5,
                    markersize=4
                )
        
        ax.set_xlabel('연도', fontsize=12)
        ax.set_ylabel('일반가구원 수', fontsize=12)
        ax.set_title(f'{gender} 연령별 일반가구원 변화 추이 (2015-2024)', fontsize=14)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_xticks(df_gender.index)
    
    plt.tight_layout()
    plt.savefig('age_by_gender_trend.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print('연령별 성별 그래프 저장 완료')


def generate_trend_report(df):
    """
    연령별 그래프 변화를 보고 인구 변화 트렌드를 데이터 기반으로 정리한 리포터 작성
    
    Args:
        df (pandas.DataFrame): 필터링된 데이터
    """
    age_by_gender = get_age_by_gender_stats(df)
    year_stats = get_year_by_gender_stats(df)
    age_stats = get_age_stats(df)
    
    report_lines = []
    report_lines.append('=' * 60)
    report_lines.append('인구 변화 트렌드 분석 리포터')
    report_lines.append('=' * 60)
    report_lines.append('')
    report_lines.append(f'분석 기간: 2015년 ~ 2024년 (10년)')
    report_lines.append('')
    
    # 전체 인구 변화
    report_lines.append('1. 전체 인구 변화')
    report_lines.append('-' * 60)
    total_2015_df = df[
        (df['시점'] == 2015) &
        (df['성별'] == '계') &
        (df['연령별'] == '합계')
    ]
    total_2024_df = df[
        (df['시점'] == 2024) &
        (df['성별'] == '계') &
        (df['연령별'] == '합계')
    ]
    
    if len(total_2015_df) > 0 and len(total_2024_df) > 0:
        total_2015_val = pd.to_numeric(
            total_2015_df['일반가구원'].iloc[0], errors='coerce'
        )
        total_2024_val = pd.to_numeric(
            total_2024_df['일반가구원'].iloc[0], errors='coerce'
        )
        if pd.notna(total_2015_val) and pd.notna(total_2024_val):
            change = total_2024_val - total_2015_val
            change_pct = (change / total_2015_val) * 100
            report_lines.append(f'  2015년: {total_2015_val:,.0f}명')
            report_lines.append(f'  2024년: {total_2024_val:,.0f}명')
            report_lines.append(f'  변화량: {change:+,.0f}명 ({change_pct:+.2f}%)')
    report_lines.append('')
    
    # 성별 인구 변화
    report_lines.append('2. 성별 인구 변화')
    report_lines.append('-' * 60)
    for gender in ['남자', '여자']:
        if gender in year_stats.columns:
            values = year_stats[gender].dropna()
            if len(values) >= 2:
                first_val = values.iloc[0]
                last_val = values.iloc[-1]
                change = last_val - first_val
                change_pct = (change / first_val) * 100
                report_lines.append(
                    f'  {gender}: {first_val:,.0f}명 → {last_val:,.0f}명 '
                    f'({change:+,.0f}명, {change_pct:+.2f}%)'
                )
    report_lines.append('')
    
    # 연령대별 주요 변화
    report_lines.append('3. 연령대별 주요 변화 (2015 vs 2024)')
    report_lines.append('-' * 60)
    
    age_order = [
        '15세미만', '15~19세', '20~24세', '25~29세', '30~34세',
        '35~39세', '40~44세', '45~49세', '50~54세', '55~59세',
        '60~64세', '65~69세', '70~74세', '75~79세', '80~84세', '85세이상'
    ]
    
    for age in age_order:
        if age in age_stats.columns:
            values = age_stats[age].dropna()
            if len(values) >= 2:
                first_val = values.iloc[0]
                last_val = values.iloc[-1]
                change = last_val - first_val
                change_pct = (change / first_val) * 100 if first_val != 0 else 0
                report_lines.append(
                    f'  {age:10s}: {first_val:>10,.0f} → {last_val:>10,.0f} '
                    f'({change:>+10,.0f}, {change_pct:>+6.2f}%)'
                )
    report_lines.append('')
    
    # 주요 트렌드 요약
    report_lines.append('4. 주요 트렌드 요약')
    report_lines.append('-' * 60)
    
    # 고령화 추세 확인
    old_ages = ['65~69세', '70~74세', '75~79세', '80~84세', '85세이상']
    young_ages = ['15세미만', '15~19세', '20~24세']
    
    old_change = 0
    young_change = 0
    
    for age in old_ages:
        if age in age_stats.columns:
            values = age_stats[age].dropna()
            if len(values) >= 2:
                old_change += (values.iloc[-1] - values.iloc[0])
    
    for age in young_ages:
        if age in age_stats.columns:
            values = age_stats[age].dropna()
            if len(values) >= 2:
                young_change += (values.iloc[-1] - values.iloc[0])
    
    if old_change > 0:
        report_lines.append(
            f'  - 고령 인구(65세 이상) 증가 추세: +{old_change:,.0f}명'
        )
    if young_change < 0:
        report_lines.append(
            f'  - 청년 인구(24세 이하) 감소 추세: {young_change:,.0f}명'
        )
    if old_change > 0 and young_change < 0:
        report_lines.append('  - 인구 고령화 현상이 뚜렷하게 나타남')
    
    report_lines.append('')
    report_lines.append('=' * 60)
    
    # 리포터 파일 저장
    report_text = '\n'.join(report_lines)
    with open('population_trend_report.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print('인구 변화 트렌드 리포터 저장 완료')
    print('\n' + report_text)


def main():
    """
    메인 함수: 인구 데이터 분석 및 시각화 수행
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(script_dir, 'polulation.csv')
    
    # CSV 파일 읽기
    print('CSV 파일 읽는 중...')
    df = read_population_data(csv_file)
    print(f'원본 데이터: {len(df)}행')
    
    # 일반가구원 컬럼만 남기고 나머지 삭제
    print('\n일반가구원 컬럼만 필터링 중...')
    df_filtered = filter_general_household_member(df)
    print(f'필터링 후 데이터: {len(df_filtered)}행')
    
    # 2015년 이후 남자 및 여자의 연도별 일반가구원 데이터 통계 출력
    print('\n=== 남자 및 여자의 연도별 일반가구원 데이터 통계 ===')
    year_by_gender = get_year_by_gender_stats(df_filtered)
    print(year_by_gender)
    print()
    
    # 2015년 이후 연령별 일반가구원 데이터 통계 출력
    print('=== 연령별 일반가구원 데이터 통계 ===')
    age_stats = get_age_stats(df_filtered)
    print(age_stats)
    print()
    
    # 2015년 이후 남자 및 여자의 연령별 일반가구원 데이터 꺽은선 그래프
    print('연령별 성별 그래프 생성 중...')
    visualize_age_by_gender(df_filtered)
    
    # 보너스: 인구 변화 트렌드 리포터 작성
    print('\n인구 변화 트렌드 리포터 생성 중...')
    generate_trend_report(df_filtered)
    
    print('\n모든 분석이 완료되었습니다!')


if __name__ == '__main__':
    main()

