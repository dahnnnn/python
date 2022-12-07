import pygame
from random import *
import time
import random

# 초기화
pygame.init()

# 가로, 세로 크기
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("[기말프로젝트] 기억력 테스트 게임")

# 시작 버튼
start_button = pygame.Rect(0, 0, 120, 120) # 가로 세로가 120인 사각형 버튼을 생성
start_button.center = (120, screen_height - 120)    # 해당 버튼의 중심점 좌표를 (120, 120)으로 설정
                                                    # x좌표는 0에서 120으로 해주면되고 y좌표는 전체 높이에서 120 뺀 값

# 색깔 
BLACK = (0, 0, 0)
WHITE = (255, 255, 255) 
GRAY = (50, 50, 50)
RED = (255, 0, 0)  
YELLOW = (255, 255, 0)

game_font = pygame.font.Font(None, 120) # 폰트 정의
large_font = pygame.font.SysFont('malgungothic', 72)
small_font = pygame.font.SysFont('malgungothic', 36)
score = 0
start_time = int(time.time()) 
remain_second = 90
penalty_second = 0
mole_game_over = False

# 배경 음악
pygame.mixer.init() # 초기화
pygame.mixer.music.load('bgm.mp3') # 배경 음악
pygame.mixer.music.play(-1) # -1: 무한 반복
whack_sound = pygame.mixer.Sound('whack.wav') # 사운드
game_over_sound = pygame.mixer.Sound('game_over.wav') # 사운드

######함수######

# 시작화면 보여주기
def display_start_screen():
    # 화면에 버튼을 그리는 데 하얀색이고 두께가 5인 반지름 60짜리의 원으로 그림.
    # 중심점은 이전에 설정한 시작버튼의 중심점 좌표를 사용함.
    pygame.draw.circle(screen, WHITE, start_button.center, 60, 5)

    msg = game_font.render(f'{curr_level}', True, WHITE)
    msg_rect = msg.get_rect(center=start_button.center)
    
    screen.blit(msg, msg_rect)

# 기억력 게임 화면 보여주기
def display_memory_game_screen():
    global hidden
    if not hidden:
        elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000 # ms -> sec 단위로 변경
        if elapsed_time > display_time:
            hidden = True

    for idx, rect in enumerate(number_buttons, start=1):
        if hidden: # 숨김처리
            # 버튼 사각형 그리기
            pygame.draw.rect(screen, WHITE, rect) # rect에는 center_x와 center_y의 정보가 있음. button_size의 정보도 있음.
        else:
            # 실제 숫자 텍스트
            cell_text = game_font.render(str(idx), True, WHITE)
            # 앞에서 가져온 버튼 rect의 center 값을 우리가 그릴 숫자 텍스트의 center 값으로 활용
            text_rect = cell_text.get_rect(center=rect.center)
            screen.blit(cell_text, text_rect)

