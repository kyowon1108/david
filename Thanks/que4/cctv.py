import os
import zipfile
import glob
from typing import List, Optional, Tuple
import cv2
import numpy as np


class MasImageHelper:
    """이미지 처리를 위한 헬퍼 클래스"""
    
    def __init__(self, image_path: str):
        """
        이미지 헬퍼 초기화
        
        Args:
            image_path: 이미지 파일 경로
        """
        self.image_path = image_path
        self.image = None
        self.original_image = None
        self.load_image()
    
    def load_image(self) -> bool:
        """
        이미지 로드
        
        Returns:
            로드 성공 여부
        """
        try:
            self.image = cv2.imread(self.image_path)
            if self.image is not None:
                self.original_image = self.image.copy()
                return True
            else:
                print(f'이미지 로드 실패: {self.image_path}')
                return False
        except Exception as e:
            print(f'이미지 로드 실패: {e}')
            return False
    
    def display_image(self, window_name: str = 'CCTV Image') -> None:
        """
        이미지 화면에 표시
        
        Args:
            window_name: 윈도우 이름
        """
        if self.image is not None:
            # 이미지 크기 조정 (너무 크면 화면에 맞게 축소)
            h, w = self.image.shape[:2]
            max_height = 800
            max_width = 1200
            
            if h > max_height or w > max_width:
                scale = min(max_width / w, max_height / h)
                new_w = int(w * scale)
                new_h = int(h * scale)
                display_image = cv2.resize(self.image, (new_w, new_h))
            else:
                display_image = self.image
            
            # 윈도우 생성 및 이미지 표시
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.imshow(window_name, display_image)
        else:
            print('표시할 이미지가 없습니다.')
    
    def preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """
        이미지 전처리
        
        Args:
            img: 입력 이미지
            
        Returns:
            전처리된 이미지
        """
        # 노이즈 제거 (적절한 필터링)
        denoised = cv2.bilateralFilter(img, 9, 75, 75)
        
        # 대비 향상 (CLAHE 사용)
        try:
            lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        except Exception:
            enhanced = denoised
        
        return enhanced
    
    def detect_people_hog(self, img: np.ndarray) -> Tuple[List[List[int]], List[float]]:
        """
        HOG를 사용한 사람 감지
        
        Args:
            img: 입력 이미지
            
        Returns:
            바운딩 박스와 신뢰도 점수
        """
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        
        boxes = []
        scores = []
        
        # 적절한 스케일에서 감지 수행 (과도한 감지 방지)
        scales = [0.8, 1.0, 1.2]
        
        for scale in scales:
            if scale != 1.0:
                h, w = img.shape[:2]
                scaled_img = cv2.resize(img, (int(w * scale), int(h * scale)))
            else:
                scaled_img = img
            
            try:
                # 적절한 파라미터로 감지 (오탐 방지)
                rects, weights = hog.detectMultiScale(
                    scaled_img,
                    winStride=(4, 4),  # 적절한 스트라이드
                    padding=(8, 8),    # 적절한 패딩
                    scale=1.05         # 적절한 스케일
                )
                
                if len(rects) > 0:
                    # 스케일 복원
                    for i, (x, y, w, h) in enumerate(rects):
                        if scale != 1.0:
                            x = int(x / scale)
                            y = int(y / scale)
                            w = int(w / scale)
                            h = int(h / scale)
                        
                        boxes.append([x, y, w, h])
                        
                        # weights가 있으면 사용, 없으면 기본값
                        if i < len(weights):
                            # HOG 감지 결과는 적절한 신뢰도 부여
                            scores.append(float(weights[i]) * 1.0)
                        else:
                            scores.append(1.0)
                            
            except Exception as e:
                print(f'HOG 감지 중 오류 (scale {scale}): {e}')
                continue
        
        return boxes, scores
    
    def detect_people_cascade(self, img: np.ndarray) -> Tuple[List[List[int]], List[float]]:
        """
        Haar Cascade를 사용한 사람 감지
        
        Args:
            img: 입력 이미지
            
        Returns:
            바운딩 박스와 신뢰도 점수
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        boxes = []
        scores = []
        
        # 다양한 cascade 파일 시도
        cascade_files = [
            'haarcascade_fullbody.xml',
            'haarcascade_upperbody.xml'
        ]
        
        for cascade_file in cascade_files:
            try:
                cascade_path = os.path.join(cv2.data.haarcascades, cascade_file)
                if not os.path.exists(cascade_path):
                    continue
                
                cascade = cv2.CascadeClassifier(cascade_path)
                if cascade.empty():
                    continue
                
                # 적절한 파라미터로 감지 시도 (오탐 방지)
                params = [
                    {'scaleFactor': 1.05, 'minNeighbors': 4, 'minSize': (30, 30)},
                    {'scaleFactor': 1.1, 'minNeighbors': 5, 'minSize': (40, 40)},
                    {'scaleFactor': 1.15, 'minNeighbors': 4, 'minSize': (50, 50)},
                    {'scaleFactor': 1.2, 'minNeighbors': 3, 'minSize': (60, 60)}
                ]
                
                for param in params:
                    rects = cascade.detectMultiScale(gray, **param)
                    
                    for (x, y, w, h) in rects:
                        boxes.append([x, y, w, h])
                        # Cascade 감지 결과는 적절한 신뢰도
                        scores.append(0.8 if 'fullbody' in cascade_file else 0.6)
                        
            except Exception as e:
                print(f'Cascade 감지 중 오류 ({cascade_file}): {e}')
                continue
        
        return boxes, scores
    
    def compute_iou(self, box1: List[int], box2: List[int]) -> float:
        """IoU (Intersection over Union) 계산"""
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        
        # 교집합 영역 계산
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        if x_right <= x_left or y_bottom <= y_top:
            return 0.0
        
        intersection = (x_right - x_left) * (y_bottom - y_top)
        union = w1 * h1 + w2 * h2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def non_max_suppression(self, boxes: List[List[int]], scores: List[float], 
                          iou_threshold: float = 0.3) -> List[List[int]]:
        """Non-Maximum Suppression을 사용한 중복 제거"""
        if not boxes:
            return []
        
        # 점수를 기준으로 정렬
        indices = sorted(range(len(boxes)), key=lambda i: scores[i], reverse=True)
        
        keep = []
        while indices:
            current = indices.pop(0)
            keep.append(boxes[current])
            
            # 현재 박스와 IoU가 임계값보다 높은 박스들 제거
            indices = [i for i in indices 
                      if self.compute_iou(boxes[current], boxes[i]) <= iou_threshold]
        
        return keep
    
    def filter_boxes(self, boxes: List[List[int]]) -> List[List[int]]:
        """
        부적절한 크기의 박스 필터링
        
        Args:
            boxes: 바운딩 박스 리스트
            
        Returns:
            필터링된 박스 리스트
        """
        if not boxes or self.image is None:
            return boxes
        
        img_h, img_w = self.image.shape[:2]
        filtered = []
        
        for box in boxes:
            x, y, w, h = box
            
            # 크기 필터링 (강화된 기준 - 오탐 방지)
            if w < 25 or h < 35:  # 적절한 크기 이상만 허용
                continue
            if w > img_w * 0.7 or h > img_h * 0.7:  # 적절한 크기 이하만 허용
                continue
            
            # 비율 필터링 (강화된 기준 - 사람 비율에 맞게)
            ratio = h / w if w > 0 else 0
            if ratio < 1.5 or ratio > 3.5:  # 사람의 일반적인 비율 범위
                continue
            
            # 경계 확인
            if x < 0 or y < 0 or x + w > img_w or y + h > img_h:
                continue
            
            filtered.append(box)
        
        return filtered
    
    def detect_people(self) -> List[List[int]]:
        """
        향상된 사람 감지 기능
        
        Returns:
            바운딩 박스 리스트 [(x, y, w, h), ...]
        """
        if self.image is None:
            return []
        
        print(f"이미지 처리 중: {os.path.basename(self.image_path)}")
        
        # 이미지 전처리
        preprocessed = self.preprocess_image(self.image)
        
        # HOG 감지
        hog_boxes, hog_scores = self.detect_people_hog(preprocessed)
        print(f"HOG 감지: {len(hog_boxes)}개")
        
        # Cascade 감지
        cascade_boxes, cascade_scores = self.detect_people_cascade(preprocessed)
        print(f"Cascade 감지: {len(cascade_boxes)}개")
        
        # 결과 합치기
        all_boxes = hog_boxes + cascade_boxes
        all_scores = hog_scores + cascade_scores
        
        if not all_boxes:
            return []
        
        # 크기 필터링
        filtered_boxes = self.filter_boxes(all_boxes)
        filtered_scores = [all_scores[i] for i, box in enumerate(all_boxes) 
                          if box in filtered_boxes]
        
        print(f"필터링 후: {len(filtered_boxes)}개")
        
        # NMS 적용
        final_boxes = self.non_max_suppression(filtered_boxes, filtered_scores)
        print(f"NMS 후 최종: {len(final_boxes)}개")
        
        return final_boxes
    
    def draw_people_boxes(self, boxes: List[List[int]]) -> None:
        """
        감지된 사람들을 빨간색 사각형으로 표시
        
        Args:
            boxes: 바운딩 박스 리스트
        """
        if self.image is None or self.original_image is None:
            return
        
        # 원본 이미지에서 시작
        self.image = self.original_image.copy()
        
        for i, (x, y, w, h) in enumerate(boxes):
            # 바운딩 박스 그리기
            cv2.rectangle(self.image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            
            # 번호 표시
            cv2.putText(self.image, f'Person {i+1}', (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)


class CCTVViewer:
    """CCTV 이미지 뷰어 클래스"""
    
    def __init__(self, zip_path: str = 'CCTV.zip'):
        """
        CCTV 뷰어 초기화
        
        Args:
            zip_path: CCTV.zip 파일 경로
        """
        self.zip_path = zip_path
        self.extract_path = 'CCTV'
        self.image_files = []
        self.current_index = 0
        self.window_name = 'CCTV Image Viewer'
        
        # 압축 해제 및 이미지 파일 목록 생성
        self.extract_zip()
        self.load_image_list()
    
    def extract_zip(self) -> None:
        """CCTV.zip 파일 압축 해제"""
        try:
            if not os.path.exists(self.zip_path):
                print(f'경고: {self.zip_path} 파일을 찾을 수 없습니다.')
                print('테스트를 위해 빈 CCTV 폴더를 생성합니다.')
                os.makedirs(self.extract_path, exist_ok=True)
                return
            
            print(f'{self.zip_path} 압축 해제 중...')
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.extract_path)
            print(f'{self.zip_path} 압축 해제 완료')
        except Exception as e:
            print(f'압축 해제 실패: {e}')
            os.makedirs(self.extract_path, exist_ok=True)
    
    def load_image_list(self) -> None:
        """이미지 파일 목록 로드"""
        if not os.path.exists(self.extract_path):
            print(f'CCTV 폴더가 존재하지 않습니다: {self.extract_path}')
            return
        
        # 지원하는 이미지 확장자
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif']
        
        for ext in image_extensions:
            # 소문자 확장자
            pattern = os.path.join(self.extract_path, '**', ext)
            self.image_files.extend(glob.glob(pattern, recursive=True))
            # 대문자 확장자
            pattern = os.path.join(self.extract_path, '**', ext.upper())
            self.image_files.extend(glob.glob(pattern, recursive=True))
        
        # 중복 제거 및 정렬
        self.image_files = sorted(list(set(self.image_files)))
        print(f'총 {len(self.image_files)}개의 이미지 파일을 찾았습니다.')
        
        # 처음 몇 개 파일 이름 출력
        if self.image_files:
            print('발견된 이미지 파일:')
            for i, img_file in enumerate(self.image_files[:5]):
                print(f'  {i+1}. {os.path.basename(img_file)}')
            if len(self.image_files) > 5:
                print(f'  ... 외 {len(self.image_files)-5}개')
    
    def display_current_image(self) -> None:
        """현재 이미지 표시"""
        if not self.image_files:
            print('표시할 이미지가 없습니다.')
            return
        
        if 0 <= self.current_index < len(self.image_files):
            image_path = self.image_files[self.current_index]
            print(f'\n현재 이미지: {os.path.basename(image_path)} ({self.current_index + 1}/{len(self.image_files)})')
            
            image_helper = MasImageHelper(image_path)
            if image_helper.image is not None:
                image_helper.display_image(self.window_name)
                cv2.waitKey(100)  # 화면 업데이트 대기
            else:
                print('이미지 로드에 실패했습니다.')
        else:
            print('유효하지 않은 이미지 인덱스입니다.')
    
    def next_image(self) -> None:
        """다음 이미지로 이동"""
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.display_current_image()
        else:
            print('마지막 이미지입니다.')
    
    def previous_image(self) -> None:
        """이전 이미지로 이동"""
        if self.current_index > 0:
            self.current_index -= 1
            self.display_current_image()
        else:
            print('첫 번째 이미지입니다.')
    
    def run_viewer(self) -> None:
        """이미지 뷰어 실행 (문제 1)"""
        if not self.image_files:
            print('표시할 이미지가 없습니다.')
            return
        
        print('\n=== CCTV 이미지 뷰어 시작 ===')
        print('조작법:')
        print('  ← 또는 A: 이전 이미지')
        print('  → 또는 D: 다음 이미지') 
        print('  ESC 또는 Q: 종료')
        print('  P: 사람 검색 모드로 전환')
        print('  (방향키도 지원됩니다)')
        
        self.display_current_image()
        
        while True:
            key = cv2.waitKey(0) & 0xFF
            
            if key == 27 or key == ord('q') or key == ord('Q'):  # ESC 또는 q
                break
            elif key == 83 or key == ord('d') or key == ord('D') or key == 3:  # → 또는 d 또는 오른쪽 방향키
                self.next_image()
            elif key == 81 or key == ord('a') or key == ord('A') or key == 2:  # ← 또는 a 또는 왼쪽 방향키
                self.previous_image()
            elif key == ord('p') or key == ord('P'):  # 사람 검색 모드
                cv2.destroyAllWindows()
                self.search_people()
                if self.image_files:  # 검색 후 뷰어로 복귀
                    self.display_current_image()
        
        cv2.destroyAllWindows()
    
    def search_people(self) -> None:
        """사람 검색 기능 (문제 2)"""
        if not self.image_files:
            print('검색할 이미지가 없습니다.')
            return
        
        print('\n=== 사람 검색 모드 시작 ===')
        print('조작법:')
        print('  ENTER: 다음 이미지')
        print('  SPACE: 사람이 감지된 이미지만 보기 모드 토글')
        print('  ESC: 검색 종료')
        
        people_found_images = []
        show_all = True  # True: 모든 이미지, False: 사람이 있는 이미지만
        
        i = 0
        while i < len(self.image_files):
            image_path = self.image_files[i]
            print(f'\n검색 중: {os.path.basename(image_path)} ({i + 1}/{len(self.image_files)})')
            
            image_helper = MasImageHelper(image_path)
            if image_helper.image is None:
                print('이미지 로드 실패, 다음 이미지로 이동...')
                i += 1
                continue
            
            people_boxes = image_helper.detect_people()
            
            if people_boxes:
                print(f'✓ 사람 {len(people_boxes)}명 감지됨!')
                people_found_images.append((i, image_path, len(people_boxes)))
                image_helper.draw_people_boxes(people_boxes)
                image_helper.display_image(self.window_name)
                
                # 창 제목 업데이트
                title = f'CCTV - {os.path.basename(image_path)} - {len(people_boxes)}명 감지'
                cv2.setWindowTitle(self.window_name, title)
            else:
                print('사람이 감지되지 않았습니다.')
                if show_all:
                    image_helper.display_image(self.window_name)
                    cv2.setWindowTitle(self.window_name, 
                                     f'CCTV - {os.path.basename(image_path)} - 감지 없음')
            
            # 사람이 있거나 모든 이미지를 보는 모드일 때만 대기
            if people_boxes or show_all:
                while True:
                    key = cv2.waitKey(0) & 0xFF
                    if key == 13:  # ENTER
                        i += 1
                        break
                    elif key == 32:  # SPACE
                        show_all = not show_all
                        mode = "모든 이미지" if show_all else "감지된 이미지만"
                        print(f'모드 변경: {mode}')
                        break
                    elif key == 27:  # ESC
                        cv2.destroyAllWindows()
                        print('\n검색이 중단되었습니다.')
                        self._show_search_summary(people_found_images)
                        return
            else:
                i += 1
        
        print('\n모든 이미지 검색이 완료되었습니다.')
        cv2.destroyAllWindows()
        self._show_search_summary(people_found_images)
    
    def _show_search_summary(self, people_found_images: List[Tuple[int, str, int]]) -> None:
        """검색 결과 요약 표시"""
        print('\n=== 검색 결과 요약 ===')
        if people_found_images:
            total_people = sum(count for _, _, count in people_found_images)
            print(f'사람이 감지된 이미지: {len(people_found_images)}개')
            print(f'총 감지된 사람 수: {total_people}명')
            print('\n상세 결과:')
            for idx, (img_idx, img_path, count) in enumerate(people_found_images, 1):
                print(f'  {idx}. {os.path.basename(img_path)} - {count}명')
        else:
            print('사람이 감지된 이미지가 없습니다.')


def main():
    """메인 함수"""
    print('CCTV 이미지 분석 시스템 시작')
    print('OpenCV 버전:', cv2.__version__)
    
    viewer = CCTVViewer()
    
    if not viewer.image_files:
        print('처리할 이미지가 없습니다. CCTV.zip 파일을 확인하세요.')
        return
    
    # 문제 1: 기본 뷰어 기능
    try:
        viewer.run_viewer()
    except KeyboardInterrupt:
        print('\n프로그램이 사용자에 의해 중단되었습니다.')
    except Exception as e:
        print(f'\n오류가 발생했습니다: {e}')
    finally:
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()