import pygame
import random
import sys
from functools import partial

# Inisialisasi Pygame
pygame.init()

# Warna (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 128, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
LIGHT_GRAY = (200, 200, 200)

# Ukuran layar untuk Redmi 10 (1080 x 2400 piksel)
WIDTH, HEIGHT = 1080, 2400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Math Quiz Game")

# Font
font_large = pygame.font.Font(None, 120)
font_medium = pygame.font.Font(None, 80)
font_small = pygame.font.Font(None, 60)

# FPS
clock = pygame.time.Clock()
FPS = 60

# Soal dan Jawaban
def generate_question():
    operations = ['+', '-', 'x', ':']  # Menambahkan operasi perkalian dan pembagian
    op = random.choice(operations)
    
    if op == '+':
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        answer = num1 + num2
    elif op == '-':
        num1 = random.randint(1, 10)
        num2 = random.randint(1, num1)  # Agar hasil pengurangan tidak negatif
        answer = num1 - num2
    elif op == 'x':  # Perkalian (lebih mudah)
        num1 = random.randint(1, 5)
        num2 = random.randint(1, 5)
        answer = num1 * num2
    elif op == ':':  # Pembagian (lebih mudah)
        num2 = random.randint(1, 5)
        num1 = num2 * random.randint(1, 5)  # Agar hasil pembagian bulat
        answer = num1 // num2  # Pembagian bulat
    question = f"{num1} {op} {num2} = ?"
    return question, answer

# Kelas Tombol
class Button:
    def __init__(self, text, x, y, width, height, inactive_color, active_color, action=None):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.action = action
        self.clicked = False

    def draw(self, surface, mouse_pos):
        color = self.active_color if self.rect.collidepoint(mouse_pos) else self.inactive_color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        text_surf = font_medium.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_click(self, mouse_pos, mouse_pressed, last_pressed_time):
        current_time = pygame.time.get_ticks()
        if self.rect.collidepoint(mouse_pos) and not self.clicked and current_time - last_pressed_time >= 200:  # 200 ms = 0.2 detik
            if mouse_pressed[0]:  # Jika tombol ditekan
                self.clicked = True
                if self.action:
                    self.action()  # Jalankan aksi tombol
                return current_time  # Perbarui waktu terakhir tombol ditekan
        return last_pressed_time

# Status Game
MENU = 'menu'
QUIZ = 'quiz'
END = 'end'

current_state = MENU
question, correct_answer = generate_question()
user_answer = ""
score = 0
total_questions = 0
start_time = 0
time_left = 60000  # Waktu total 1 menit dalam milidetik
last_pressed_time = 0  # Variabel waktu terakhir tombol ditekan
skip_question = False  # Variabel untuk skip soal

