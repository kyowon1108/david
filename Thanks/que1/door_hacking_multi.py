import zipfile
import itertools
import string
import time
from multiprocessing import Pool, cpu_count, Manager
from typing import Optional, List, Generator
import os
import threading
import signal


def generate_password_chunks(chunk_size: int = 50000) -> Generator[List[str], None, None]:
    """
    비밀번호를 청크 단위로 생성 (더 작은 청크로 안정성 향상)
    """
    chars = string.digits + string.ascii_lowercase
    
    # 자주 사용되는 문자 순서 (빈도수 기반)
    frequent_chars = '1234567890abcdefghijklmnopqrstuvwxyz'
    
    current_chunk = []
    
    # 1단계: 자주 사용되는 문자로 시작하는 조합
    for start_char in frequent_chars[:10]:  # 상위 10개 문자
        for suffix in itertools.product(frequent_chars, repeat=5):
            password = start_char + ''.join(suffix)
            current_chunk.append(password)
            
            if len(current_chunk) >= chunk_size:
                yield current_chunk
                current_chunk = []
    
    # 2단계: 나머지 조합들
    for start_char in frequent_chars[10:]:
        for suffix in itertools.product(frequent_chars, repeat=5):
            password = start_char + ''.join(suffix)
            current_chunk.append(password)
            
            if len(current_chunk) >= chunk_size:
                yield current_chunk
                current_chunk = []
    
    # 마지막 청크 반환
    if current_chunk:
        yield current_chunk


def test_password_chunk(args) -> Optional[str]:
    """
    하나의 프로세스에서 비밀번호 청크를 테스트합니다.
    """
    zip_path, password_chunk = args
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            for password in password_chunk:
                try:
                    zip_file.read('password.txt', pwd=password.encode('utf-8'))
                    return password
                except (zipfile.BadZipFile, RuntimeError):
                    continue
                except Exception:
                    continue
    except Exception:
        pass
    
    return None


def progress_monitor(manager_dict, start_time):
    """
    별도 스레드에서 진행 상황을 모니터링하고 출력
    """
    last_attempt_count = 0
    last_time = start_time
    
    while not manager_dict.get('found', False):
        time.sleep(1.0)  # 1초마다 체크
        
        current_attempt_count = manager_dict.get('attempt_count', 0)
        current_time = time.time()
        
        if current_attempt_count > last_attempt_count:
            elapsed = current_time - start_time
            rate = current_attempt_count / elapsed if elapsed > 0 else 0
            
            # 1초간 증가한 시도 수
            attempts_in_second = current_attempt_count - last_attempt_count
            
            print(f"진행 상황: {current_attempt_count:,} 시도 | "
                  f"진행 시간: {elapsed:.1f}초 | "
                  f"속도: {rate:.0f} 시도/초 | "
                  f"1초간: {attempts_in_second:,} 시도")
            
            last_attempt_count = current_attempt_count
            last_time = current_time


