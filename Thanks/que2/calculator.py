import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, 
                             QPushButton, QVBoxLayout, QHBoxLayout, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class Calculator:
    """계산기 기능을 담당하는 클래스"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """계산기 초기화"""
        self.current_number = '0' # 화면에 표시되는 숫자
        self.previous_number = None # 연산자 입력 전의 숫자
        self.operator = None # 연산자
        self.new_number = True # 새로운 숫자 입력을 시작해야 하는지의 여부 (bool)
        self.has_decimal = False # 현재 숫자에 소수점이 있는지의 여부 (bool)
    
    def add_digit(self, digit):
        """숫자 추가"""
        if self.new_number: # 새로운 숫자 입력해야 하는 경우
            self.current_number = digit
            self.new_number = False
            self.has_decimal = False
        else:
            if self.current_number == '0':
                self.current_number = digit
            else:
                self.current_number += digit
    
    def add_decimal(self):
        """소수점 추가"""
        if not self.has_decimal:
            self.current_number += '.'
            self.has_decimal = True
            self.new_number = False
    
    def toggle_sign(self):
        """± 누르면 부호 변경"""
        if self.current_number != '0':
            if self.current_number.startswith('-'):
                self.current_number = self.current_number[1:]
            else:
                self.current_number = '-' + self.current_number
    
    def percent(self):
        """퍼센트 계산"""
        try:
            value = float(self.current_number)
            result = value / 100
            self.current_number = self.format_number(result)
        except ValueError:
            pass
    
    def set_operator(self, op):
        """연산자 설정"""
        if self.operator and not self.new_number:
            self.calculate()
        
        self.previous_number = float(self.current_number)
        self.operator = op
        self.new_number = True
        self.has_decimal = False
    
    def calculate(self):
        """계산 실행"""
        if self.operator and self.previous_number is not None:
            current = float(self.current_number)
            
            try:
                if self.operator == '+':
                    result = self.previous_number + current
                elif self.operator == '−':
                    result = self.previous_number - current
                elif self.operator == '×':
                    result = self.previous_number * current
                elif self.operator == '÷':
                    if current == 0: # 0으로 나누는 경우 에러 처리
                        self.current_number = 'Error'
                        return
                    result = self.previous_number / current
                
                self.current_number = self.format_number(result) # 결과 포맷팅
                self.operator = None # 연산자 초기화
                self.previous_number = None # 이전 숫자 초기화
                self.new_number = True # 새로운 숫자 입력 준비
                self.has_decimal = '.' in self.current_number # 소숫점 체크
                
            except (OverflowError, ValueError):
                self.current_number = 'Error'
    
    def format_number(self, number):
        """숫자 포맷팅 (소수점 6자리 이하 반올림)"""
        if isinstance(number, int):
            return str(number)
        
        # 소수점 6자리 이하 반올림
        rounded = round(number, 6)
        if rounded == int(rounded):
            return str(int(rounded))
        else:
            # 불필요한 0 제거
            return str(rounded).rstrip('0').rstrip('.')
    
    def get_display_text(self):
        """디스플레이에 표시할 텍스트 반환"""
        return self.current_number


class CalculatorUI(QMainWindow):
    """아이폰 계산기와 유사한 UI를 가진 계산기 제작"""
    
    def __init__(self):
        super().__init__()
        self.calculator = Calculator()
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle('계산기')
        self.setFixedSize(350, 500)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
        """)
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 디스플레이 영역
        self.display = QLabel('0')
        self.display.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.display.setStyleSheet("""
            QLabel {
                color: white;
                background-color: #000000;
                border: none;
                padding: 20px;
            }
        """)
        self.display.setFont(QFont('Arial', 48, QFont.Bold))
        main_layout.addWidget(self.display)
        
        # 버튼 그리드 레이아웃
        button_layout = QGridLayout()
        button_layout.setSpacing(10)
        
        # 버튼 텍스트 및 스타일 정의
        buttons = [
            ('AC', '#A5A5A5', '#000000'),
            ('±', '#A5A5A5', '#000000'),
            ('%', '#A5A5A5', '#000000'),
            ('÷', '#FF9500', '#FFFFFF'),
            ('7', '#333333', '#FFFFFF'),
            ('8', '#333333', '#FFFFFF'),
            ('9', '#333333', '#FFFFFF'),
            ('×', '#FF9500', '#FFFFFF'),
            ('4', '#333333', '#FFFFFF'),
            ('5', '#333333', '#FFFFFF'),
            ('6', '#333333', '#FFFFFF'),
            ('−', '#FF9500', '#FFFFFF'),
            ('1', '#333333', '#FFFFFF'),
            ('2', '#333333', '#FFFFFF'),
            ('3', '#333333', '#FFFFFF'),
            ('+', '#FF9500', '#FFFFFF'),
            ('🧮', '#333333', '#FFFFFF'),
            ('0', '#333333', '#FFFFFF'),
            ('.', '#333333', '#FFFFFF'),
            ('=', '#FF9500', '#FFFFFF')
        ]
        
        # 버튼 생성 및 배치
        row, col = 0, 0
        for button_info in buttons:
            text, bg_color, text_color = button_info
            button = self.create_button(text, bg_color, text_color)
            button_layout.addWidget(button, row, col)
            col += 1
            
            if col > 3:  # 3개마다 끊어서 버튼 넣기용
                col = 0
                row += 1
        
        main_layout.addLayout(button_layout)
        
    def create_button(self, text, bg_color, text_color):
        """버튼 생성 및 스타일 설정"""
        button = QPushButton(text)
        button.setFixedSize(70, 70)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 35px;
                font-size: 24px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: {self.lighten_color(bg_color)};
            }}
        """)
        
        # 버튼 클릭 이벤트 연결
        button.clicked.connect(lambda checked, t=text: self.button_clicked(t))
        
        return button
    
    def lighten_color(self, color):
        """색상을 밝게 만드는 헬퍼 함수"""
        if color == '#333333':
            return '#666666'
        elif color == '#A5A5A5':
            return '#CCCCCC'
        elif color == '#FF9500':
            return '#FFB84D'
        return color
    
    def button_clicked(self, text):
        """버튼 클릭 이벤트 처리"""
        if text.isdigit():
            self.calculator.add_digit(text)
        elif text == '.':
            self.calculator.add_decimal()
        elif text == 'AC':
            self.calculator.reset()
        elif text == '±':
            self.calculator.toggle_sign()
        elif text == '%':
            self.calculator.percent()
        elif text in ['+', '−', '×', '÷']:
            self.calculator.set_operator(text)
        elif text == '=':
            self.calculator.calculate()
        
        self.update_display()
    
    def update_display(self):
        """디스플레이 업데이트"""
        display_text = self.calculator.get_display_text()
        
        # 폰트 크기 자동 조정 (보너스 과제)
        font_size = self.adjust_font_size(display_text)
        self.display.setFont(QFont('Arial', font_size, QFont.Bold))
        
        self.display.setText(display_text)
    
    def adjust_font_size(self, text):
        """텍스트 길이에 따라 폰트 크기 조정 (보너스 과제)"""
        if len(text) <= 6:
            return 48
        elif len(text) <= 8:
            return 40
        elif len(text) <= 10:
            return 32
        elif len(text) <= 12:
            return 28
        else:
            return 24


def main():
    """메인 함수"""
    app = QApplication(sys.argv)
    calculator = CalculatorUI()
    calculator.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
