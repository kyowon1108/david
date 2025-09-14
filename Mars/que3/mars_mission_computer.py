import random
import json
import time
import datetime
import platform
import os
import psutil
import threading
import multiprocessing
import signal
import sys


class DummySensor:
    """더미 센서 클래스 - 테스트용 랜덤 데이터 생성"""
    
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': 0.0, # 화성 기지 내부 온도
            'mars_base_external_temperature': 0.0, # 화성 기지 외부 온도
            'mars_base_internal_humidity': 0.0, # 화성 기지 내부 습도
            'mars_base_external_illuminance': 0.0, # 화성 기지 외부 광량
            'mars_base_internal_co2': 0.0, # 화성 기지 내부 이산화탄소 농도
            'mars_base_internal_oxygen': 0.0 # 화성 기지 내부 산소 농도
        }

    def set_env(self):
        """랜덤한 환경 데이터 생성"""
        self.env_values = {
            'mars_base_internal_temperature': round(random.uniform(18, 30), 2), # (18~30도)
            'mars_base_external_temperature': round(random.uniform(0, 21), 2), # (0~21도)
            'mars_base_internal_humidity': round(random.uniform(50, 60), 2), # (50~60%)
            'mars_base_external_illuminance': round(random.uniform(500, 715), 2), # (500~715 W/m2)
            'mars_base_internal_co2': round(random.uniform(0.02, 0.1), 4), # (0.02~0.1%)
            'mars_base_internal_oxygen': round(random.uniform(4, 7), 2) # (4%~7%)
        }

    def get_env(self):
        """환경 데이터 반환 및 로그 기록 (보너스)"""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 로그 파일에 기록
        try:
            with open('sensor_log.txt', 'a', encoding='utf-8') as f:
                log_entry = f"{timestamp}, {self.env_values['mars_base_internal_temperature']}, " \
                           f"{self.env_values['mars_base_external_temperature']}, " \
                           f"{self.env_values['mars_base_internal_humidity']}, " \
                           f"{self.env_values['mars_base_external_illuminance']}, " \
                           f"{self.env_values['mars_base_internal_co2']}, " \
                           f"{self.env_values['mars_base_internal_oxygen']}\n"
                f.write(log_entry)
        except Exception as e:
            print(f'로그 기록 오류: {e}')
        
        return self.env_values


class MissionComputer:
    """미션 컴퓨터 클래스"""
    
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }
        self.ds = DummySensor() # DummySensor 클래스를 ds라는 이름으로 인스턴스(Instance)로 만듦
        self.running = True
        self.env_history = []  # 5분 평균 계산용
        self.last_average_time = time.time()
        
        # 설정 파일 읽기 (보너스)
        self.load_settings()
    

    
    def load_settings(self):
        """설정 파일 읽기 (보너스)"""
        try:
            if os.path.exists('setting.txt'):
                with open('setting.txt', 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            else:
                # 기본 설정 생성 (최초 생성시)
                self.settings = {
                    'show_system_info': True,
                    'show_load_info': True,
                    'show_sensor_data': True,
                    'sensor_interval': 5,
                    'system_interval': 20
                }
                with open('setting.txt', 'w', encoding='utf-8') as f:
                    json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f'설정 파일 읽기 오류: {e}')
            self.settings = {
                'show_system_info': True,
                'show_load_info': True,
                'show_sensor_data': True,
                'sensor_interval': 5,
                'system_interval': 20
            }
    
    def get_sensor_data(self):
        """
        센서 데이터 수집 및 출력
        
        1. 센서의 값을 가져와서 env_values에 담는다.
        2. env_values의 값을 출력한다. 이때 환경 정보의 값은 json 형태로 화면에 출력한다.
        3. 위의 두 가지 동작을 5초에 한번씩 반복한다.
        """
        print('=== 센서 데이터 모니터링 시작 ===')
        
        while self.running:
            try:
                # 센서 값 가져오기
                self.ds.set_env()
                self.env_values = self.ds.get_env() # 1
                
                # 히스토리 저장 (5분 평균용)
                self.env_history.append({
                    'timestamp': time.time(),
                    'data': self.env_values.copy() # 2
                })
                
                # JSON 형태로 출력
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                output_data = {
                    'timestamp': timestamp,
                    'sensor_data': self.env_values # 2
                }
                
                if self.settings.get('show_sensor_data', True):
                    print(f'[센서 데이터] {json.dumps(output_data, indent=2, ensure_ascii=False)}') # 2
                
                # 5분 평균 계산 (보너스)
                current_time = time.time()
                if current_time - self.last_average_time >= 20:  # 5분 = 300초
                    self.calculate_5min_average()
                    self.last_average_time = current_time
                
                time.sleep(self.settings.get('sensor_interval', 5))
                
            except Exception as e:
                print(f'센서 데이터 오류: {e}')
                time.sleep(1)
    
    def calculate_5min_average(self):
        """5분 평균값 계산 (보너스)"""
        if not self.env_history:
            return
        
        current_time = time.time()
        five_min_ago = current_time - 20
        
        # 5분 이내 데이터만 필터링
        recent_data = [item for item in self.env_history if item['timestamp'] >= five_min_ago]
        
        if not recent_data:
            return
        
        # 평균 계산
        averages = {}
        for key in self.env_values.keys():
            values = [item['data'][key] for item in recent_data]
            averages[key] = round(sum(values) / len(values), 2)
        
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        average_output = {
            'timestamp': timestamp,
            'type': '5분_평균',
            'averages': averages
        }
        
        print(f'[5분 평균] {json.dumps(average_output, indent=2, ensure_ascii=False)}')
        
        # 오래된 데이터 제거
        self.env_history = recent_data
    
    def get_mission_computer_info(self):
        """미션 컴퓨터 시스템 정보 수집 (20초마다 반복)"""
        while self.running:
            try:
                system_info = {
                    'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'system_info': {
                        'operating_system': platform.system(),
                        'os_version': platform.version(),
                        'cpu_type': platform.processor() or platform.machine(),
                        'cpu_cores': os.cpu_count(),
                        'memory_size_gb': round(psutil.virtual_memory().total / (1024**3), 2)
                    }
                }
                
                if self.settings.get('show_system_info', True):
                    print(f'[시스템 정보] {json.dumps(system_info, indent=2, ensure_ascii=False)}')
                
                time.sleep(self.settings.get('system_interval', 20)) # 20초마다 실행
                
            except Exception as e:
                print(f'시스템 정보 수집 오류: {e}')
                time.sleep(5)
    
    def get_mission_computer_load(self):
        """미션 컴퓨터 부하 정보 수집 (20초마다 반복)"""
        while self.running:
            try:
                load_info = {
                    'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'load_info': {
                        'cpu_usage_percent': round(psutil.cpu_percent(interval=1), 2),
                        'memory_usage_percent': round(psutil.virtual_memory().percent, 2),
                        'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2)
                    }
                }
                
                if self.settings.get('show_load_info', True):
                    print(f'[시스템 부하] {json.dumps(load_info, indent=2, ensure_ascii=False)}')
                
                time.sleep(self.settings.get('system_interval', 20)) # 20초마다 실행
                
            except Exception as e:
                print(f'시스템 부하 수집 오류: {e}')
                time.sleep(5)
    
    def stop_system(self):
        """시스템 정지"""
        self.running = False
        print('System stoped….')


