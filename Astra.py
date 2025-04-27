import pygame
import random
import sys
import numpy as np
import pickle
from sklearn.neighbors import KNeighborsClassifier

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hunter")

# Define color constants
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Player attributes
PLAYER_SIZE = 50
player_x = WIDTH // 2
player_y = HEIGHT - PLAYER_SIZE - 10
PLAYER_SPEED = 5

# Bullet attributes
BULLET_SIZE = 10
bullets = []
BULLET_SPEED = 7

# Alien attributes
ALIEN_SIZE = 50
alien = None
ALIEN_SPEED = 2
misses = 0
speed_multiplier = 1.0
spawn_rate = 0.025

# Font setup
font = pygame.font.Font(None, 36)

# KNN-based difficulty adjustment
data = []
target = []
knn_model = KNeighborsClassifier(n_neighbors=3)

def adjust_difficulty(score, misses):
    if len(data) > 3:
        difficulty = knn_model.predict([[score, misses]])[0]
        return difficulty * 0.5
    return 1.0

# Linked List Implementation for Storing Scores
class Node:
    def __init__(self, score):
        self.score = score
        self.next = None

class ScoreLinkedList:
    def __init__(self):
        self.head = None
    
    def append(self, score):
        new_node = Node(score)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
    
    def to_list(self):
        scores = []
        current = self.head
        while current:
            scores.append(current.score)
            current = current.next
        return scores
    
    def quick_sort(self, scores):
        if len(scores) <= 1:
            return scores
        pivot = scores[len(scores) // 2]
        left = [x for x in scores if x > pivot]
        middle = [x for x in scores if x == pivot]
        right = [x for x in scores if x < pivot]
        return self.quick_sort(left) + middle + self.quick_sort(right)

def save_score(score, misses):
    scores_list = ScoreLinkedList()
    try:
        with open("highscores.txt", "r") as file:
            for line in file.readlines():
                scores_list.append(int(line.strip()))
    except FileNotFoundError:
        pass
    
    scores_list.append(score)
    sorted_scores = scores_list.quick_sort(scores_list.to_list())[:10]
    
    with open("highscores.txt", "w") as file:
        for s in sorted_scores:
            file.write(f"{s}\n")
    
    data.append([score, misses])
    target.append(int(score / 10))
    knn_model.fit(data, target)

def load_scores():
    scores_list = ScoreLinkedList()
    try:
        with open("highscores.txt", "r") as file:
            for line in file.readlines():
                scores_list.append(int(line.strip()))
    except FileNotFoundError:
        return []
    return scores_list.quick_sort(scores_list.to_list())

def spawn_alien():
    return pygame.Rect(random.randint(0, WIDTH - ALIEN_SIZE), random.randint(0, HEIGHT // 2), ALIEN_SIZE, ALIEN_SIZE)

def display_scores():
    scores = load_scores()
    screen.fill(BLACK)
    y_offset = 100
    for idx, score in enumerate(scores):
        text = font.render(f"{idx+1}. Score: {score}", True, WHITE)
        screen.blit(text, (WIDTH // 3, y_offset))
        y_offset += 30
    pygame.display.update()
    pygame.time.delay(3000)

def game_over_screen(score):
    screen.fill(BLACK)
    text = font.render(f"Game Over! Score: {score}", True, WHITE)
    screen.blit(text, (WIDTH // 3, HEIGHT // 3))
    pygame.display.update()
    pygame.time.delay(2000)
    display_scores()

def main():
    global player_x, bullets, alien, ALIEN_SPEED, misses, speed_multiplier
    running = True
    score = 0
    clock = pygame.time.Clock()
    alien = spawn_alien()
    
    while running:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and player_x < WIDTH - PLAYER_SIZE:
            player_x += PLAYER_SPEED
        if keys[pygame.K_SPACE]:
            if len(bullets) < 3:
                bullet = pygame.Rect(player_x + PLAYER_SIZE // 2, player_y, BULLET_SIZE, BULLET_SIZE)
                bullets.append(bullet)
        
        for bullet in bullets[:]:
            bullet.y -= BULLET_SPEED
            if bullet.y < 0:
                bullets.remove(bullet)
        
        difficulty_factor = adjust_difficulty(score, misses)
        alien.y += int(ALIEN_SPEED * speed_multiplier * difficulty_factor)
        if alien.y > HEIGHT:
            misses += 1
            if misses >= 1:
                running = False
            alien = spawn_alien()
            speed_multiplier *= 0.15
        
        for bullet in bullets[:]:
            if bullet.colliderect(alien):
                bullets.remove(bullet)
                alien = spawn_alien()
                score += 1
        
        pygame.draw.polygon(screen, GREEN, [(player_x + PLAYER_SIZE // 2, player_y), (player_x, player_y + PLAYER_SIZE), (player_x + PLAYER_SIZE, player_y + PLAYER_SIZE)])
        for bullet in bullets:
            pygame.draw.rect(screen, RED, bullet)
        pygame.draw.rect(screen, BLUE, alien)
        
        text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(text, (10, 10))
        
        pygame.display.update()
        clock.tick(60)
    
    save_score(score, misses)
    game_over_screen(score)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()