# 두더지 게임 화면 보여주기     
def mole_game_screen():
    
    BONUS = game_font.render(f'Bonus Stage', True, WHITE)
    BONUS_rect = BONUS.get_rect(center=(screen_width/2, 100))
    screen.blit(BONUS, BONUS_rect)
    
    for mole, appear_time, disappear_time in moles:
        current_time = int(time.time())
        if  current_time >= appear_time:  
            screen.blit(mole_image, mole)

    score_image = small_font.render('점수 {}'.format(score), True, YELLOW)
    screen.blit(score_image, (10, 10))

    remain_second_image = small_font.render('남은 시간 {}'.format(remain_second), True, YELLOW)
    screen.blit(remain_second_image, remain_second_image.get_rect(right=screen_width - 10, top=10))

    if mole_game_over:
        game_over_image = large_font.render('게임 종료', True, RED)
        screen.blit(game_over_image, game_over_image.get_rect(centerx=screen_width // 2, centery=screen_height // 2))
        
# 게임 종료 처리 // 메세지도 보여줌
def game_over():
    global running

    running = False
    
    msg = game_font.render(f'Your LEVEL is {curr_level} !', True, WHITE)
    msg_rect = msg.get_rect(center=(screen_width/2, screen_height/2))
    
    screen.fill(BLACK)
    screen.blit(msg, msg_rect)

## 기억력 게임 함수

# 레벨에 맞게 설정
def setup(level):
    global display_time
    # 얼마동안 숫자를 보여줄지
    display_time = 5 - (level // 3)
    display_time = max(display_time, 1) # 1초 미만이면 1초로 처리

    # 얼마나 많은 숫자를 보여줄 것인가?
    number_count = (level // 3) + 5
    number_count = min(number_count, 20) # 만약 20 초과하면 20으로 처리

    # 실제 화면에 grid 형태로 숫자를 랜덤 배치
    shuffle_grid(number_count)
    
# 숫자 섞기
def shuffle_grid(number_count):
    rows = 5
    columns = 9

    cell_size = 130 # 각 grid cell 별 가로, 세로 크기
    button_size = 110 # grid cell 내에 실제로 그려질 버튼 크기
    screen_left_margin = 55 # 전체 스크린의 왼쪽 여백
    screen_top_margin = 20 # 전체 스크린의 위쪽 여백

    grid = [[0 for col in range(columns)] for row in range(rows)]

    number = 1 # 시작 숫자를 1부터 number_count까지, 만약 5라면 5까지의 숫자를 랜덤으로 배치
    while number <= number_count:
        row_idx = randrange(0, rows) # 0, 1, 2, 3, 4 중에서 랜덤으로 뽑기
        col_idx = randrange(0, columns) # 0 ~ 8 중에서 랜덤으로 뽑기

        if grid[row_idx][col_idx] == 0:
            grid[row_idx][col_idx] = number # 숫자 지정
            number += 1

            # 현재 grid cell 위치 기준으로 x, y 위치 구함
            center_x = screen_left_margin + (col_idx * cell_size) + (cell_size / 2)
            center_y = screen_top_margin + (row_idx * cell_size) + (cell_size / 2)

            # 숫자 버튼 만들기
            button = pygame.Rect(0, 0, button_size, button_size)
            button.center = (center_x, center_y)

            number_buttons.append(button)
    # 배치된 랜덤 숫자 확인
    print(grid)
    
# 포지션에 대응하는 버튼 확인
def check_buttons(pos):
    global start, start_ticks
    if start: # 게임이 시작했으면?
        check_number_buttons(pos)
    elif start_button.collidepoint(pos):
        start = True
        start_ticks = pygame.time.get_ticks() # 타이머 시작(현재 시간을 저장)

def check_number_buttons(pos):
    global start, hidden, curr_level
    for button in number_buttons:
        if button.collidepoint(pos):
            if button == number_buttons[0]: # 올바른 숫자 클릭
                print("correct")
                # 올바른 숫자 눌렀을 시 올바른 숫자가 삭제됨
                del number_buttons[0]
                if not hidden:
                    hidden = True # 화면에서 숫자 숨김 처리
            else: # 잘못된 숫자 클릭    
                game_over()
            break
# 오든 숫자를 다 맞혔다면? 다음 레벨로 넘어간다.
    if len(number_buttons) == 0:
        start = False
        hidden = False
        curr_level += 1
        setup(curr_level)
    
      
# 두더지 게임 설정
mole_image = pygame.image.load('mole.png')
moles = []
for i in range(2):
    mole = mole_image.get_rect(left=random.randint(0, screen_width - mole_image.get_width()), 
                               top=random.randint(0, screen_height - mole_image.get_height()))
    after_second = random.randint(0, 3)
    during_second = random.randint(1, 3)
    appear_time = int(time.time()) + after_second
    disappear_time = int(time.time()) + after_second + during_second
    moles.append((mole, appear_time, disappear_time))
    

# 기억력 테스트 게임 설정
# 실제 플레이어가 눌러야 하는 버튼
number_buttons = []
# 현재 레벨
curr_level = 1
# 숫자를 보여주는 시간
display_time = None
# 시간 계산(현재 시간 정보를 저장)
start_ticks = None

# 게임 시작 여부
start = False
# 숫자 숨김 여부(사용자가 1(첫 번째 숫자)을 클릭했거나, 보여주는 시간을 초과했을 때)
hidden = False

# 게임 시작 직전에 게임 설정 함수 수행, 현재 레벨
setup(curr_level)

####게임 루프####
running = True

while running:
    click_pos = None

    # 이벤트 루프
    for event in pygame.event.get(): # 어떤 이벤트가 발생하였는지
        if event.type == pygame.QUIT: # 사용자가 창을 닫는 이벤트면 게임 종료
            running = False # 게임이 더 이상 실행 중이 아닌 상태
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONUP: # 사용자가 마우스 클릭 후 뗄 때
            click_pos = pygame.mouse.get_pos()
            print(click_pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and not mole_game_over: # 사용자가 마우스 클릭할 때
            print(event.pos[0], event.pos[1])
            for mole, appear_time, disappear_time in moles:
                if mole.collidepoint(event.pos):
                    print(mole)
                    moles.remove((mole, appear_time, disappear_time))
                    mole = mole_image.get_rect(left=random.randint(0, screen_width - mole_image.get_width()), 
                                               top=random.randint(0, screen_height - mole_image.get_height()))
                    after_second = random.randint(0, 3)
                    during_second = random.randint(1, 3)
                    appear_time = int(time.time()) + after_second
                    disappear_time = int(time.time()) + after_second + during_second
                    moles.append((mole, appear_time, disappear_time))
                    score += 1
                    whack_sound.play() # 사운드
                    
        # 두더지 게임 종료
        if not mole_game_over:       
            current_time = int(time.time())
            remain_second = 90 - (current_time - start_time) - penalty_second

            if remain_second <= 0:
                mole_game_over = True
                for mole, appear_time, disappear_time in moles:
                    current_time = int(time.time())
                    if appear_time > current_time:  
                        moles.remove((mole, appear_time, disappear_time))
                        pygame.mixer.music.stop() # 배경 음악 정지
                        game_over_sound.play() # 종료 사운드

            for mole, appear_time, disappear_time in moles:
                current_time = int(time.time())
                if current_time > disappear_time:  
                    moles.remove((mole, appear_time, disappear_time))
                    mole = mole_image.get_rect(left=random.randint(0, screen_width - mole_image.get_width()), 
                                               top=random.randint(0, screen_height - mole_image.get_height()))
                    after_second = random.randint(0, 3)
                    during_second = random.randint(1, 3)
                    appear_time = int(time.time()) + after_second
                    disappear_time = int(time.time()) + after_second + during_second
                    moles.append((mole, appear_time, disappear_time))
                    if remain_second >= 2:
                        penalty_second += 2


    # 화면 전체 까맣게 칠함
    screen.fill(BLACK)

    if start:
        display_memory_game_screen() # 게임 화면 표시
    else:
        display_start_screen() # 시작 화면 표시

    if curr_level == 5 :
        screen.fill(GRAY)
        mole_game_screen()
    # 사용자가 클릭한 좌표값이 있다면 / 어딘가 클릭했다면 
    if click_pos:
        check_buttons(click_pos)

    # 화면 업데이트
    pygame.display.update()

# 결과를 5초정도 보여줌
pygame.time.delay(5000)

#게임 종료
pygame.quit()