# Fungsi Menu Utama
def main_menu():
    screen.fill(WHITE)
    draw_text_center("Math Quiz Game", font_large, BLACK, WIDTH // 2, HEIGHT // 3)
    start_button.draw(screen, pygame.mouse.get_pos())
    pygame.display.flip()

# Fungsi Kuis
def game_loop():
    global time_left, skip_question
    screen.fill(WHITE)
    
    # Hitung sisa waktu
    elapsed_time = pygame.time.get_ticks() - start_time  # Waktu yang sudah berlalu dalam milidetik
    time_left = max(0, 60000 - elapsed_time)  # Menghitung waktu sisa dalam milidetik

    time_seconds = time_left // 1000  # Waktu dalam detik
    time_milliseconds = time_left % 1000  # Sisa milidetik
    
    # Tampilkan sisa waktu
    draw_text_center(f"Time Left: {time_seconds}s {time_milliseconds // 100}ms", font_medium, BLACK, WIDTH - 250, 50)
    draw_text_center("Answer the question:", font_medium, BLACK, WIDTH // 2, HEIGHT // 4)
    draw_text_center(question, font_large, BLACK, WIDTH // 2, HEIGHT // 3)
    
    # Kotak input jawaban
    answer_box = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 120)
    pygame.draw.rect(screen, LIGHT_GRAY, answer_box, border_radius=10)
    pygame.draw.rect(screen, BLACK, answer_box, 3, border_radius=10)
    draw_text_center(user_answer, font_large, BLACK, answer_box.centerx, answer_box.centery)

    # Tampilkan tombol angka, '=', tombol skip, dan tombol tambahan
    global last_pressed_time
    last_pressed_time = draw_numeric_buttons(last_pressed_time)
    
    # Jika waktu habis, tampilkan layar skor
    if time_left == 0:
        current_state = END  # Pindah ke layar akhir jika waktu habis
        end_screen()
    
    pygame.display.flip()

# Fungsi Layar Akhir
def end_screen():
    screen.fill(WHITE)
    draw_text_center("Quiz Finished!", font_large, BLACK, WIDTH // 2, HEIGHT // 3)
    draw_text_center(f"Your Score: {score} / {total_questions}", font_medium, BLACK, WIDTH // 2, HEIGHT // 2)
    retry_button.draw(screen, pygame.mouse.get_pos())
    pygame.display.flip()

# Fungsi untuk Menampilkan Teks di Tengah Layar
def draw_text_center(text, font, color, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    screen.blit(text_obj, text_rect)

# Fungsi untuk Menambahkan Karakter ke Jawaban
def add_to_answer(char):
    global user_answer
    if char == "=":
        submit_answer()  # Periksa jawaban ketika tombol "=" ditekan
    elif char == "C":
        user_answer = ""  # Hapus seluruh input
    elif char == "X":
        user_answer = user_answer[:-1]  # Hapus karakter terakhir
    elif char == "Skip":
        skip_soal()  # Skip soal jika tombol "Skip" ditekan
    else:
        # Batasi input maksimal 3 digit angka dan tambahkan hanya jika tidak melebihi batas
        if len(user_answer) < 3:
            user_answer += char  # Tambahkan angka ke jawaban

# Fungsi untuk Menggambar Tombol Angka, '=', tombol Skip, dan Tombol Hapus
def draw_numeric_buttons(last_pressed_time):
    button_texts = [
        ('1', '2', '3'),
        ('4', '5', '6'),
        ('7', '8', '9'),
        ('0', '.', 'Skip'),
        ('X', 'C', '=')
    ]
    
    button_width, button_height = 200, 120
    start_x = WIDTH // 2 - (button_width * 3) // 2
    start_y = HEIGHT // 2 + 200
    gap = 20

    for i, row in enumerate(button_texts):
        for j, char in enumerate(row):
            x = start_x + j * (button_width + gap)
            y = start_y + i * (button_height + gap)
            button = Button(char, x, y, button_width, button_height, BLUE, GREEN, partial(add_to_answer, char))
            button.draw(screen, pygame.mouse.get_pos())
            last_pressed_time = button.check_click(pygame.mouse.get_pos(), pygame.mouse.get_pressed(), last_pressed_time)
    
    return last_pressed_time

# Aksi Tombol
def start_game():
    global current_state, question, correct_answer, user_answer, score, total_questions, start_time
    current_state = QUIZ
    question, correct_answer = generate_question()
    user_answer = ""
    score = 0
    total_questions = 0
    start_time = pygame.time.get_ticks()  # Set waktu mulai

def submit_answer():
    global current_state, question, correct_answer, user_answer, score, total_questions
    if user_answer.isdigit():
        total_questions += 1
        if int(user_answer) == correct_answer:
            score += 1
    question, correct_answer = generate_question()
    user_answer = ""

def skip_soal():
    global question, correct_answer, user_answer, total_questions
    total_questions += 1
    question, correct_answer = generate_question()
    user_answer = ""

def retry_game():
    global current_state, question, correct_answer, user_answer, score, total_questions, start_time
    current_state = QUIZ  # Mengubah state ke QUIZ
    question, correct_answer = generate_question()
    user_answer = ""
    score = 0
    total_questions = 0
    start_time = pygame.time.get_ticks()  # Reset waktu

# Tombol untuk Mulai dan Ulangi
start_button = Button("START", WIDTH // 2 - 150, HEIGHT // 2, 300, 100, BLUE, GREEN, start_game)
retry_button = Button("RETRY", WIDTH // 2 - 150, HEIGHT // 2 + 300, 300, 100, BLUE, GREEN, retry_game)

# Main Loop
running = True
while running:
    clock.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Proses state game sesuai posisi (menu, kuis, akhir)
    if current_state == MENU:
        main_menu()
        last_pressed_time = start_button.check_click(mouse_pos, mouse_pressed, last_pressed_time)
    elif current_state == QUIZ:
        game_loop()
    elif current_state == END:
        end_screen()
        last_pressed_time = retry_button.check_click(mouse_pos, mouse_pressed, last_pressed_time)

pygame.quit()
sys.exit()
