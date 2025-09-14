import os
import wave
import pyaudio
import speech_recognition as sr
import pandas as pd
from datetime import datetime
import glob
import re
import whisper


class JavisSystem:
    
    def __init__(self):
        """시스템 초기화"""
        self.records_dir = 'records'
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.chunk = 1024
        self.audio = pyaudio.PyAudio()
        self.recognizer = sr.Recognizer()
        
        # Whisper 모델 로드 (base 모델 사용)
        try:
            print("Whisper 모델 로딩 중...")
            self.whisper_model = whisper.load_model("base")
            print("Whisper 모델 로드 완료!")
        except Exception as e:
            print(f"Whisper 모델 로드 실패: {e}")
            self.whisper_model = None
        
        # records 폴더가 없으면 생성
        if not os.path.exists(self.records_dir):
            os.makedirs(self.records_dir)
            print(f'{self.records_dir} 폴더가 생성되었습니다.')
    
    def get_current_timestamp(self):
        """현재 날짜와 시간을 '년월일-시간분초' 형태로 반환"""
        now = datetime.now()
        return now.strftime('%Y%m%d-%H%M%S') # 년월일-시간분초 -> Ymd-HMS
    
    def list_microphones(self):
        """사용 가능한 마이크 목록을 출력"""
        print('\n=== 사용 가능한 마이크 목록 ===')
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:  # 입력 장치만 표시
                print(f'마이크 {i}: {device_info["name"]}')
        print()
    
    def record_audio(self, duration=5, device_index=None):
        """
        음성 녹음
        
        Args:
            duration (int): 녹음 시간 (초)
            device_index (int): 사용할 마이크 인덱스 (None이면 기본 마이크)
        
        Returns:
            str: 저장된 파일명
        """
        try:
            # 파일명 생성 (년월일-시간분초.wav)
            filename = f'{self.get_current_timestamp()}.wav'
            filepath = os.path.join(self.records_dir, filename)
            
            print(f'녹음을 시작합니다... ({duration}초)')
            print(f'저장될 파일: {filename}')
            
            # 오디오 스트림 설정
            stream = self.audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk
            )
            
            frames = []
            
            # 녹음 진행률 표시
            for i in range(0, int(self.rate / self.chunk * duration)):
                data = stream.read(self.chunk)
                frames.append(data)
                
                # 진행률 표시 (10%마다)
                if i % (int(self.rate / self.chunk * duration / 10)) == 0:
                    progress = (i / (self.rate / self.chunk * duration)) * 100
                    print(f'녹음 진행률: {progress:.0f}%')
            
            print('녹음 완료!')
            
            # 스트림 정리
            stream.stop_stream()
            stream.close()
            
            # WAV 파일로 저장
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.audio_format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(frames))
            
            print(f'파일이 저장되었습니다: {filepath}')
            return filename
            
        except Exception as e:
            print(f'녹음 중 오류가 발생했습니다: {e}')
            return None
    
    def get_audio_files(self, start_date=None, end_date=None):
        """
        records 폴더의 음성 파일 목록을 반환
        
        Args:
            start_date (str): 시작 날짜 (YYYYMMDD 형식)
            end_date (str): 종료 날짜 (YYYYMMDD 형식)
        
        Returns:
            list: 음성 파일 목록
        """
        pattern = os.path.join(self.records_dir, '*.wav')
        files = glob.glob(pattern)
        
        if start_date or end_date:
            filtered_files = []
            for file in files:
                # 파일명에서 날짜 추출 (YYYYMMDD-HHMMSS.wav)
                filename = os.path.basename(file)
                date_part = filename.split('-')[0]
                
                if start_date and date_part < start_date:
                    continue
                if end_date and date_part > end_date:
                    continue
                
                filtered_files.append(file)
            
            return filtered_files
        
        return files
    
    def speech_to_text(self, audio_file_path):
        """
        음성 파일을 텍스트로 변환
        
        Args:
            audio_file_path (str): 음성 파일 경로
        
        Returns:
            list: (시간, 텍스트) 튜플의 리스트
        """
        try:
            print(f'음성 인식 중: {os.path.basename(audio_file_path)}')
            
            # 음성 파일 로드 및 전처리
            with sr.AudioFile(audio_file_path) as source:
                # 배경 소음 조정
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.record(source)
            
            # 여러 음성 인식 엔진 시도 (Whisper -> Sphinx)
            engines = []
            
            # Whisper 우선 사용 (가장 정확함)
            if self.whisper_model:
                try:
                    segments = self._whisper_recognize(audio_file_path)
                    print(f'Whisper STT 성공: {len(segments)}개 세그먼트 인식')
                    return segments
                except Exception as e:
                    print(f'Whisper STT 실패: {e}')

            # 오프라인 대안으로 Sphinx 추가
            engines = [('Sphinx', lambda: self.recognizer.recognize_sphinx(audio))]

            for engine_name, recognize_func in engines:
                try:
                    text = recognize_func()
                    print(f'{engine_name} STT 성공: {text}')
                    return [(0, text)]
                except sr.RequestError as e:
                    print(f'{engine_name} STT 실패: {e}')
                    continue
                except sr.UnknownValueError:
                    print(f'{engine_name} STT: 음성을 인식할 수 없음')
                    continue
                except ImportError as e:
                    print(f'{engine_name} STT: 필요한 모듈이 설치되지 않음 ({e})')
                    continue
                except Exception as e:
                    print(f'{engine_name} STT: 예상치 못한 오류 ({e})')
                    continue
            
            # 모든 엔진이 실패한 경우 더미 텍스트 반환
            print('모든 STT 엔진 실패 - 기본 텍스트 반환')
            return [(0, f'[STT 실패] 파일: {os.path.basename(audio_file_path)}')]
            
        except sr.UnknownValueError:
            print('음성을 인식할 수 없습니다.')
            return [(0, '음성 인식 실패')]
        except Exception as e:
            print(f'음성 인식 중 오류 발생: {e}')
            return [(0, f'오류: {e}')]
    
    def _whisper_recognize(self, audio_file_path):
        """Whisper를 사용한 음성 인식"""
        try:
            result = self.whisper_model.transcribe(audio_file_path, language='ko')
            segments = []
            for segment in result['segments']:
                start_time = round(segment['start'], 2)
                text = segment['text'].strip()
                segments.append((start_time, text))
            return segments if segments else [(0, result["text"].strip())]
        except Exception as e:
            raise Exception(f"Whisper 인식 실패: {e}")
    
    def save_to_csv(self, audio_file_path, text_data):
        """
        인식된 텍스트를 CSV 파일로 저장
        
        Args:
            audio_file_path (str): 원본 음성 파일 경로
            text_data (list): (시간, 텍스트) 튜플의 리스트
        """
        try:
            # CSV 파일명 생성 (원본 파일명과 동일, 확장자만 .csv)
            base_name = os.path.splitext(os.path.basename(audio_file_path))[0]
            csv_filename = f'{base_name}.csv'
            csv_filepath = os.path.join(self.records_dir, csv_filename)
            
            # DataFrame 생성
            df = pd.DataFrame(text_data, columns=['시간(초)', '인식된_텍스트'])
            
            # CSV 파일로 저장
            df.to_csv(csv_filepath, index=False, encoding='utf-8-sig')
            
            print(f'CSV 파일이 저장되었습니다: {csv_filename}')
            return csv_filename
            
        except Exception as e:
            print(f'CSV 저장 중 오류 발생: {e}')
            return None
    
    def process_all_audio_files(self):
        """모든 음성 파일을 처리하여 CSV로 변환"""
        audio_files = self.get_audio_files()
        
        if not audio_files:
            print('처리할 음성 파일이 없습니다.')
            return
        
        print(f'총 {len(audio_files)}개의 음성 파일을 처리합니다.')
        
        for i, audio_file in enumerate(audio_files, 1):
            print(f'\n[{i}/{len(audio_files)}] 처리 중...')
            
            # 이미 CSV 파일이 있는지 확인
            base_name = os.path.splitext(os.path.basename(audio_file))[0]
            csv_file = os.path.join(self.records_dir, f'{base_name}.csv')
            
            if os.path.exists(csv_file):
                print(f'이미 처리된 파일입니다: {base_name}.csv')
                continue
            
            # 음성 인식 및 CSV 저장
            text_data = self.speech_to_text(audio_file)
            self.save_to_csv(audio_file, text_data)
    
    def search_keyword(self, keyword):
        """
        특정 키워드를 CSV 파일에서 검색
        
        Args:
            keyword (str): 검색할 키워드
        """
        csv_files = glob.glob(os.path.join(self.records_dir, '*.csv'))
        
        if not csv_files:
            print('검색할 CSV 파일이 없습니다.')
            return
        
        print(f'키워드 "{keyword}" 검색 결과:')
        print('=' * 50)
        
        found_count = 0
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file, encoding='utf-8-sig')
                
                # 키워드가 포함된 행 찾기
                matches = df[df['인식된_텍스트'].str.contains(keyword, case=False, na=False)]
                
                if not matches.empty:
                    print(f'\n파일: {os.path.basename(csv_file)}')
                    print('-' * 30)
                    
                    for _, row in matches.iterrows():
                        print(f'시간: {row["시간(초)"]}초')
                        print(f'텍스트: {row["인식된_텍스트"]}')
                        print()
                        found_count += 1
                        
            except Exception as e:
                print(f'파일 읽기 오류 ({os.path.basename(csv_file)}): {e}')
        
        if found_count == 0:
            print('검색 결과가 없습니다.')
        else:
            print(f'총 {found_count}개의 결과를 찾았습니다.')
    
    def show_date_range_files(self, start_date, end_date):
        """
        특정 날짜 범위의 녹음 파일을 보여줌
        
        Args:
            start_date (str): 시작 날짜 (YYYYMMDD 형식)
            end_date (str): 종료 날짜 (YYYYMMDD 형식)
        """
        files = self.get_audio_files(start_date, end_date)
        
        if not files:
            print(f'{start_date} ~ {end_date} 기간의 녹음 파일이 없습니다.')
            return
        
        print(f'{start_date} ~ {end_date} 기간의 녹음 파일 목록:')
        print('=' * 50)
        
        for i, file in enumerate(files, 1):
            filename = os.path.basename(file)
            file_size = os.path.getsize(file) / 1024  # KB
            print(f'{i}. {filename} ({file_size:.1f} KB)')
    
    def cleanup(self):
        """리소스 정리"""
        self.audio.terminate()


