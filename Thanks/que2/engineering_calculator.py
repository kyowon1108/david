import sys
import math
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, 
                             QPushButton, QVBoxLayout, QHBoxLayout, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class Calculator:
    """기본 계산기 기능을 담당하는 클래스"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """계산기 초기화"""
        self.current_number = '0'
        self.previous_number = None
        self.operator = None
        self.new_number = True
        self.has_decimal = False
    
    def add_digit(self, digit):
        """숫자 추가"""
        if self.new_number:
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
        """부호 변경"""
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
                    if current == 0:
                        self.current_number = 'Error'
                        return
                    result = self.previous_number / current
                
                self.current_number = self.format_number(result)
                self.operator = None
                self.previous_number = None
                self.new_number = True
                self.has_decimal = '.' in self.current_number
                
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


class EngineeringCalculator(Calculator):
    """공학용 계산기 기능을 담당하는 클래스"""
    
    def __init__(self):
        super().__init__()
        self.memory = 0
        self.angle_mode = 'deg'  # deg 또는 rad
        self.second_mode = False  # 2nd 모드
    
    def reset(self):
        """공학용 계산기 초기화"""
        super().reset()
        self.memory = 0
        self.angle_mode = 'deg'
        self.second_mode = False
    
    def toggle_angle_mode(self):
        """각도 모드 변경 (deg ↔ rad)"""
        self.angle_mode = 'rad' if self.angle_mode == 'deg' else 'deg'
    
    def toggle_second_mode(self):
        """2nd 모드 토글"""
        self.second_mode = not self.second_mode
    
    def memory_clear(self):
        """메모리 초기화"""
        self.memory = 0
    
    def memory_add(self):
        """메모리에 현재 값 추가"""
        try:
            self.memory += float(self.current_number)
        except ValueError:
            pass
    
    def memory_subtract(self):
        """메모리에서 현재 값 빼기"""
        try:
            self.memory -= float(self.current_number)
        except ValueError:
            pass
    
    def memory_recall(self):
        """메모리 값 불러오기"""
        self.current_number = self.format_number(self.memory)
        self.new_number = True
        self.has_decimal = '.' in str(self.memory)
    
    def square(self):
        """x² 계산"""
        try:
            value = float(self.current_number)
            result = value ** 2
            self.current_number = self.format_number(result)
            self.new_number = True
            self.has_decimal = '.' in str(result)
        except (OverflowError, ValueError):
            self.current_number = 'Error'
    
    def cube(self):
        """x³ 계산"""
        try:
            value = float(self.current_number)
            result = value ** 3
            self.current_number = self.format_number(result)
            self.new_number = True
            self.has_decimal = '.' in str(result)
        except (OverflowError, ValueError):
            self.current_number = 'Error'
    
    def power(self, exponent):
        """xʸ 계산"""
        try:
            base = float(self.current_number)
            result = base ** exponent
            self.current_number = self.format_number(result)
            self.new_number = True
            self.has_decimal = '.' in str(result)
        except (OverflowError, ValueError):
            self.current_number = 'Error'
    
    def reciprocal(self):
        """1/x 계산"""
        try:
            value = float(self.current_number)
            if value == 0:
                self.current_number = 'Error'
                return
            result = 1 / value
            self.current_number = self.format_number(result)
            self.new_number = True
            self.has_decimal = '.' in str(result)
        except (OverflowError, ValueError):
            self.current_number = 'Error'
    
    def absolute(self):
        """|x| 계산"""
        try:
            value = float(self.current_number)
            result = abs(value)
            self.current_number = self.format_number(result)
            self.new_number = True
            self.has_decimal = '.' in str(result)
        except (OverflowError, ValueError):
            self.current_number = 'Error'
    
    def square_root(self):
        """√x 계산"""
        try:
            value = float(self.current_number)
            if value < 0:
                self.current_number = 'Error'
                return
            result = math.sqrt(value)
            self.current_number = self.format_number(result)
            self.new_number = True
            self.has_decimal = '.' in str(result)
        except (OverflowError, ValueError):
            self.current_number = 'Error'
    
    def factorial(self):
        """x! 계산"""
        try:
            value = int(float(self.current_number))
            if value < 0:
                self.current_number = 'Error'
                return
            if value > 170:  # Python에서 처리 가능한 팩토리얼 한계
                self.current_number = 'Error'
                return
            result = math.factorial(value)
            self.current_number = self.format_number(result)
            self.new_number = True
            self.has_decimal = '.' in str(result)
        except (OverflowError, ValueError):
            self.current_number = 'Error'
    
    def natural_log(self):
        """ln(x) 계산"""
        try:
            value = float(self.current_number)
            if value <= 0:
                self.current_number = 'Error'
                return
            result = math.log(value)
            self.current_number = self.format_number(result)
            self.new_number = True
            self.has_decimal = '.' in str(result)
        except (OverflowError, ValueError):
            self.current_number = 'Error'
    
    def log_base_10(self):
        """log₁₀(x) 계산"""
        try:
            value = float(self.current_number)
            if value <= 0:
                self.current_number = 'Error'
                return
            result = math.log10(value)
            self.current_number = self.format_number(result)
            self.new_number = True
            self.has_decimal = '.' in str(result)
        except (OverflowError, ValueError):
            self.current_number = 'Error'
    
    def exponential(self):
        """e^x 계산"""
        try:
            value = float(self.current_number)
            result = math.exp(value)
            self.current_number = self.format_number(result)
            self.new_number = True
            self.has_decimal = '.' in str(result)
        except (OverflowError, ValueError):
            self.current_number = 'Error'
    
    def sin(self):
        """sin(x) 계산"""
        try:
            value = float(self.current_number)
            if self.angle_mode == 'deg':
                value = math.radians(value)
            result = math.sin(value)
            self.current_number = self.format_number(result)
            self.new_number = True
            self.has_decimal = '.' in str(result)
        except (OverflowError, ValueError):
            self.current_number = 'Error'
    
    def cos(self):
        """cos(x) 계산"""
        try:
            value = float(self.current_number)
            if self.angle_mode == 'deg':
                value = math.radians(value)
            result = math.cos(value)
            self.current_number = self.format_number(result)
            self.new_number = True
            self.has_decimal = '.' in str(result)
        except (OverflowError, ValueError):
            self.current_number = 'Error'
    
    def tan(self):
        """tan(x) 계산"""
        try:
            value = float(self.current_number)
            if self.angle_mode == 'deg':
                value = math.radians(value)
            result = math.tan(value)
            self.current_number = self.format_number(result)
            self.new_number = True
            self.has_decimal = '.' in str(result)
        except (OverflowError, ValueError):
            self.current_number = 'Error'
    
    def sinh(self):
        """sinh(x) 계산"""
        try:
            value = float(self.current_number)
            result = math.sinh(value)
            self.current_number = self.format_number(result)
            self.new_number = True
            self.has_decimal = '.' in str(result)
        except (OverflowError, ValueError):
            self.current_number = 'Error'
    
    def cosh(self):
        """cosh(x) 계산"""
        try:
            value = float(self.current_number)
            result = math.cosh(value)
            self.current_number = self.format_number(result)
            self.new_number = True
            self.has_decimal = '.' in str(result)
        except (OverflowError, ValueError):
            self.current_number = 'Error'
    
    def tanh(self):
        """tanh(x) 계산"""
        try:
            value = float(self.current_number)
            result = math.tanh(value)
            self.current_number = self.format_number(result)
            self.new_number = True
            self.has_decimal = '.' in str(result)
        except (OverflowError, ValueError):
            self.current_number = 'Error'
    
    def set_pi(self):
        """π 값 설정"""
        self.current_number = self.format_number(math.pi)
        self.new_number = True
        self.has_decimal = True
    
    def set_e(self):
        """e 값 설정"""
        self.current_number = self.format_number(math.e)
        self.new_number = True
        self.has_decimal = True
    
    def random_number(self):
        """랜덤 숫자 생성"""
        import random
        result = random.random()
        self.current_number = self.format_number(result)
        self.new_number = True
        self.has_decimal = True


class EngineeringCalculatorUI(QMainWindow):
    """아이폰 공학용 계산기와 유사한 UI를 가진 공학용 계산기"""
    
    def __init__(self):
        super().__init__()
        self.calculator = EngineeringCalculator()
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle('공학용 계산기')
        self.setFixedSize(800, 600)
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
        self.display.setFont(QFont('Arial', 36, QFont.Bold))
        main_layout.addWidget(self.display)
        
        # 공학용 계산기 버튼 레이아웃
        self.create_engineering_buttons(main_layout)
        
    def create_engineering_buttons(self, main_layout):
        """공학용 계산기 버튼 생성 - 5행 10열 격자 형태"""
        
        # 그리드 레이아웃 사용
        button_grid = QGridLayout()
        button_grid.setSpacing(8)
        
        # 버튼 정의 (5행 10열)
        buttons = [
            # 첫 번째 행: (, ), mc, m+, m-, mr, AC, +/-, %, ÷
            [('(', '#333333', '#FFFFFF'), (')', '#333333', '#FFFFFF'),
             ('mc', '#333333', '#FFFFFF'), ('m+', '#333333', '#FFFFFF'),
             ('m-', '#333333', '#FFFFFF'), ('mr', '#333333', '#FFFFFF'),
             ('AC', '#A5A5A5', '#000000'), ('±', '#A5A5A5', '#000000'),
             ('%', '#A5A5A5', '#000000'), ('÷', '#FF9500', '#FFFFFF')],
            
            # 두 번째 행: 2nd, x², x³, xʸ, eˣ, 10ˣ, 7, 8, 9, ×
            [('2nd', '#333333', '#FFFFFF'), ('x²', '#333333', '#FFFFFF'),
             ('x³', '#333333', '#FFFFFF'), ('xʸ', '#333333', '#FFFFFF'),
             ('eˣ', '#333333', '#FFFFFF'), ('10ˣ', '#333333', '#FFFFFF'),
             ('7', '#333333', '#FFFFFF'), ('8', '#333333', '#FFFFFF'),
             ('9', '#333333', '#FFFFFF'), ('×', '#FF9500', '#FFFFFF')],
            
            # 세 번째 행: 1/x, ²√x, ³√x, ʸ√x, ln, log₁₀, 4, 5, 6, −
            [('1/x', '#333333', '#FFFFFF'), ('²√x', '#333333', '#FFFFFF'),
             ('³√x', '#333333', '#FFFFFF'), ('ʸ√x', '#333333', '#FFFFFF'),
             ('ln', '#333333', '#FFFFFF'), ('log₁₀', '#333333', '#FFFFFF'),
             ('4', '#333333', '#FFFFFF'), ('5', '#333333', '#FFFFFF'),
             ('6', '#333333', '#FFFFFF'), ('−', '#FF9500', '#FFFFFF')],
            
            # 네 번째 행: x!, sin, cos, tan, e, EE, 1, 2, 3, +
            [('x!', '#333333', '#FFFFFF'), ('sin', '#333333', '#FFFFFF'),
             ('cos', '#333333', '#FFFFFF'), ('tan', '#333333', '#FFFFFF'),
             ('e', '#333333', '#FFFFFF'), ('EE', '#333333', '#FFFFFF'),
             ('1', '#333333', '#FFFFFF'), ('2', '#333333', '#FFFFFF'),
             ('3', '#333333', '#FFFFFF'), ('+', '#FF9500', '#FFFFFF')],
            
            # 다섯 번째 행: Rad, sinh, cosh, tanh, π, Rand, 0 (2칸), ., =
            [('Rad', '#333333', '#FFFFFF'), ('sinh', '#333333', '#FFFFFF'),
             ('cosh', '#333333', '#FFFFFF'), ('tanh', '#333333', '#FFFFFF'),
             ('π', '#333333', '#FFFFFF'), ('Rand', '#333333', '#FFFFFF'),
             ('0', '#333333', '#FFFFFF', 2), ('', '#000000', '#000000'),
             ('.', '#333333', '#FFFFFF'), ('=', '#FF9500', '#FFFFFF')]
        ]
        
        # 버튼을 그리드에 배치
        for row_idx, row_buttons in enumerate(buttons):
            for col_idx, button_info in enumerate(row_buttons):
                if button_info[0]:  # 빈 공간이 아닌 경우에만 버튼 생성
                    if len(button_info) == 4:  # 0 버튼 (2칸 차지)
                        text, bg_color, text_color, colspan = button_info
                        button = self.create_small_button(text, bg_color, text_color)
                        # 0 버튼은 실제 크기도 2배로 설정
                        if text == '0':
                            button.setFixedSize(140, 50)  # 가로 2배 크기
                        button_grid.addWidget(button, row_idx, col_idx, 1, colspan)
                    else:
                        text, bg_color, text_color = button_info
                        button = self.create_small_button(text, bg_color, text_color)
                        button_grid.addWidget(button, row_idx, col_idx)
        
        main_layout.addLayout(button_grid)
        
    def create_small_button(self, text, bg_color, text_color):
        """작은 크기의 버튼 생성"""
        button = QPushButton(text)
        button.setFixedSize(60, 50)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 8px;
                font-size: 14px;
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
        elif text == '2nd':
            self.calculator.toggle_second_mode()
        elif text == 'Rad':
            self.calculator.toggle_angle_mode()
        elif text == 'mc':
            self.calculator.memory_clear()
        elif text == 'm+':
            self.calculator.memory_add()
        elif text == 'm-':
            self.calculator.memory_subtract()
        elif text == 'mr':
            self.calculator.memory_recall()
        elif text == 'x²':
            self.calculator.square()
        elif text == 'x³':
            self.calculator.cube()
        elif text == '1/x':
            self.calculator.reciprocal()
        elif text == '²√x':
            self.calculator.square_root()
        elif text == 'x!':
            self.calculator.factorial()
        elif text == 'ln':
            self.calculator.natural_log()
        elif text == 'log₁₀':
            self.calculator.log_base_10()
        elif text == 'eˣ':
            self.calculator.exponential()
        elif text == 'sin':
            self.calculator.sin()
        elif text == 'cos':
            self.calculator.cos()
        elif text == 'tan':
            self.calculator.tan()
        elif text == 'sinh':
            self.calculator.sinh()
        elif text == 'cosh':
            self.calculator.cosh()
        elif text == 'tanh':
            self.calculator.tanh()
        elif text == 'π':
            self.calculator.set_pi()
        elif text == 'e':
            self.calculator.set_e()
        elif text == 'Rand':
            self.calculator.random_number()
        elif text in ['(', ')']:
            # 괄호 처리 (현재는 기본 구현)
            self.handle_other_engineering_function(text)
        else:
            # 기타 공학용 함수들 (xʸ, 10ˣ, ³√x, ʸ√x, EE 등)
            self.handle_other_engineering_function(text)
        
        self.update_display()
    
    def handle_other_engineering_function(self, function):
        """기타 공학용 함수 처리"""
        # 현재는 기본적인 함수들만 구현
        # 필요에 따라 추가 기능 구현 가능
        pass
    
    def update_display(self):
        """디스플레이 업데이트"""
        display_text = self.calculator.get_display_text()
        
        # 폰트 크기 자동 조정
        font_size = self.adjust_font_size(display_text)
        self.display.setFont(QFont('Arial', font_size, QFont.Bold))
        
        self.display.setText(display_text)
    
    def adjust_font_size(self, text):
        """텍스트 길이에 따라 폰트 크기 조정"""
        if len(text) <= 6:
            return 36
        elif len(text) <= 8:
            return 30
        elif len(text) <= 10:
            return 24
        elif len(text) <= 12:
            return 20
        else:
            return 16


def main():
    """메인 함수"""
    app = QApplication(sys.argv)
    calculator = EngineeringCalculatorUI()
    calculator.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
