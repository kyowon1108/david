#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사전 기반 카이사르 암호 자동 해독 프로그램
password.txt 파일을 읽어와서 사전을 기반으로 자동으로 카이사르 암호를 해독합니다.
"""

import string


def create_dictionary():
    """일반적인 영어 단어들의 사전을 생성합니다."""
    # 일반적인 영어 단어들
    common_words = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her',
        'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there',
        'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get',
        'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no',
        'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your',
        'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then',
        'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
        'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first',
        'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
        'give', 'day', 'most', 'us', 'hello', 'world', 'password', 'key',
        'secret', 'code', 'access', 'system', 'computer', 'data', 'file',
        'open', 'close', 'start', 'stop', 'run', 'execute', 'program',
        'mission', 'mars', 'base', 'emergency', 'storage', 'unlock',
        'success', 'failure', 'error', 'warning', 'info', 'debug', 'test'
    }
    
    print(f'사전에 {len(common_words)}개의 단어가 로드되었습니다.')
    return common_words


def caesar_cipher_decode(target_text, shift):
    """카이사르 암호를 해독합니다."""
    result = ''
    
    for char in target_text:
        if char.isalpha():
            if char.isupper():
                shifted = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            else:
                shifted = chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
            result += shifted
        else:
            result += char
    
    return result


def calculate_word_score(decoded_text, dictionary):
    """해독된 텍스트의 단어 점수를 계산합니다."""
    words = decoded_text.lower().split()
    score = 0
    
    for word in words:
        clean_word = ''.join(c for c in word if c.isalpha())
        if clean_word in dictionary:
            score += 1
            score += len(clean_word) // 3
    
    return score


def auto_decode_caesar(encrypted_text, dictionary):
    """사전을 기반으로 자동으로 카이사르 암호를 해독합니다."""
    best_shift = 0
    best_score = 0
    best_decoded = ''
    
    print('사전 기반 자동 해독을 시작합니다...\n')
    
    for shift in range(26):
        decoded = caesar_cipher_decode(encrypted_text, shift)
        score = calculate_word_score(decoded, dictionary)
        
        print(f'자리수 {shift:2d}: {decoded} (점수: {score})')
        
        if score > best_score:
            best_score = score
            best_shift = shift
            best_decoded = decoded
    
    return best_shift, best_decoded, best_score


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


def save_result(decoded_text, shift, score):
    """해독 결과를 result.txt에 저장합니다."""
    try:
        with open('result.txt', 'w', encoding='utf-8') as f:
            f.write(f'해독된 텍스트: {decoded_text}\n')
            f.write(f'사용된 자리수: {shift}\n')
            f.write(f'단어 점수: {score}\n')
            f.write(f'해독 방법: 사전 기반 자동 해독\n')
        print(f'결과가 result.txt에 저장되었습니다.')
    except Exception as e:
        print(f'경고: result.txt 저장 중 오류 발생: {e}')


def main():
    """메인 함수"""
    print('=' * 50)
    print('🔐 사전 기반 카이사르 암호 자동 해독 프로그램')
    print('=' * 50)
    
    # 사전 생성
    dictionary = create_dictionary()
    
    # password.txt 파일 읽기
    encrypted_text = read_password_file()
    if not encrypted_text:
        return
    
    print(f'\n암호화된 텍스트: {encrypted_text}')
    print('-' * 50)
    
    # 자동 해독 실행
    best_shift, best_decoded, best_score = auto_decode_caesar(encrypted_text, dictionary)
    
    print('-' * 50)
    print(f'🎯 자동 해독 결과:')
    print(f'최적 자리수: {best_shift}')
    print(f'해독된 텍스트: {best_decoded}')
    print(f'단어 점수: {best_score}')
    
    if best_score > 0:
        print(f'\n✅ 의미 있는 텍스트를 찾았습니다!')
        
        # 결과 저장
        save_result(best_decoded, best_shift, best_score)
        
        # 사용자 확인
        confirm = input(f'\n이 결과를 사용하시겠습니까? (y/n): ').strip().lower()
        if confirm in ['y', 'yes', '네']:
            print('결과가 result.txt에 저장되었습니다.')
        else:
            print('사용자가 결과 저장을 취소했습니다.')
    else:
        print(f'\n❌ 의미 있는 텍스트를 찾지 못했습니다.')
        print('수동으로 자리수를 확인해보세요.')
    
    print('=' * 50)


if __name__ == '__main__':
    main()
