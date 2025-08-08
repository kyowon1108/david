import numpy as np
import csv


def read_csv_with_numpy(filename):
    """NumPy를 사용하여 CSV 파일 읽기"""
    try:
        # 헤더를 제외하고 데이터만 읽기
        data = np.loadtxt(filename, delimiter=',', skiprows=1, dtype=str)
        
        # 부품명과 강도 분리
        parts_names = data[:, 0]  # 부품명
        parts_strength = data[:, 1].astype(float)  # 강도 (float 변환)
        
        return parts_names, parts_strength
    
    except FileNotFoundError:
        print(f'파일 {filename}을 찾을 수 없습니다.')
        return None, None
    except Exception as e:
        print(f'파일 {filename} 읽기 중 오류 발생: {e}')
        return None, None


def merge_arrays(arr1, arr2, arr3):
    """세 배열(arr1,2,3)을 병합"""
    try:
        # 세 배열을 세로로 쌓기 (vstack)
        parts = np.vstack((arr1, arr2, arr3))
        print(f'배열 병합 완료: {parts.shape}')
        return parts
    except Exception as e:
        print(f'배열 병합 중 오류 발생: {e}')
        return None


def calculate_item_averages(parts_names, parts_strength):
    """항목별 평균값 계산"""
    try:
        # 고유한 부품명 찾기
        unique_parts = np.unique(parts_names)
        
        averages = {}
        for part in unique_parts:
            # 해당 부품의 모든 강도값 찾기
            mask = parts_names == part
            part_strengths = parts_strength[mask]
            avg_strength = np.mean(part_strengths)
            averages[part] = avg_strength
        
        print(f'{len(averages)}개의 고유 부품에 대한 평균 계산 완료')
        return averages
    except Exception as e:
        print(f'평균 계산 중 오류 발생: {e}')
        return {}


def filter_low_strength(averages, threshold=50):
    """평균값이 threshold보다 작은 항목만 필터링하는 함수"""
    try:
        filtered_items = {part: avg for part, avg in averages.items() if avg < threshold}
        print(f'평균 강도가 {threshold}보다 작은 부품: {len(filtered_items)}개')
        return filtered_items
    except Exception as e:
        print(f'필터링 중 오류 발생: {e}')
        return {}