def signal_handler(signum, frame):
    """시그널 핸들러 - Ctrl+C 처리"""
    print('\n프로그램을 종료합니다...')
    sys.exit(0)


def run_multithread():
    """멀티스레드 실행"""
    print('=== 멀티스레드 모드 시작 ===')
    
    RunComputer = MissionComputer() # MissionComputer 클래스를 RunComputer 라는 이름으로 인스턴스화
    
    # 스레드 생성 - 기존 메소드 사용
    thread1 = threading.Thread(target=RunComputer.get_mission_computer_info, daemon=True)
    thread2 = threading.Thread(target=RunComputer.get_mission_computer_load, daemon=True)
    thread3 = threading.Thread(target=RunComputer.get_sensor_data, daemon=True)
    
    # 스레드 시작
    thread1.start()
    thread2.start()
    thread3.start()
    
    try:
        # 메인 스레드에서 키 입력 대기
        while True:
            user_input = input('시스템을 중지하려면 "q" 입력: ')
            if user_input.lower() == 'q':
                RunComputer.stop_system()
                break
    except Exception as e:
        print(f'오류 발생: {e}')
    
    print('멀티스레드 실행 완료')


def run_multiprocess():
    """멀티프로세스 실행"""
    print('=== 멀티프로세스 모드 시작 ===')
    
    # MissionComputer를 RunComputer1, RunComputer2, RunComputer3으로 인스턴스화
    RunComputer1 = MissionComputer()
    RunComputer2 = MissionComputer()
    RunComputer3 = MissionComputer()
    
    # 각각을 별도 프로세스로 실행 - 기존 메소드 사용
    process1 = multiprocessing.Process(target=RunComputer1.get_mission_computer_info)
    process2 = multiprocessing.Process(target=RunComputer2.get_mission_computer_load)
    process3 = multiprocessing.Process(target=RunComputer3.get_sensor_data)
    
    try:
        # 프로세스 시작
        process1.start()
        process2.start()
        process3.start()
        
        # 키 입력 대기
        while True:
            user_input = input('시스템을 중지하려면 "q" 입력: ')
            if user_input.lower() == 'q':
                print('System stoped….')
                break
    
    except Exception as e:
        print(f'오류 발생: {e}')
    finally:
        # 프로세스 종료
        process1.terminate()
        process2.terminate()
        process3.terminate()
        
        process1.join()
        process2.join()
        process3.join()
        
        print('멀티프로세스 실행 완료')


def test_dummy_sensor():
    """더미 센서 테스트"""
    print('=== 더미 센서 테스트 ===')
    
    ds = DummySensor()
    ds.set_env()
    env_data = ds.get_env()
    
    print('센서 데이터:')
    print(json.dumps(env_data, indent=2, ensure_ascii=False))