def unlock_zip_stable(zip_path: str = "emergency_storage_key.zip", 
                     chunk_size: int = 50000) -> Optional[str]:
    """
    안정적인 멀티프로세싱을 사용하여 ZIP 파일의 비밀번호를 찾는 함수
    """
    print("안정적인 멀티프로세싱 ZIP 파일 비밀번호 탐색 시작")
    print(f"대상 파일: {zip_path}")
    print(f"CPU 코어 수: {cpu_count()}")
    print(f"청크 크기: {chunk_size:,}")
    print("=" * 50)
    
    start_time = time.time()
    
    # 멀티프로세싱 매니저 생성
    manager = Manager()
    manager_dict = manager.dict()
    manager_dict['attempt_count'] = 0
    manager_dict['found'] = False
    manager_dict['password'] = None
    
    # 프로세스 풀 생성 (코어 수의 절반으로 제한하여 안정성 향상)
    num_processes = max(1, cpu_count() // 2)
    print(f"사용할 프로세스 수: {num_processes}")
    
    try:
        with Pool(processes=num_processes) as pool:
            # 진행 상황 모니터링 스레드 시작
            monitor_thread = threading.Thread(
                target=progress_monitor, 
                args=(manager_dict, start_time)
            )
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # 비밀번호 청크들을 생성하고 작업 제출
            chunk_generator = generate_password_chunks(chunk_size)
            results = []
            max_pending_results = num_processes * 3  # 최대 대기 결과 수 제한
            
            for chunk in chunk_generator:
                # 시도 횟수 업데이트
                manager_dict['attempt_count'] += len(chunk)
                
                # 대기 중인 결과가 너무 많으면 일부 완료 대기
                while len(results) >= max_pending_results:
                    # 완료된 결과들 확인 및 제거
                    completed_results = []
                    for r in results:
                        if r.ready():
                            password = r.get()
                            if password:
                                manager_dict['found'] = True
                                manager_dict['password'] = password
                                
                                end_time = time.time()
                                total_time = end_time - start_time
                                total_attempts = manager_dict['attempt_count']
                                
                                print("\n" + "=" * 50)
                                print("비밀번호 발견!")
                                print(f"비밀번호: {password}")
                                print(f"총 소요 시간: {total_time:.2f}초")
                                print(f"총 시도 횟수: {total_attempts:,}")
                                print(f"평균 속도: {total_attempts/total_time:.0f} 시도/초")
                                print("=" * 50)
                                
                                # ZIP 파일 내용 추출 및 저장
                                save_zip_content(zip_path, password)
                                return password
                            completed_results.append(r)
                    
                    # 완료된 결과들 제거
                    for r in completed_results:
                        results.remove(r)
                    
                    # 아직 완료되지 않은 결과가 있으면 잠시 대기
                    if len(results) >= max_pending_results:
                        time.sleep(0.1)
                
                # 작업 제출 (비동기)
                result = pool.apply_async(test_password_chunk, [(zip_path, chunk)])
                results.append(result)
                
                # 주기적으로 완료된 결과들 확인
                if len(results) % 10 == 0:  # 10개 청크마다 확인
                    completed_results = []
                    for r in results:
                        if r.ready():
                            password = r.get()
                            if password:
                                manager_dict['found'] = True
                                manager_dict['password'] = password
                                
                                end_time = time.time()
                                total_time = end_time - start_time
                                total_attempts = manager_dict['attempt_count']
                                
                                print("\n" + "=" * 50)
                                print("비밀번호 발견!")
                                print(f"비밀번호: {password}")
                                print(f"총 소요 시간: {total_time:.2f}초")
                                print(f"총 시도 횟수: {total_attempts:,}")
                                print(f"평균 속도: {total_attempts/total_time:.0f} 시도/초")
                                print("=" * 50)
                                
                                # ZIP 파일 내용 추출 및 저장
                                save_zip_content(zip_path, password)
                                return password
                            completed_results.append(r)
                    
                    # 완료된 결과들 제거
                    for r in completed_results:
                        results.remove(r)
            
            # 남은 작업들 완료 대기
            print("모든 청크 제출 완료, 남은 작업 대기 중...")
            for result in results:
                password = result.get()
                if password:
                    manager_dict['found'] = True
                    manager_dict['password'] = password
                    
                    end_time = time.time()
                    total_time = end_time - start_time
                    total_attempts = manager_dict['attempt_count']
                    
                    print("\n" + "=" * 50)
                    print("비밀번호 발견!")
                    print(f"비밀번호: {password}")
                    print(f"총 소요 시간: {total_time:.2f}초")
                    print(f"총 시도 횟수: {total_attempts:,}")
                    print(f"평균 속도: {total_attempts/total_time:.0f} 시도/초")
                    print("=" * 50)
                    
                    # ZIP 파일 내용 추출 및 저장
                    save_zip_content(zip_path, password)
                    return password
                    
    except FileNotFoundError:
        print(f"오류: {zip_path} 파일을 찾을 수 없습니다.")
        return None
    except Exception as e:
        print(f"오류 발생: {e}")
        return None
    
    print("모든 가능한 비밀번호를 시도했지만 찾지 못했습니다.")
    return None


def save_zip_content(zip_path: str, password: str):
    """ZIP 파일에서 내용을 추출하고 저장합니다."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            zip_content = zip_file.read('password.txt', pwd=password.encode('utf-8'))
            zip_content_text = zip_content.decode('utf-8').strip()
            
            print(f"ZIP 파일에서 추출된 내용: {zip_content_text}")
            
            # ZIP 파일 내용을 password.txt에 저장
            with open("password.txt", "w", encoding="utf-8") as f:
                f.write(zip_content_text)
            print("ZIP 파일의 password.txt 내용이 password.txt에 저장되었습니다.")
            
    except Exception as e:
        print(f"ZIP 파일 내용 추출 중 오류: {e}")


def main():
    """메인 함수"""
    print("Mars Mission - Emergency Storage Key Hacker (Stable Multi-Processing)")
    print("=" * 50)
    
    try:
        # 실행 즉시 안정적인 멀티프로세싱 탐색 시작
        password = unlock_zip_stable()
        if password:
            print(f"\n성공적으로 비밀번호를 찾았습니다: {password}")
        else:
            print("\n비밀번호를 찾지 못했습니다.")
    except KeyboardInterrupt:
        print("\n프로그램이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")


if __name__ == "__main__":
    main()
