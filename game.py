import pygame
import random
import sys
import math
import arabic_reshaper
from bidi.algorithm import get_display
import time

pygame.init()
pygame.mixer.init()
FPS = 60

correct_sound = pygame.mixer.Sound("assets/sounds/correct.wav")
wrong_sound = pygame.mixer.Sound("assets/sounds/wrong.wav") 
timeout_sound = pygame.mixer.Sound("assets/sounds/timeout.wav")

DARK_BLUE = (28, 37, 65)
NEON_BLUE = (66, 214, 249)
NEON_PINK = (255, 89, 158) 
NEON_PURPLE = (157, 78, 221)
DARK_GRAY = (40, 44, 52)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)  
RED = (255, 0, 0)    

WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("تحدي الرياضيات")

font = pygame.font.SysFont('calibri', 48)
title_font = pygame.font.SysFont('calibri', 70)
score_font = pygame.font.SysFont('calibri', 36)
button_font = pygame.font.SysFont('calibri', 32)
info_font = pygame.font.SysFont('calibri', 24)

class GameState:
    MENU = "menu"
    PLAYING = "playing"  
    GAME_OVER = "game_over"

class MathGame:
    def __init__(self):
        self.reset_game()
        self.state = GameState.MENU
        self.time_elapsed = 0
       
    def reset_game(self):
        self.score = 0
        self.mistakes = 0
        self.max_mistakes = 3
        self.winning_score = 100
        self.game_over = False
       
    def check_game_over(self):
        if self.score >= self.winning_score:
            self.game_over = True
            return "win"
        if self.mistakes >= self.max_mistakes:
            self.game_over = True
            return "lose"
        return None

def draw_neon_circle(surface, color, center, radius):
    for i in range(3):
        alpha = 100 - i * 30
        pygame.draw.circle(surface, (*color, alpha), center, radius + i*2, 2)

def draw_neon_text(text, font, color, x, y):
    for i in range(3):
        alpha = 100 - i * 30
        rendered_text = font.render(text, True, (*color, alpha))
        text_rect = rendered_text.get_rect(center=(x, y))
        screen.blit(rendered_text, text_rect)
   
    rendered_text = font.render(text, True, color)
    text_rect = rendered_text.get_rect(center=(x, y))
    screen.blit(rendered_text, text_rect)

def draw_text(text, font_type, color, x, y):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    draw_neon_text(bidi_text, font_type, color, x, y)

def draw_modern_timer(time_left, x, y, radius=40):
    draw_neon_circle(screen, NEON_BLUE, (x, y), radius)
   
    angle = (time_left / 10) * 360
    if time_left > 0:
        end_angle = -90 + angle
        pygame.draw.arc(screen, NEON_PINK, 
                     (x-radius, y-radius, radius*2, radius*2),
                     math.radians(-90), math.radians(end_angle), 3)

