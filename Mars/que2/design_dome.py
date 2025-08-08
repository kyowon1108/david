import math

# 전역 변수로 저장을 요구함
g_material = ''
g_diameter = 0.0
g_thickness = 0.0
g_area = 0.0
g_weight = 0.0

# 재질별 밀도 (g/cm³)
MATERIAL_DENSITY = {
    '유리': 2.4,
    'glass': 2.4,
    '알루미늄': 2.7,
    'aluminum': 2.7,
    '탄소강': 7.85,
    'carbon_steel': 7.85
}

def sphere_area(diameter, material, thickness=1.0):
    """반구체 돔의 표면적과 무게 계산"""
    global g_material, g_diameter, g_thickness, g_area, g_weight
    
    # 입력값 검증
    if diameter <= 0:
        raise ValueError('지름은 0보다 큰 값이어야 합니다.')
    
    if thickness <= 0:
        raise ValueError('두께는 0보다 큰 값이어야 합니다.')
    
    # 재질 검증 (한글과 영어 모두 지원)
    material_lower = material.lower()
    material_key = None
    
    for key in MATERIAL_DENSITY.keys():
        if key.lower() == material_lower or key == material:
            material_key = key
            break
    
    if material_key is None:
        raise KeyError(f'지원하지 않는 재질입니다: {material}. 지원하는 재질: 유리(glass), 알루미늄(aluminum), 탄소강(carbon_steel)')
    
    # 반구체 표면적 계산 (반구 = 구의 절반 + 바닥면)
    # 구의 표면적: 4πr², 반구 표면적: 2πr² + πr² = 3πr²
    radius = diameter / 2.0
    area = 3 * math.pi * (radius ** 2)
    
    # 부피 계산 (두께 적용)
    # 반구 껍질의 부피 ≈ 표면적 × 두께
    thickness_m = thickness / 100.0  # cm를 m로 변환
    volume_m3 = area * thickness_m
    
    # 부피를 cm³로 변환하여 밀도와 곱하기
    volume_cm3 = volume_m3 * 1000000  # m³를 cm³로 변환
    density = MATERIAL_DENSITY[material_key]
    weight_g = volume_cm3 * density
    weight_kg = weight_g / 1000.0  # g를 kg로 변환
    
    # 화성 중력 적용
    mars_weight_kg = weight_kg * 0.38
    
    # 전역 변수에 저장
    g_material = material
    g_diameter = diameter
    g_thickness = thickness
    g_area = area
    g_weight = mars_weight_kg
    
    return area, mars_weight_kg


def get_user_input():
    while True:
        try:
            # 지름 입력
            diameter_input = input('돔의 지름을 입력하세요 (m): ').strip()
            if diameter_input.lower() in ['quit', 'exit', 'q']:
                return None, None, None
            
            diameter = float(diameter_input)
            if diameter <= 0:
                print('지름은 0보다 큰 값이어야 합니다.')
                continue
            
            # 재질 입력
            print('재질을 선택하세요:')
            print('1. 유리 (glass)')
            print('2. 알루미늄 (aluminum)')
            print('3. 탄소강 (carbon_steel)')
            material_input = input('재질을 입력하세요: ').strip()
            
            if material_input.lower() in ['quit', 'exit', 'q']:
                return None, None, None
            
            # 재질 매핑
            material_map = {
                '1': '유리',
                '유리': '유리',
                'glass': '유리',
                '2': '알루미늄',
                '알루미늄': '알루미늄',
                'aluminum': '알루미늄',
                '3': '탄소강',
                '탄소강': '탄소강',
                'carbon_steel': '탄소강'
            } # 여러 방면으로 처리
            
            material = material_map.get(material_input.lower())
            if material is None:
                print('올바른 재질을 선택해주세요.')
                continue
            
            # 두께 입력 (선택사항)
            thickness_input = input('두께를 입력하세요 (cm, 기본값 1): ').strip()
            if thickness_input.lower() in ['quit', 'exit', 'q']:
                return None, None, None
            
            if thickness_input == '':
                thickness = 1.0
            else:
                thickness = float(thickness_input)
                if thickness <= 0:
                    print('두께는 0보다 큰 값이어야 합니다.')
                    continue
            
            return diameter, material, thickness
            
        except ValueError:
            print('올바른 숫자를 입력해주세요.')
        except KeyboardInterrupt:
            print('\n프로그램을 종료합니다.')
            return None, None, None


def display_result():
    print(f'재질 ⇒ {g_material}, 지름 ⇒ {g_diameter}, 두께 ⇒ {g_thickness}, 면적 ⇒ {g_area:.3f}, 무게 ⇒ {g_weight:.3f} kg')


def main():
    print('=== Mars 돔 구조물 설계 프로그램 ===')
    print('종료하려면 "quit", "exit", 또는 "q"를 입력하세요.\n')
    
    while True:
        try:
            # 사용자 입력 받기
            diameter, material, thickness = get_user_input()
            
            if diameter is None:  # 종료 조건
                print('프로그램을 종료합니다.')
                break
            
            # 돔 설계 계산
            area, weight = sphere_area(diameter, material, thickness)
            
            # 결과 출력
            print('\n=== 계산 결과 ===')
            display_result()
            print(f'표면적: {area:.3f} m²') # 소수점 3자리 자르기
            print(f'화성에서의 무게: {weight:.3f} kg')
            
        except ValueError as e:
            print(f'입력 오류: {e}')
        except KeyError as e:
            print(f'재질 오류: {e}')
        except Exception as e:
            print(f'예상치 못한 오류가 발생했습니다: {e}')


if __name__ == '__main__':
    main()

