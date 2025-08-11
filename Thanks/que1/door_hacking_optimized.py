import zipfile
import time
import string
from itertools import product
from concurrent.futures import ThreadPoolExecutor, as_completed


def try_password(zip_file_path, password):
    """단일 암호를 시도합니다."""
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
            zip_file.extractall(pwd=password.encode('utf-8'))
            return True, password
    except:
        return False, password


def generate_password_batch(start_index, batch_size, chars):
    """특정 범위의 암호 배치를 생성합니다."""
    passwords = []
    count = 0
    
    for password_tuple in product(chars, repeat=6):
        if count >= start_index:
            password = ''.join(password_tuple)
            passwords.append(password)
            
            if len(passwords) >= batch_size:
                break
        count += 1
    
    return passwords


def unlock_zip_optimized(zip_file_path, max_workers=4):
    """
    최적화된 방법으로 ZIP 파일의 암호를 찾습니다.
    
    Args:
        zip_file_path (str): 암호를 찾을 ZIP 파일 경로
        max_workers (int): 동시 실행할 스레드 수
        
    Returns:
        str: 찾은 암호 또는 None
    """
    # ZIP 파일 확인
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
            print(f'ZIP 파일을 열었습니다: {zip_file_path}')
    except Exception as e:
        print(f'오류: {e}')
        return None
    
    # 가능한 문자들 (숫자와 소문자 알파벳)
    chars = string.digits + string.ascii_lowercase
    total_combinations = len(chars) ** 6
    
    # 시작 시간 기록
    start_time = time.time()
    attempts = 0
    
    print(f'최적화된 암호 해독을 시작합니다...')
    print(f'총 조합 수: {total_combinations:,}')
    print(f'동시 실행 스레드 수: {max_workers}')
    print('-' * 40)
    
    # 배치 크기와 총 배치 수 계산
    batch_size = 10000  # 배치 크기를 늘림
    total_batches = (total_combinations + batch_size - 1) // batch_size
    
    print(f'배치 크기: {batch_size:,}, 총 배치 수: {total_batches:,}')
    
    # ThreadPoolExecutor를 사용한 병렬 처리
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 배치별로 작업 제출
        future_to_batch = {}
        
        for batch_idx in range(total_batches):
            start_index = batch_idx * batch_size
            future = executor.submit(process_batch_range, zip_file_path, start_index, batch_size, chars, batch_idx)
            future_to_batch[future] = batch_idx
        
        # 완료된 작업들 처리
        for future in as_completed(future_to_batch):
            batch_idx = future_to_batch[future]
            try:
                result = future.result()
                attempts += batch_size
                
                if result:
                    # 암호를 찾았음
                    end_time = time.time()
                    total_time = end_time - start_time
                    
                    print('-' * 40)
                    print(f'암호를 찾았습니다!')
                    print(f'암호: {result}')
                    print(f'총 시도 횟수: {attempts:,}')
                    print(f'총 소요 시간: {total_time:.2f}초')
                    
                    # 암호를 password.txt에 저장
                    try:
                        with open('password.txt', 'w', encoding='utf-8') as f:
                            f.write(result)
                        print(f'암호가 password.txt에 저장되었습니다.')
                    except Exception as e:
                        print(f'경고: password.txt 저장 중 오류 발생: {e}')
                    
                    return result
                
                # 진행 상황 출력
                elapsed_time = time.time() - start_time
                rate = attempts / elapsed_time if elapsed_time > 0 else 0
                progress = (attempts / total_combinations) * 100
                
                # 현재 시도 중인 암호 패턴 표시 (대략적인 위치)
                current_pattern = get_password_at_index(start_index, chars)
                print(f'배치 {batch_idx + 1}/{total_batches} 완료, 시도 횟수: {attempts:,}, '
                      f'진행률: {progress:.2f}%, 속도: {rate:.0f}번/초')
                print(f'현재 암호 패턴: {current_pattern}')
                
            except Exception as e:
                print(f'배치 {batch_idx + 1} 처리 중 오류 발생: {e}')
    
    # 모든 조합을 시도했지만 암호를 찾지 못함
    end_time = time.time()
    total_time = end_time - start_time
    print('-' * 40)
    print(f'암호를 찾지 못했습니다.')
    print(f'총 시도 횟수: {attempts:,}')
    print(f'총 소요 시간: {total_time:.2f}초')
    return None


def process_batch_range(zip_file_path, start_index, batch_size, chars, batch_idx):
    """특정 범위의 암호 배치를 처리합니다."""
    passwords = generate_password_batch(start_index, batch_size, chars)
    
    for password in passwords:
        success, found_password = try_password(zip_file_path, password)
        if success:
            return found_password
    return None


def get_password_at_index(index, chars):
    """특정 인덱스의 암호를 계산합니다."""
    if index == 0:
        return '000000'
    
    # 간단한 근사치 계산
    total_chars = len(chars)
    positions = []
    temp_index = index
    
    for i in range(6):
        pos = temp_index % total_chars
        positions.insert(0, chars[pos])
        temp_index //= total_chars
    
    return ''.join(positions)


def main():
    """메인 함수"""
    zip_file = 'emergency_storage_key.zip'
    
    print('=' * 50)
    print('최적화된 ZIP 파일 암호 해독 프로그램')
    print('=' * 50)
    
    # CPU 코어 수에 따른 최적 스레드 수 결정
    import os
    optimal_workers = min(os.cpu_count() or 1, 4)  # 최대 4개로 제한하여 메모리 사용량 줄임
    
    print(f'시스템 CPU 코어 수: {os.cpu_count() or 1}')
    print(f'권장 스레드 수: {optimal_workers}')
    
    password = unlock_zip_optimized(zip_file, max_workers=optimal_workers)
    
    if password:
        print(f'\n성공: 암호 "{password}"를 찾았습니다!')
    else:
        print(f'\n실패: 암호를 찾지 못했습니다.')
    
    print('=' * 50)


if __name__ == '__main__':
    main()
