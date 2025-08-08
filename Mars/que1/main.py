import json
import os
from datetime import datetime


def read_log_file(log_file_path):
    try:
        # 파일 존재 여부 확인
        if not os.path.exists(log_file_path):
            print(f"오류: 파일 '{log_file_path}'을 찾을 수 없습니다.")
            return None
            
        # 파일 읽기
        with open(log_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        print("=== 로그 파일 전체 내용 ===")
        print(content)
        print("=" * 50)
        
        return content
        
    except UnicodeDecodeError as e:
        print(f"디코딩 오류: {e}")
        return None
    except IOError as e:
        print(f"파일 읽기 오류: {e}")
        return None
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        return None


def parse_log_content(content, show_output=True):
    try:
        lines = content.strip().split('\n')
        log_entries = []
        
        # 첫 번째 라인은 헤더이므로 건너뛰기
        for line in lines[1:]:
            if line.strip():
                parts = line.split(',', 2)  # 시간, 로그레벨, 내용으로 분리
                if len(parts) >= 3:
                    timestamp = parts[0].strip()
                    message = parts[2].strip()
                    log_entries.append([timestamp, message])
        
        if show_output:            
            print("\n=== 파싱된 리스트 객체 ===")
            for entry in log_entries:
                print(entry)
            print("=" * 50)
        
        return log_entries
        
    except Exception as e:
        print(f"로그 파싱 중 오류 발생: {e}")
        return []


def sort_by_time_desc(log_entries, show_output=True):
    """시간 역순 정렬"""
    try:
        sorted_entries = sorted(log_entries, 
                              key=lambda x: datetime.strptime(x[0], '%Y-%m-%d %H:%M:%S'), 
                              reverse=True)
        
        if show_output:
            print("\n=== 시간 역순으로 정렬된 리스트 ===")
            for entry in sorted_entries:
                print(entry)
            print("=" * 50)
        
        return sorted_entries
        
    except Exception as e:
        print(f"정렬 중 오류 발생: {e}")
        return log_entries


def convert_to_dict(sorted_entries):
    """정렬된 리스트를 사전(Dict) 객체로 변환"""
    try:
        log_dict = {
            "mission_log": [],
            "total_entries": len(sorted_entries),
            "processed_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        for i, entry in enumerate(sorted_entries):
            log_dict["mission_log"].append({
                "index": i + 1,
                "timestamp": entry[0],
                "message": entry[1]
            })
            
        print("\n=== Dict 객체로 변환 완료 ===")
        print(f"총 {log_dict['total_entries']}개의 로그 엔트리가 변환되었습니다.")
        print("=" * 50)
        
        return log_dict
        
    except Exception as e:
        print(f"Dict 변환 중 오류 발생: {e}")
        return {}


def save_to_json(log_dict, output_file_path):
    """
    Dict 객체를 JSON 파일로 저장합니다.
    """
    try:
        with open(output_file_path, 'w', encoding='utf-8') as file:
            json.dump(log_dict, file, ensure_ascii=False, indent=2)
            
        print(f"\n=== JSON 파일 저장 완료 ===")
        print(f"파일 경로: {output_file_path}")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"JSON 파일 저장 중 오류 발생: {e}")
        return False


def filter_danger_logs(log_entries):
    """위험 키워드가 포함된 로그만 필터링"""
    danger_keywords = ['oxygen', 'explosion', 'unstable', 'overheating']
    dangerous_logs = []
    
    try:
        for entry in log_entries:
            message_lower = entry[1].lower() # 소문자로 전부 변형해서 찾기
            for keyword in danger_keywords:
                if keyword.lower() in message_lower:
                    dangerous_logs.append(entry)
                    break
                    
        print(f"\n=== 위험 키워드 필터링 결과 ===")
        print(f"총 {len(dangerous_logs)}개의 위험 로그가 발견되었습니다:")
        for entry in dangerous_logs:
            print(f"  {entry[0]} -  {entry[1]}")
        print("=" * 50)
        
        return dangerous_logs
        
    except Exception as e:
        print(f"위험 로그 필터링 중 오류 발생: {e}")
        return []


def save_danger_logs(dangerous_logs, output_file_path):
    try:
        danger_dict = {
            "dangerous_logs": [],
            "total_dangerous_entries": len(dangerous_logs),
            "analyzed_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "danger_keywords": ['oxygen', 'explosion', 'unstable', 'overheating']
        }
        
        for i, entry in enumerate(dangerous_logs):
            danger_dict["dangerous_logs"].append({
                "index": i + 1,
                "timestamp": entry[0],
                "message": entry[1]
            })
            
        with open(output_file_path, 'w', encoding='utf-8') as file:
            json.dump(danger_dict, file, ensure_ascii=False, indent=2)
            
        print(f"\n=== 위험 로그 파일 저장 완료 ===")
        print(f"파일 경로: {output_file_path}")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"위험 로그 파일 저장 중 오류 발생: {e}")
        return False


