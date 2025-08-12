#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
비밀번호 찾기 - 효율적인 ZIP 파일 해킹 도구
메모리 효율성을 고려하여 제너레이터를 사용합니다.
"""

import zipfile
import itertools
import time
import string
from typing import Generator, Optional


def generate_passwords() -> Generator[str, None, None]:
    """
    가능한 모든 6자리 비밀번호를 생성하는 제너레이터
    숫자와 소문자 알파벳만 사용 (특수문자 제외)
    """
    chars = string.digits + string.ascii_lowercase  # 0-9, a-z
    
    # 6자리 조합을 생성
    for password in itertools.product(chars, repeat=6):
        yield ''.join(password)


def unlock_zip(zip_path: str = "emergency_storage_key.zip") -> Optional[str]:
    """
    ZIP 파일의 비밀번호를 찾는 함수
    
    Args:
        zip_path: 해킹할 ZIP 파일 경로
        
    Returns:
        찾은 비밀번호 또는 None (실패 시)
    """
    print("ZIP 파일 비밀번호 해킹 시작!")
    print(f"대상 파일: {zip_path}")
    print("=" * 50)
    
    # 시작 시간 기록
    start_time = time.time()
    
    # 총 가능한 조합 수 계산
    total_combinations = 36 ** 6  # 10(숫자) + 26(소문자) = 36개 문자, 6자리
    print(f"총 시도할 조합 수: {total_combinations:,}")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            # 파일 목록 확인
            file_list = zip_file.namelist()
            print(f"ZIP 내 파일: {file_list}")
            print("=" * 50)
            
            # 비밀번호 시도
            attempt_count = 0
            last_progress_time = start_time
            
            for password in generate_passwords():
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
                
                # 비밀번호 시도
                try:
                    # 먼저 파일 무결성 확인
                    if zip_file.testzip() is not None:
                        print("경고: ZIP 파일이 손상되었을 수 있습니다.")
                    
                    # 개별 파일로 테스트
                    for file_name in file_list:
                        try:
                            # 파일 읽기 시도
                            content = zip_file.read(file_name, pwd=password.encode('utf-8'))
                            
                            # 성공! (내용이 실제로 읽혔는지 확인)
                            if content:
                                end_time = time.time()
                                total_time = end_time - start_time
                                
                                print("\n" + "=" * 50)
                                print("비밀번호 발견!")
                                print(f"비밀번호: {password}")
                                print(f"총 소요 시간: {total_time:.2f}초")
                                print(f"총 시도 횟수: {attempt_count:,}")
                                print(f"평균 속도: {attempt_count/total_time:.0f} 시도/초")
                                print("=" * 50)
                                
                                # 비밀번호를 파일로 저장
                                with open("password.txt", "w", encoding="utf-8") as f:
                                    f.write(password)
                                print("비밀번호가 password.txt에 저장되었습니다.")
                                
                                return password
                            
                        except (zipfile.BadZipFile, RuntimeError, Exception):
                            # 잘못된 비밀번호, 계속 시도
                            continue
                    
                    # 모든 파일에서 실패한 경우
                    continue
                    
                except Exception:
                    # 예상치 못한 오류, 계속 시도
                    continue
                    
    except FileNotFoundError:
        print(f"오류: {zip_path} 파일을 찾을 수 없습니다.")
        return None
    except Exception as e:
        print(f"오류 발생: {e}")
        return None
    
    # 모든 조합을 시도했지만 실패
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n" + "=" * 50)
    print("모든 가능한 비밀번호를 시도했지만 실패했습니다.")
    print(f"총 소요 시간: {total_time:.2f}초")
    print(f"총 시도 횟수: {attempt_count:,}")
    print("=" * 50)
    
    return None


def main():
    """메인 함수"""
    print("Mars Mission - Emergency Storage Key Hacker")
    print("=" * 50)
    
    # 비밀번호 찾기 실행
    password = unlock_zip()
    
    if password:
        print(f"\n성공적으로 비밀번호를 찾았습니다: {password}")
    else:
        print("\n비밀번호를 찾지 못했습니다.")


if __name__ == "__main__":
    main()
