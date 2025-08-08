import csv
import pickle


def print_csv_content(filename):
    """CSV 파일 내용을 그냥 읽어서 화면에 출력"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            print(f'\n=== {filename} 파일 내용 ===')
            content = file.read()
            print(content)
            print('=' * 50)
    except FileNotFoundError:
        print(f'파일 {filename}을 찾을 수 없습니다.')
    except Exception as e:
        print(f'파일 읽기 중 오류 발생: {e}')


def read_csv_to_list(filename):
    """CSV 파일을 읽어서 리스트로 변환"""
    inventory_list = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            
            for row in csv_reader:
                  try:
                      # 인화성 지수를 float으로 변환
                      flammability = float(row[4])
                      inventory_item = {
                          'substance': row[0],
                          'weight': row[1],
                          'specific_gravity': row[2],
                          'strength': row[3],
                          'flammability': flammability
                      }
                      inventory_list.append(inventory_item)
                  except ValueError:
                    continue # 숫자가 아닌 경우 건너뛰기
    except FileNotFoundError:
        print(f'파일 {filename}을 찾을 수 없습니다.')
        return []
    except Exception as e:
        print(f'파일 읽기 중 오류 발생: {e}')
        return []
    
    return inventory_list


def sort_by_flammability(inventory_list):
    """인화성 지수를 기준으로 내림차순 정렬"""
    return sorted(inventory_list, key=lambda x: x['flammability'], reverse=True)


def filter_high_flammability(inventory_list, threshold=0.7):
    """인화성 지수가 threshold 이상인 항목만 필터링"""
    dangerous_items = [item for item in inventory_list if item['flammability'] >= threshold]
    return dangerous_items


def save_to_csv(data, filename):
    """리스트를 CSV 파일로 저장"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            if data:
                fieldnames = ['Substance', 'Weight (g/cm³)', 'Specific Gravity', 'Strength', 'Flammability']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                writer.writeheader()
                for item in data:
                    writer.writerow({
                        'Substance': item['substance'],
                        'Weight (g/cm³)': item['weight'],
                        'Specific Gravity': item['specific_gravity'],
                        'Strength': item['strength'],
                        'Flammability': item['flammability']
                    })
        print(f'\n{filename} 파일에 저장 완료')
    except Exception as e:
        print(f'\nCSV 저장 중 오류 발생: {e}')


def save_to_binary(data, filename):
    """리스트를 이진 파일로 저장 (보너스 과제)"""
    try:
        with open(filename, 'wb') as file:
            pickle.dump(data, file)
        print(f'\n{filename} 이진 파일에 저장 완료')
    except Exception as e:
        print(f'\n이진 파일 저장 중 오류 발생: {e}')


def load_from_binary(filename):
    """이진 파일에서 데이터 읽기 (보너스 과제)"""
    try:
        with open(filename, 'rb') as file:
            data = pickle.load(file)
        print(f'\n{filename} 이진 파일에서 읽기 완료')
        return data
    except FileNotFoundError:
        print(f'\n파일 {filename}을 찾을 수 없습니다.')
        return []
    except Exception as e:
        print(f'이진 파일 읽기 중 오류 발생: {e}')
        return []


def main():
    # CSV 파일 내용을 그냥 출력
    csv_filename = 'mars_base/Mars_Base_Inventory_List.csv'
    print_csv_content(csv_filename)
    
    # CSV 파일 읽기
    inventory_data = read_csv_to_list(csv_filename)
    
    if not inventory_data:
        print('데이터를 읽을 수 없습니다.')
        return

    # 인화성 지수로 내림차순 정렬
    sorted_data = sort_by_flammability(inventory_data)
    print('\n=== 인화성 지수 기준 내림차순 정렬 결과 ===')
    for item in sorted_data:
        print(f'{item["substance"]}: {item["flammability"]}')
    
    # 인화성 지수 0.7 이상 필터링
    dangerous_items = filter_high_flammability(sorted_data, 0.7)
    print(f'\n=== 위험 물질 (인화성 지수 0.7 이상): {len(dangerous_items)}개 ===')
    for item in dangerous_items:
        print(f'{item["substance"]}: {item["flammability"]}')
    
    # 위험 물질을 CSV로 저장
    danger_csv_filename = 'Mars_Base_Inventory_danger.csv'
    save_to_csv(dangerous_items, danger_csv_filename)
    
    # 보너스 과제: 이진 파일 저장
    binary_filename = 'Mars_Base_Inventory_List.bin'
    save_to_binary(sorted_data, binary_filename)
    
    # 보너스 과제: 이진 파일 읽기
    loaded_data = load_from_binary(binary_filename)
    print(f'\n=== 이진 파일에서 읽은 데이터 ===')
    for item in loaded_data:
        print(f'{item["substance"]}: {item["flammability"]}')

if __name__ == '__main__':
    main()