def draw_modern_button(text, x, y, width, height, color, hover=False):
    button_rect = pygame.Rect(x - width//2, y - height//2, width, height)
   
    if hover:
        for i in range(3):
            glow = pygame.Rect(x - width//2 - i*2, y - height//2 - i*2, 
                           width + i*4, height + i*4)
            pygame.draw.rect(screen, (*color, 100-i*30), glow, border_radius=15)
   
    pygame.draw.rect(screen, DARK_GRAY, button_rect, border_radius=15)
    pygame.draw.rect(screen, color, button_rect, 3, border_radius=15)
   
    draw_text(text, button_font, color, x, y)
    return button_rect

def draw_modern_menu():
    screen.fill(DARK_BLUE)
    current_time = time.time()
    for x in range(0, WIDTH, 30):
        for y in range(0, HEIGHT, 30):
            offset = math.sin(current_time + x*0.05 + y*0.05) * 2
            pygame.draw.circle(screen, (40, 50, 80), (x, y + offset), 1)
   
    draw_text("تحدي الرياضيات", title_font, NEON_BLUE, WIDTH//2, 150)
   
    info_rect = pygame.Rect(WIDTH//2 - 300, 220, 600, 200)
    pygame.draw.rect(screen, DARK_GRAY, info_rect, border_radius=20)
    pygame.draw.rect(screen, NEON_PURPLE, info_rect, 2, border_radius=20)
   
    draw_text("- اختبر مهاراتك في العمليات الحسابية", info_font, NEON_BLUE, WIDTH//2, 250)
    draw_text("- لديك 10 ثوانٍ للإجابة على كل سؤال", info_font, NEON_PINK, WIDTH//2, 300) 
    draw_text("- كل إجابة صحيحة = 5 نقاط", info_font, NEON_PURPLE, WIDTH//2, 350)
    draw_text("- 3 أخطاء = نهاية اللعبة", info_font, NEON_BLUE, WIDTH//2, 400)
   
    dev_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT - 120, 400, 100)
   
   
    draw_text("تم تطوير هذه اللعبة بواسطة: صادق الدبيسي", info_font, NEON_PINK, WIDTH//2, HEIGHT - 30)

    mouse_pos = pygame.mouse.get_pos()
    mouse_pos = pygame.mouse.get_pos()
    return draw_modern_button("ابدأ اللعب", WIDTH - 150, 380 + 3 * 100, 250, 60, NEON_BLUE,
                          hover=pygame.Rect(WIDTH - 275, 380 + 3 * 100 - 30, 250, 60).collidepoint(mouse_pos))

def generate_question():
    operation = random.choice(["+", "-", "x", "÷"])
    if operation == "÷":
        answer = random.randint(1, 10)
        num2 = random.randint(1, 10)
        num1 = answer * num2
    else:
        while True:
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
            if operation == "-":
                if num1 >= num2:
                    break
            else:
                break
               
    answer = eval(f"{num1} {operation.replace('x', '*').replace('÷', '//')} {num2}")
    question = f" ? = {num2} {operation} {num1}"
    choices = [answer]
    while len(choices) < 4:
        wrong = answer + random.choice([1,2,3,4,5])
        if wrong not in choices and wrong > 0:
            choices.append(wrong)
    random.shuffle(choices)
    return question, answer, choices

def main():
    running = True
    start_button_clicked = False
    game = MathGame()
    clock = pygame.time.Clock()
   
    question, correct_answer, choices = generate_question()
    last_answer_time = pygame.time.get_ticks()
    question_time = pygame.time.get_ticks() 
    answer_delay, question_timeout = 2000, 10000
    answer_state = None
    start_button = None

    while running:
        current_time = pygame.time.get_ticks()
       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
           
            if game.state == GameState.MENU:
                start_button = draw_modern_menu()
    
                if event.type == pygame.MOUSEBUTTONDOWN and start_button.collidepoint(event.pos):
                    game.state = GameState.PLAYING
                    question_time = pygame.time.get_ticks()

        if game.state == GameState.PLAYING:
            remaining_time = (question_timeout - (current_time - question_time)) // 1000
            screen.fill(DARK_BLUE)
  
            # رسم النمط الخلفي
            for x in range(0, WIDTH, 30):
                for y in range(0, HEIGHT, 30):
                    offset = math.sin(time.time() + x*0.05 + y*0.05) * 2
                    pygame.draw.circle(screen, (40, 50, 80), (x, y + offset), 1)
           
            game_state = game.check_game_over()
            if game_state:
                game.state = GameState.GAME_OVER
                continue

            # رسم واجهة اللعب
            draw_text("تحدي الرياضيات", title_font, NEON_BLUE, WIDTH//2, 80)
            draw_text(f"النقاط: {game.score}", score_font, NEON_PINK, WIDTH - 100, 50)
            draw_text(f"الأخطاء: {game.mistakes}/{game.max_mistakes}", score_font, NEON_PURPLE, 100, 50)
            draw_modern_timer(remaining_time, WIDTH//2, 150)
            draw_text(str(max(0, remaining_time)), score_font, NEON_BLUE, WIDTH//2, 150)
            draw_text(question, font, NEON_PINK, WIDTH//2, 250)

            choice_buttons = []
            mouse_pos = pygame.mouse.get_pos()
           
            for i, choice in enumerate(choices):
                button_color = NEON_BLUE
               
                if answer_state is not None:
                    if choice == correct_answer:
                        button_color = GREEN
                    elif i == answer_state and choice != correct_answer:
                        button_color = RED
                       
                button = draw_modern_button(f"{choice}", 
                                         WIDTH//2, 380 + i * 100,
                                         250, 90, button_color,
                                         hover=(not answer_state and 
                                               380 + i * 100 - 45 < mouse_pos[1] < 380 + i * 100 + 45))
                choice_buttons.append(button)

            if event.type == pygame.MOUSEBUTTONDOWN and answer_state is None and remaining_time > 0:
                for i, button in enumerate(choice_buttons):
                    if button.collidepoint(event.pos):
                        if choices[i] == correct_answer:
                            game.score += 5
                            correct_sound.play()
                        else:
                            game.mistakes += 1
                            wrong_sound.play()
                        answer_state = i
                        last_answer_time = current_time

            if remaining_time <= 0 and answer_state is None:
                answer_state = -1
                game.mistakes += 1
                timeout_sound.play()
                last_answer_time = current_time

            if answer_state is not None and current_time - last_answer_time > answer_delay:
                question, correct_answer, choices = generate_question()
                answer_state = None
                question_time = current_time
       
        elif game.state == GameState.GAME_OVER:
            screen.fill(DARK_BLUE)
            for x in range(0, WIDTH, 30):
                for y in range(0, HEIGHT, 30):
                    offset = math.sin(time.time() + x*0.05 + y*0.05) * 2 
                    pygame.draw.circle(screen, (40, 50, 80), (x, y + offset), 1)
                   
            if game.check_game_over() == "win":
                draw_text("!مبروك! لقد فزت", title_font, NEON_PINK, WIDTH//2, HEIGHT//2 - 50)
            else:
                draw_text("!انتهت اللعبة", title_font, NEON_PURPLE, WIDTH//2, HEIGHT//2 - 50)
                draw_text(f"مجموع النقاط: {game.score}", score_font, NEON_BLUE, WIDTH//2, HEIGHT//2)
           
            restart_button = draw_modern_button("العب مرة أخرى", WIDTH//2, HEIGHT//2 + 50, 250, 60, NEON_PINK)
           
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    game.reset_game()
                    game.state = GameState.MENU
                    question, correct_answer, choices = generate_question()
                    answer_state = None
                    question_time = pygame.time.get_ticks()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()