def save_filtered_data(filtered_data, filename):
    """필터링된 데이터를 CSV 파일로 저장"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # 헤더 쓰기
            writer.writerow(['parts', 'average_strength'])
            
            # 데이터 쓰기
            for part, avg_strength in filtered_data.items():
                writer.writerow([part, f'{avg_strength:.2f}'])
        
        print(f'{filename} 파일에 저장 완료')
        return True
    except Exception as e:
        print(f'파일 저장 중 오류 발생: {e}')
        return False


def read_filtered_csv(filename):
    """저장된 필터링 데이터를 다시 읽고 part2로 저장 (보너스 과제)"""
    try:
        parts2_names, parts2_strength = read_csv_with_numpy(filename)
        if parts2_names is not None and parts2_strength is not None:
            # 2차원 배열로 만들기
            parts2 = np.column_stack((parts2_names, parts2_strength))
            print(f'parts2 배열 생성: {parts2.shape} 형태')
            return parts2
        return None
    except Exception as e:
        print(f'필터링된 파일 읽기 중 오류 발생: {e}')
        return None


def calculate_transpose(parts2):
    """전치 행렬 계산 (보너스 과제)"""
    try:
        parts3 = parts2.T  # 전치 행렬
        print(f'전치 행렬 parts3 생성: {parts3.shape} 형태')
        return parts3
    except Exception as e:
        print(f'전치 행렬 계산 중 오류 발생: {e}')
        return None


def display_array_info(array, name):
    """배열 정보를 출력하는 함수"""
    print(f'\n=== {name} 배열 정보 ===')
    print(f'형태: {array.shape}')
    print(f'데이터 타입: {array.dtype}')
    print(f'처음 5개 항목:')
    if len(array.shape) == 1:
        print(array[:5])
    else:
        print(array[:5])


def main():
    
    # 1. 세 개의 CSV 파일을 NumPy로 읽기
    files = [
        'mars_base/mars_base_main_parts-001.csv',
        'mars_base/mars_base_main_parts-002.csv',
        'mars_base/mars_base_main_parts-003.csv'
    ]
    
    all_parts_names = []
    all_parts_strength = []
    arrays = []
    
    for i, filename in enumerate(files, 1):
        parts_names, parts_strength = read_csv_with_numpy(filename)
        if parts_names is not None and parts_strength is not None:
            all_parts_names.extend(parts_names)
            all_parts_strength.extend(parts_strength)
            
            # 개별 배열 생성 (arr1, arr2, arr3)
            arr = np.column_stack((parts_names, parts_strength))
            arrays.append(arr)
            
            print(f'arr{i} 생성: {arr.shape}')
    
    if len(arrays) != 3: # 무조건 3개 읽어야 진행할 수 있게 처리함 (에러방지)
        print('읽은 file length가 3이 아닙니다. 프로그램을 종료합니다.')
        return
    
    arr1, arr2, arr3 = arrays
    
    # 2. 세 배열을 병합하여 parts ndarray 생성
    parts = merge_arrays(arr1, arr2, arr3)
    if parts is None:
        print('배열 병합에 실패했습니다.') # 배열 병합 에러시 예외 처리
        return
    
    display_array_info(parts, 'parts (병합된 배열)')
    
    # NumPy 배열에서 부품명과 강도 분리
    parts_names_all = parts[:, 0]
    parts_strength_all = parts[:, 1].astype(float) # astype로 csv 불러온 문자열 한꺼번에 float로 변환해버림
    
    # 3. 항목별 평균값 계산
    print('\n=== 항목별 평균값 계산 ===')
    averages = calculate_item_averages(parts_names_all, parts_strength_all)
    
    # 평균값 출력 (처음 10개만)
    sorted_averages = sorted(averages.items(), key=lambda x: x[1])
    print('\n평균 강도가 낮은 순서대로 처음 10개:')
    for i, (part, avg) in enumerate(sorted_averages[:10], 1):
        print(f'{i:2d}. {part}: {avg:.2f}')
    
    # 4. 평균값이 50보다 작은 항목만 필터링
    print('\n=== 평균 강도 50 미만 필터링 ===')
    filtered_items = filter_low_strength(averages, 50)
    
    print('필터링된 부품들:')
    for part, avg in sorted(filtered_items.items(), key=lambda x: x[1]):
        print(f'{part}: {avg:.2f}')
    
    # 5. 필터링된 데이터를 CSV로 저장 (예외 처리 포함)
    save_success = save_filtered_data(filtered_items, 'parts_to_work_on.csv')
    
    if not save_success:
        print('파일 저장에 실패했습니다.')
        return
    
    # 보너스 과제: parts_to_work_on.csv를 다시 읽어서 parts2로 저장
    print('\n=== 보너스 과제: parts_to_work_on.csv 재읽기 ===')
    parts2 = read_filtered_csv('parts_to_work_on.csv')
    
    if parts2 is not None:
        display_array_info(parts2, 'parts2 (재읽기)')
        
        # 보너스 과제: 전치 행렬 계산
        print('\n=== 보너스 과제: 전치 행렬 계산 ===')
        parts3 = calculate_transpose(parts2)
        
        if parts3 is not None:
            display_array_info(parts3, 'parts3 (전치 행렬)')
            
            print('\nparts3 전치 행렬의 내용:')
            print('첫 번째 행 (부품명들):')
            print(parts3[0][:10] if len(parts3[0]) > 10 else parts3[0])
            print('두 번째 행 (평균 강도들):')
            print(parts3[1][:10] if len(parts3[1]) > 10 else parts3[1])


if __name__ == '__main__':
    main()