def generate_analysis_report(dangerous_logs, output_file_path):
    try:
        report_content = f"""# 미션 컴퓨터 로그 분석 보고서

## 분석 개요
- 분석 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 총 위험 로그: {len(dangerous_logs)}개

## 위험 상황 요약

"""      
        if dangerous_logs:
            report_content += "### 발견된 위험 로그:\n\n"
            for i, log in enumerate(dangerous_logs, 1):
                report_content += f"{i}. **{log[0]}** - {log[1]}\n"

        else:
            report_content += "### 위험 로그 없음\n모든 시스템이 정상적으로 작동했습니다.\n\n"
        
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(report_content)
            
        print(f"\n=== 분석 보고서 생성 완료 ===")
        print(f"파일 경로: {output_file_path}")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"분석 보고서 생성 중 오류 발생: {e}")
        return False


def search_logs_by_keyword(json_file_path, search_keyword):
    try:
        if not os.path.exists(json_file_path):
            print(f"오류: JSON 파일 '{json_file_path}'을 찾을 수 없습니다.")
            return
            
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        matching_logs = []
        
        if "mission_log" in data:
            for log_entry in data["mission_log"]:
                message = log_entry.get("message", "").lower()
                if search_keyword.lower() in message: # 소문자로 바꿔서 찾기
                    matching_logs.append(log_entry)
                    
        print(f"\n=== '{search_keyword}' 검색 결과 ===")
        if matching_logs:
            print(f"총 {len(matching_logs)}개의 로그가 발견되었습니다:")
            for log in matching_logs:
                print(f"  {log['timestamp']} - {log['message']}")
        else:
            print("검색 조건에 맞는 로그가 없습니다.")
        print("=" * 50)
        
        return matching_logs
        
    except Exception as e:
        print(f"로그 검색 중 오류 발생: {e}")
        return []


def interactive_menu():
    """
    사용자 인터랙티브 메뉴를 제공합니다.
    """
    print("\n=== 미션 컴퓨터 로그 분석 도구 ===")
    print("1. 전체 로그 분석 실행 (JSON + 위험로그 + MD보고서)")
    print("2. 로그 파일 시간 역순으로 출력")
    print("3. 위험 키워드 로그 검색")
    print("4. 특정 키워드로 로그 검색")
    print("5. 종료")
    print("=" * 40)
    
    return input("원하는 기능을 선택하세요 (1-5): ").strip()


def main():
    print("=" * 50)
    
    # 파일 경로 설정
    log_file_path = "mission_computer_main.log"
    output_file_path = "mission_computer_main.json"
    danger_log_file = "dangerous_logs.json"
    analysis_report_file = "log_analysis.md"
    
    while True:
        choice = interactive_menu()
        
        if choice == "1":
            # 전체 로그 분석 실행
            print("\n전체 로그 분석을 시작합니다...")
            
            # 1. 로그 파일 읽기
            content = read_log_file(log_file_path)
            if content is None:
                print("로그 파일을 읽을 수 없습니다.")
                continue
            
            # 2. 로그 내용 파싱
            log_entries = parse_log_content(content)
            if not log_entries:
                print("파싱할 로그 데이터가 없습니다.")
                continue
            
            # 3. 시간 역순으로 정렬
            sorted_entries = sort_by_time_desc(log_entries)
            
            # 4. Dict 객체로 변환
            log_dict = convert_to_dict(sorted_entries)
            if not log_dict:
                print("Dict 변환에 실패했습니다.")
                continue
            
            # 5. JSON 파일로 저장
            success = save_to_json(log_dict, output_file_path)
            
            # 6. 위험 로그 필터링 및 저장
            dangerous_logs = filter_danger_logs(sorted_entries)
            if dangerous_logs:
                save_danger_logs(dangerous_logs, danger_log_file)
            
            # 7. 분석 보고서 생성
            generate_analysis_report(dangerous_logs, analysis_report_file)
            
            if success:
                print("\n모든 작업이 성공적으로 완료되었습니다!")
            else:
                print("\n일부 작업에서 오류가 발생했습니다.")
                
        elif choice == "2":
            # 로그 파일 시간 역순으로 출력
            print("\n로그 파일을 시간 역순으로 출력합니다...")
            content = read_log_file(log_file_path)
            if content:
                log_entries = parse_log_content(content, show_output=False)
                sorted_entries = sort_by_time_desc(log_entries, show_output=False)
                
                print("\n=== 시간 역순 정렬된 로그 ===")
                for i, entry in enumerate(sorted_entries, 1):
                    print(f"{i:2d}. {entry[0]} - {entry[1]}")
                print("=" * 50)
                
        elif choice == "3":
            # 위험 키워드 로그 검색
            print("\n위험 키워드 로그를 검색합니다...")
            content = read_log_file(log_file_path)
            if content:
                log_entries = parse_log_content(content)
                dangerous_logs = filter_danger_logs(log_entries)
                if dangerous_logs:
                    save_danger_logs(dangerous_logs, danger_log_file)
                    
        elif choice == "4":
            # 특정 키워드로 로그 검색
            if not os.path.exists(output_file_path):
                print("먼저 전체 로그 분석을 실행해주세요 (옵션 1).")
                continue
                
            search_keyword = input("검색할 키워드를 입력하세요: ").strip()
            if search_keyword:
                search_logs_by_keyword(output_file_path, search_keyword)
            else:
                print("유효한 키워드를 입력해주세요.")
                
        elif choice == "5":
            print("프로그램을 종료합니다.")
            break
            
        else:
            print("잘못된 선택입니다. 1-5 중에서 선택해주세요.")


if __name__ == "__main__":
    main()
