import zipfile
import itertools
import time
import string
from typing import Optional, List


 


def generate_smart_passwords() -> itertools.product:
    """
    스마트한 순서로 비밀번호를 생성합니다.
    자주 사용되는 문자 조합을 우선적으로 시도합니다.
    """
    # 자주 사용되는 문자 순서 (빈도수 기반)
    frequent_chars = '1234567890abcdefghijklmnopqrstuvwxyz'
    
    # 1단계: 자주 사용되는 문자로 시작하는 조합
    for start_char in frequent_chars[:10]:  # 상위 10개 문자
        for suffix in itertools.product(frequent_chars, repeat=5):
            yield start_char + ''.join(suffix)
    
    # 2단계: 나머지 조합들
    for start_char in frequent_chars[10:]:
        for suffix in itertools.product(frequent_chars, repeat=5):
            yield start_char + ''.join(suffix)


def generate_passwords() -> itertools.product:
    """
    기존의 무차별 대입 방식 (백업용)
    """
    chars = string.digits + string.ascii_lowercase
    return itertools.product(chars, repeat=6)


def test_password(zip_file: zipfile.ZipFile, password: str) -> bool:
    """
    주어진 비밀번호로 ZIP 파일을 열 수 있는지 테스트
    """
    try:
        zip_file.read('password.txt', pwd=password.encode('utf-8'))
        return True
    except (zipfile.BadZipFile, RuntimeError):
        return False
    except Exception:
        return False


def unlock_zip_smart(zip_path: str = "emergency_storage_key.zip") -> Optional[str]:
    """
    스마트한 알고리즘을 사용하여 ZIP 파일의 비밀번호를 찾는 함수
    """
    print("스마트 ZIP 파일 비밀번호 탐색 시작")
    print(f"대상 파일: {zip_path}")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            file_list = zip_file.namelist()
            print(f"ZIP 내 파일: {file_list}")
            print("=" * 50)
            
            # 스마트 패턴 공격
            print("스마트 패턴 공격 시작...")
            attempt_count = 0
            last_progress_time = start_time
            
            for password in generate_smart_passwords():
                attempt_count += 1
                
                # 진행률 표시 (1초마다)
                current_time = time.time()
                if current_time - last_progress_time >= 1.0:
                    elapsed = current_time - start_time
                    rate = attempt_count / elapsed if elapsed > 0 else 0
                    print(f"스마트 공격 진행: {attempt_count:,} 시도 | "
                          f"진행 시간: {elapsed:.1f}초 | "
                          f"속도: {rate:.0f} 시도/초")
                    last_progress_time = current_time
                
                if test_password(zip_file, password):
                    end_time = time.time()
                    total_time = end_time - start_time
                    
                    print("\n" + "=" * 50)
                    print("비밀번호 발견!")
                    print(f"비밀번호: {password}")
                    print(f"총 소요 시간: {total_time:.2f}초")
                    print(f"총 시도 횟수: {attempt_count:,}")
                    print(f"평균 속도: {attempt_count/total_time:.0f} 시도/초")
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
    
    print("모든 공격 방법을 시도했지만 비밀번호를 찾지 못했습니다.")
    return None


def unlock_zip(zip_path: str = "emergency_storage_key.zip") -> Optional[str]:
    """
    기존의 무차별 대입 방식
    """
    print("무차별 대입 ZIP 파일 비밀번호 해킹 시작!")
    print(f"대상 파일: {zip_path}")
    print("=" * 50)
    
    start_time = time.time()
    total_combinations = 36 ** 6
    print(f"총 시도할 조합 수: {total_combinations:,}")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            file_list = zip_file.namelist()
            print(f"ZIP 내 파일: {file_list}")
            print("=" * 50)
            
            attempt_count = 0
            last_progress_time = start_time
            
            for password_tuple in generate_passwords():
                password = ''.join(password_tuple)
                attempt_count += 1
                
                # 진행률 표시 (1초마다)
                current_time = time.time()
                if current_time - last_progress_time >= 1.0:
                    elapsed = current_time - start_time
                    progress = (attempt_count / total_combinations) * 100
                    rate = attempt_count / elapsed if elapsed > 0 else 0
                    
                    print(f"진행 시간: {elapsed:.1f}초 | "
                          f"시도 횟수: {attempt_count:,} | "
                          f"진행률: {progress:.2f}% | "
                          f"속도: {rate:.0f} 시도/초")
                    
                    last_progress_time = current_time
                
                if test_password(zip_file, password):
                    end_time = time.time()
                    total_time = end_time - start_time
                    
                    print("\n" + "=" * 50)
                    print("비밀번호 발견!")
                    print(f"비밀번호: {password}")
                    print(f"총 소요 시간: {total_time:.2f}초")
                    print(f"총 시도 횟수: {attempt_count:,}")
                    print(f"평균 속도: {attempt_count/total_time:.0f} 시도/초")
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
    
    print("모든 가능한 비밀번호를 시도했지만 실패했습니다.")
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
    print("Mars Mission - Emergency Storage Key Hacker")
    print("=" * 50)
    try:
        # 실행 즉시 스마트 패턴 탐색 시작
        password = unlock_zip_smart()
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
