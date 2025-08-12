import string


def caesar_cipher_decode(target_text, shift):
    """
    카이사르 암호를 해독합니다.
    
    Args:
        target_text (str): 해독할 암호문
        shift (int): 이동할 자리수
        
    Returns:
        str: 해독된 평문
    """
    result = ''
    
    for char in target_text:
        if char.isalpha():
            # 알파벳인 경우에만 이동
            if char.isupper():
                shifted = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            else:
                shifted = chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
            result += shifted
        else:
            # 알파벳이 아닌 경우 그대로 유지
            result += char
    
    return result


def read_password_file():
    """password.txt 파일을 읽어옵니다."""
    try:
        with open('password.txt', 'r', encoding='utf-8') as f:
            content = f.read().strip()
            print(f'password.txt 파일을 읽었습니다: {content}')
            return content
    except FileNotFoundError:
        print('오류: password.txt 파일을 찾을 수 없습니다.')
        print('먼저 door_hacking.py를 실행하여 암호를 찾아주세요.')
        return None
    except Exception as e:
        print(f'오류: 파일 읽기 중 문제 발생: {e}')
        return None


def save_result(decoded_text, shift):
    """해독 결과를 caesar_result.txt에 저장합니다."""
    try:
        with open('caesar_result.txt', 'w', encoding='utf-8') as f:
            f.write(f'해독된 텍스트: {decoded_text}\n')
            f.write(f'사용된 자리수: {shift}\n')
        print(f'결과가 caesar_result.txt에 저장되었습니다.')
    except Exception as e:
        print(f'경고: caesar_result.txt 저장 중 오류 발생: {e}')


def main():
    """메인 함수"""
    print('=' * 50)
    print('🔐 카이사르 암호 해독 프로그램')
    print('=' * 50)
    
    # password.txt 파일 읽기
    encrypted_text = read_password_file()
    if not encrypted_text:
        return
    
    print(f'\n암호화된 텍스트: {encrypted_text}')
    print('-' * 50)
    
    # 모든 가능한 자리수로 해독 시도
    print('모든 자리수로 해독을 시도합니다...\n')
    
    for shift in range(26):
        decoded = caesar_cipher_decode(encrypted_text, shift)
        print(f'자리수 {shift:2d}: {decoded}')
    
    print('-' * 50)
    print('위 결과 중에서 의미가 있는 텍스트를 찾았나요?')
    
    # 사용자 입력 받기
    while True:
        try:
            user_input = input('올바른 자리수를 입력하세요 (0-25, 또는 q로 종료): ').strip()
            
            if user_input.lower() == 'q':
                print('프로그램을 종료합니다.')
                break
            
            shift = int(user_input)
            if 0 <= shift <= 25:
                decoded = caesar_cipher_decode(encrypted_text, shift)
                print(f'\n선택한 자리수 {shift}로 해독된 결과: {decoded}')
                
                # 결과 저장
                save_result(decoded, shift)
                break
            else:
                print('0에서 25 사이의 숫자를 입력해주세요.')
        except ValueError:
            print('올바른 숫자를 입력해주세요.')
        except KeyboardInterrupt:
            print('\n\n프로그램을 종료합니다.')
            break
    
    print('=' * 50)


if __name__ == '__main__':
    main()
