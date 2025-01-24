import pygame
import random
import sys
import math
import arabic_reshaper
from bidi.algorithm import get_display

pygame.init()
pygame.mixer.init()

correct_sound = pygame.mixer.Sound("assets/sounds/correct.wav")
wrong_sound = pygame.mixer.Sound("assets/sounds/wrong.wav") 
timeout_sound = pygame.mixer.Sound("assets/sounds/timeout.wav")

WHITE = (155, 155, 255)
BLACK = (0, 0, 0)
BLUE = (30, 144, 255)
GREEN = (50, 205, 50)
RED = (220, 20, 60)
GRAY = (211, 211, 211)

WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("تحدي الرياضيات")

font = pygame.font.SysFont('calibri', 48)
title_font = pygame.font.SysFont('calibri', 60)
score_font = pygame.font.SysFont('calibri', 36)
button_font = pygame.font.SysFont('calibri', 32)

class MathGame:
   def __init__(self):
       self.reset_game()

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

def draw_timer(time_left, x, y, radius=40):
   angle = (time_left / 10) * 360
   pygame.draw.circle(screen, BLACK, (x, y), radius, 3)
   color = BLUE if time_left > 3 else RED
   if time_left > 0:
       pygame.draw.arc(screen, color, (x-radius, y-radius, radius*2, radius*2),
                      -90 * (math.pi/180), (angle-90) * (math.pi/180), radius)

def draw_text(text, font_type, color, x, y):
   reshaped_text = arabic_reshaper.reshape(text)
   bidi_text = get_display(reshaped_text)
   rendered_text = font_type.render(bidi_text, True, color)
   text_rect = rendered_text.get_rect(center=(x, y))
   screen.blit(rendered_text, text_rect)

def draw_button(text, x, y, width, height, color):
   button_rect = pygame.Rect(x - width//2, y - height//2, width, height)
   pygame.draw.rect(screen, color, button_rect, border_radius=15)
   pygame.draw.rect(screen, BLACK, button_rect, 3, border_radius=15)
   draw_text(text, button_font, BLACK, x, y)
   return button_rect

def generate_question():
   operation = random.choice(["+", "-", "x", "÷"])
   if operation == "÷":
       answer = random.randint(1, 10)
       num2 = random.randint(1, 10)
       num1 = answer * num2
   else:
       num1, num2 = random.randint(1, 10), random.randint(1, 10)
       answer = eval(f"{num1} {operation.replace('x', '*').replace('÷', '//')} {num2}")
   
   question = f"{num1} {operation} {num2} = ?"
   choices = [answer]
   while len(choices) < 4:
       wrong = answer + random.choice([-5,-4,-3,-2,-1,1,2,3,4,5])
       if wrong not in choices and wrong > 0:
           choices.append(wrong)
   random.shuffle(choices)
   return question, answer, choices

game = MathGame()
question, correct_answer, choices = generate_question()
choice_buttons = []
last_answer_time = pygame.time.get_ticks()
question_time = pygame.time.get_ticks()
answer_delay, question_timeout = 1000, 10000
answer_state = None
running = True
clock = pygame.time.Clock()

while running:
   current_time = pygame.time.get_ticks()
   remaining_time = (question_timeout - (current_time - question_time)) // 1000
   screen.fill(WHITE)
   
   game_state = game.check_game_over()
   if game_state:
       screen.fill(WHITE)
       if game_state == "win":
           draw_text("مبروك! لقد فزت!", title_font, GREEN, WIDTH//2, HEIGHT//2 - 50)
       else:
           draw_text("انتهت اللعبة!", title_font, RED, WIDTH//2, HEIGHT//2 - 50)
       
       restart_button = draw_button("العب مرة أخرى", WIDTH//2, HEIGHT//2 + 50, 250, 60, GREEN)
       
       pygame.display.flip()
       
       for event in pygame.event.get():
           if event.type == pygame.QUIT:
               running = False
           if event.type == pygame.MOUSEBUTTONDOWN:
               if restart_button.collidepoint(event.pos):
                   game.reset_game()
                   question, correct_answer, choices = generate_question()
                   answer_state = None
                   question_time = pygame.time.get_ticks()
       continue

   draw_text("تحدي الرياضيات", title_font, BLUE, WIDTH//2, 80)
   draw_text(f"النقاط: {game.score}", score_font, BLACK, WIDTH - 100, 50)
   draw_text(f"الأخطاء: {game.mistakes}/{game.max_mistakes}", score_font, BLACK, 100, 50)
   draw_timer(remaining_time, WIDTH//2, 150)
   draw_text(str(max(0, remaining_time)), score_font, BLACK, WIDTH//2, 150)
   draw_text(question, font, BLACK, WIDTH//2, 250)

   choice_buttons = []
   for i, choice in enumerate(choices):
       button_color = GRAY
       if answer_state is not None:
           if choice == correct_answer:
               button_color = GREEN
           elif i == answer_state and choice != correct_answer:
               button_color = RED
       button = draw_button(f"{i+1}) {choice}", WIDTH//2, 380 + i * 100, 250, 90, button_color)
       choice_buttons.append(button)

   for event in pygame.event.get():
       if event.type == pygame.QUIT:
           running = False
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
       if event.type == pygame.KEYDOWN and answer_state is None and remaining_time > 0:
           if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
               i = int(event.unicode) - 1
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

   pygame.display.flip()
   clock.tick(60)

pygame.quit()
sys.exit()