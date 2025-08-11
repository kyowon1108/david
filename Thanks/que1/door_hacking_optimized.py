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
    
    # 시작 시간 기록
    start_time = time.time()
    attempts = 0
    
    print(f'최적화된 암호 해독을 시작합니다...')
    print(f'총 조합 수: {len(chars) ** 6:,}')
    print(f'동시 실행 스레드 수: {max_workers}')
    print('-' * 40)
    
    # 암호 조합을 배치로 나누어 처리
    batch_size = 1000
    password_batches = []
    
    for i, password_tuple in enumerate(product(chars, repeat=6)):
        password = ''.join(password_tuple)
        if i % batch_size == 0:
            batch = []
        batch.append(password)
        if len(batch) == batch_size:
            password_batches.append(batch)
    
    # 마지막 배치 추가
    if batch:
        password_batches.append(batch)
    
    print(f'총 {len(password_batches)}개의 배치로 나누어 처리합니다.')
    
    # ThreadPoolExecutor를 사용한 병렬 처리
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 모든 배치에 대해 작업 제출
        future_to_batch = {}
        for batch_idx, batch in enumerate(password_batches):
            future = executor.submit(process_batch, zip_file_path, batch, batch_idx)
            future_to_batch[future] = batch_idx
        
        # 완료된 작업들 처리
        for future in as_completed(future_to_batch):
            batch_idx = future_to_batch[future]
            try:
                result = future.result()
                attempts += len(password_batches[batch_idx])
                
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
                progress = (attempts / (len(chars) ** 6)) * 100
                
                # 현재 시도 중인 암호 패턴 표시
                current_password = ''.join(password_batches[batch_idx][0])
                print(f'배치 {batch_idx + 1} 완료, 시도 횟수: {attempts:,}, '
                      f'진행률: {progress:.2f}%, 속도: {rate:.0f}번/초')
                print(f'현재 암호 패턴: {current_password}')
                
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


def process_batch(zip_file_path, password_batch, batch_idx):
    """암호 배치를 처리합니다."""
    for password in password_batch:
        success, found_password = try_password(zip_file_path, password)
        if success:
            return found_password
    return None


def main():
    """메인 함수"""
    zip_file = 'emergency_storage_key.zip'
    
    print('=' * 50)
    print('최적화된 ZIP 파일 암호 해독 프로그램')
    print('=' * 50)
    
    # CPU 코어 수에 따른 최적 스레드 수 결정
    import os
    optimal_workers = min(os.cpu_count() or 1, 8)  # 최대 8개로 제한
    
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
