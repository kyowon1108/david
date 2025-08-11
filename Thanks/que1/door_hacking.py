import zipfile
import time
import string
from itertools import product


def unlock_zip(zip_file_path):
    """
    ZIP 파일의 암호를 무차별 대입으로 찾습니다.
    
    Args:
        zip_file_path (str): 암호를 찾을 ZIP 파일 경로
        
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
    
    print(f'암호 해독을 시작합니다...')
    print(f'총 조합 수: {len(chars) ** 6:,}')
    print('-' * 40)
    
    # 6자리 암호 조합 생성 및 시도
    for password_tuple in product(chars, repeat=6):
        password = ''.join(password_tuple)
        attempts += 1
        
        # 진행 상황 출력 (1000번마다)
        if attempts % 1000 == 0:
            elapsed_time = time.time() - start_time
            rate = attempts / elapsed_time if elapsed_time > 0 else 0
            print(f'시도 횟수: {attempts:,}, 속도: {rate:.0f}번/초')
        
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
                zip_file.extractall(pwd=password.encode('utf-8'))
                # 암호가 맞으면 여기까지 실행됨
                end_time = time.time()
                total_time = end_time - start_time
                
                print('-' * 40)
                print(f'🎉 암호를 찾았습니다!')
                print(f'암호: {password}')
                print(f'총 시도 횟수: {attempts:,}')
                print(f'총 소요 시간: {total_time:.2f}초')
                
                # 암호를 password.txt에 저장
                try:
                    with open('password.txt', 'w', encoding='utf-8') as f:
                        f.write(password)
                    print(f'암호가 password.txt에 저장되었습니다.')
                except Exception as e:
                    print(f'경고: password.txt 저장 중 오류 발생: {e}')
                
                return password
                
        except:
            # 잘못된 암호
            continue
    
    # 모든 조합을 시도했지만 암호를 찾지 못함
    end_time = time.time()
    total_time = end_time - start_time
    print('-' * 40)
    print(f'❌ 암호를 찾지 못했습니다.')
    print(f'총 시도 횟수: {attempts:,}')
    print(f'총 소요 시간: {total_time:.2f}초')
    return None


def main():
    """메인 함수"""
    zip_file = 'emergency_storage_key.zip'
    
    print('=' * 50)
    print('🚀 ZIP 파일 암호 해독 프로그램')
    print('=' * 50)
    
    password = unlock_zip(zip_file)
    
    if password:
        print(f'\n✅ 성공: 암호 "{password}"를 찾았습니다!')
    else:
        print(f'\n❌ 실패: 암호를 찾지 못했습니다.')
    
    print('=' * 50)


if __name__ == '__main__':
    main()