def main():
    """메인 함수"""
    javis = JavisSystem()
    
    try:
        while True:
            print('\n' + '=' * 50)
            print('JAVIS 시스템 - 음성 처리 및 문자 처리')
            print('=' * 50)
            print('1. 마이크 목록 보기')
            print('2. 음성 녹음')
            print('3. 모든 음성 파일 STT 처리')
            print('4. 특정 날짜 범위 파일 조회')
            print('5. 키워드 검색')
            print('6. 종료')
            print('=' * 50)
            
            choice = input('선택하세요 (1-6): ').strip()
            
            if choice == '1':
                javis.list_microphones()
                
            elif choice == '2':
                print('\n=== 음성 녹음 ===')
                duration = input('녹음 시간을 입력하세요 (초, 기본값: 5): ').strip()
                duration = int(duration) if duration.isdigit() else 5
                
                device_choice = input('마이크 인덱스를 입력하세요 (엔터: 기본 마이크): ').strip()
                device_index = int(device_choice) if device_choice.isdigit() else None
                
                javis.record_audio(duration, device_index)
                
            elif choice == '3':
                print('\n=== STT 처리 ===')
                javis.process_all_audio_files()
                
            elif choice == '4':
                print('\n=== 날짜 범위 파일 조회 ===')
                start_date = input('시작 날짜 (YYYYMMDD): ').strip()
                end_date = input('종료 날짜 (YYYYMMDD): ').strip()
                
                if start_date and end_date:
                    javis.show_date_range_files(start_date, end_date)
                else:
                    print('날짜 형식이 올바르지 않습니다.')
                    
            elif choice == '5':
                print('\n=== 키워드 검색 ===')
                keyword = input('검색할 키워드를 입력하세요: ').strip()
                if keyword:
                    javis.search_keyword(keyword)
                else:
                    print('키워드를 입력해주세요.')
                    
            elif choice == '6':
                print('JAVIS 시스템을 종료합니다.')
                break
                
            else:
                print('잘못된 선택입니다. 1-6 중에서 선택해주세요.')
                
    except KeyboardInterrupt:
        print('\n\n프로그램이 중단되었습니다.')
    finally:
        javis.cleanup()


if __name__ == '__main__':
    main()