def main():
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    
    print('=== Mars Mission Computer System ===')
    print('1. 더미 센서 테스트')
    print('2. 싱글 스레드 실행')
    print('3. 멀티 스레드 실행')
    print('4. 멀티 프로세스 실행')
    print('5. 종료')
    
    while True:
        try:
            choice = input('\n선택하세요 (1-5): ').strip()
            
            if choice == '1':
                test_dummy_sensor()
                
            elif choice == '2':
                RunComputer = MissionComputer()
                print('싱글 스레드 모드 - q로 종료 또는 Ctrl+C')
                
                # 시스템 정보 및 부하 지속 출력 (20초마다 반복)
                print('시스템 정보 및 부하 모니터링 시작 (20초마다 반복, q 또는 Ctrl+C로 종료)')
                
                # q 입력 감지를 위한 백그라운드 입력 스레드
                def _single_input_listener():
                    try:
                        while RunComputer.running:
                            user_input = input('시스템을 중지하려면 "q" 입력: ')
                            if user_input.lower() == 'q':
                                RunComputer.stop_system()
                                break
                    except Exception as e:
                        print(f'오류 발생: {e}')

                threading.Thread(target=_single_input_listener, daemon=True).start()
                
                # 시스템 정보 및 부하를 별도 스레드로 실행
                def _system_monitor():
                    try:
                        while RunComputer.running:
                            # 시스템 정보 출력
                            if RunComputer.settings.get('show_system_info', True):
                                system_info = {
                                    'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    'system_info': {
                                        'operating_system': platform.system(),
                                        'os_version': platform.version(),
                                        'cpu_type': platform.processor() or platform.machine(),
                                        'cpu_cores': os.cpu_count(),
                                        'memory_size_gb': round(psutil.virtual_memory().total / (1024**3), 2)
                                    }
                                }
                                print(f'[시스템 정보] {json.dumps(system_info, indent=2, ensure_ascii=False)}')
                            
                            time.sleep(RunComputer.settings.get('system_interval', 20))
                    except Exception as e:
                        print(f'시스템 정보 모니터링 오류: {e}')
                
                def _load_monitor():
                    try:
                        while RunComputer.running:
                            # 시스템 부하 출력
                            if RunComputer.settings.get('show_load_info', True):
                                load_info = {
                                    'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    'load_info': {
                                        'cpu_usage_percent': round(psutil.cpu_percent(interval=1), 2),
                                        'memory_usage_percent': round(psutil.virtual_memory().percent, 2),
                                        'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2)
                                    }
                                }
                                print(f'[시스템 부하] {json.dumps(load_info, indent=2, ensure_ascii=False)}')
                            
                            time.sleep(RunComputer.settings.get('system_interval', 20))
                    except Exception as e:
                        print(f'시스템 부하 모니터링 오류: {e}')
                
                # 시스템 모니터링 스레드 시작
                threading.Thread(target=_system_monitor, daemon=True).start()
                threading.Thread(target=_load_monitor, daemon=True).start()
                
                # 센서 데이터 지속 출력 (5초마다 반복)
                print('센서 데이터 모니터링 시작 (5초마다 반복)')
                try:
                    while RunComputer.running:
                        # 센서 값 가져오기
                        RunComputer.ds.set_env()
                        RunComputer.env_values = RunComputer.ds.get_env()
                        
                        # 히스토리 저장 (5분 평균용)
                        RunComputer.env_history.append({
                            'timestamp': time.time(),
                            'data': RunComputer.env_values.copy()
                        })
                        
                        # JSON 형태로 출력
                        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        output_data = {
                            'timestamp': timestamp,
                            'sensor_data': RunComputer.env_values
                        }
                        
                        if RunComputer.settings.get('show_sensor_data', True):
                            print(f'[센서 데이터] {json.dumps(output_data, indent=2, ensure_ascii=False)}')
                        
                        # 5분 평균 계산 (보너스)
                        current_time = time.time()
                        if current_time - RunComputer.last_average_time >= 20:  # 5분 = 300초
                            RunComputer.calculate_5min_average()
                            RunComputer.last_average_time = current_time
                        
                        time.sleep(RunComputer.settings.get('sensor_interval', 5))
                        
                except KeyboardInterrupt:
                    print('\nCtrl+C로 프로그램을 종료합니다.')
                    RunComputer.stop_system()
                except Exception as e:
                    print(f'센서 데이터 오류: {e}')
                    RunComputer.stop_system()
                
            elif choice == '3':
                run_multithread()
                
            elif choice == '4':
                run_multiprocess()
                
            elif choice == '5':
                print('프로그램을 종료합니다.')
                break
                
            else:
                print('올바른 선택지를 입력하세요.')
                
        except Exception as e:
            print(f'오류 발생: {e}')


if __name__ == '__main__':
    # 멀티프로세싱을 위한 설정
    multiprocessing.freeze_support()
    main()
