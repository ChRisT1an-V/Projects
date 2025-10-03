import pygame
import json
import hashlib
import os
import random
import math
from pygame.locals import *  # Precisa instalar o pygame 2.6.1
from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
# PRECISA INSTALAR O FLET NA VERSÃO 0.28.3, para não ter erros de conflito ative o ambiente virtual com o comando:
# python -m venv venv

# Inicialização do pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Configurações da janela
WIDTH, HEIGHT = 1200, 800
janela = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Epic RPG Character Creator v2.0')

# Paleta de cores moderna
class Colors:
    PRIMARY = (46, 125, 160)      # Azul principal
    SECONDARY = (30, 81, 105)     # Azul escuro
    ACCENT = (255, 107, 107)      # Vermelho accent
    SUCCESS = (76, 175, 80)       # Verde
    WARNING = (255, 193, 7)       # Amarelo
    DANGER = (244, 67, 54)        # Vermelho
    
    # UI Colors
    BACKGROUND = (18, 18, 18)     # Preto suave
    SURFACE = (28, 28, 30)        # Cinza escuro
    CARD = (44, 44, 46)           # Cinza médio
    TEXT_PRIMARY = (255, 255, 255)
    TEXT_SECONDARY = (170, 170, 170)
    BORDER = (60, 60, 67)
    SHADOW = (0, 0, 0, 50)

# Enums para melhor organização
class Screen(Enum):
    LOGIN = "login"
    REGISTER = "register" 
    MAIN_MENU = "main_menu"
    CHARACTER_SELECT = "character_select"
    CUSTOMIZE = "customize"
    INVENTORY = "inventory"
    BATTLE = "battle"

class CharacterClass(Enum):
    WARRIOR = "warrior"
    MAGE = "mage"
    ARCHER = "archer"
    ROGUE = "rogue"

# Fontes modernas
try:
    font_title = pygame.font.Font(None, 48)
    font_header = pygame.font.Font(None, 36)
    font_body = pygame.font.Font(None, 24)
    font_small = pygame.font.Font(None, 18)
except:
    font_title = pygame.font.SysFont('Arial', 48, bold=True)
    font_header = pygame.font.SysFont('Arial', 36, bold=True)
    font_body = pygame.font.SysFont('Arial', 24)
    font_small = pygame.font.SysFont('Arial', 18)

@dataclass
class Character:
    name: str = "Hero"
    class_type: str = CharacterClass.WARRIOR.value
    level: int = 1
    experience: int = 0
    
    # Atributos primários
    strength: int = 10
    intelligence: int = 10
    agility: int = 10
    charisma: int = 10
    vitality: int = 10
    luck: int = 10
    
    # Atributos derivados
    health: int = 100
    mana: int = 50
    
    # Aparência
    skin_color: Tuple[int, int, int] = (255, 213, 170)
    hair_color: Tuple[int, int, int] = (139, 69, 19)
    hair_style: int = 0
    eye_color: Tuple[int, int, int] = (70, 130, 180)
    
    # Equipamentos
    armor_color: Tuple[int, int, int] = (100, 100, 100)
    weapon_type: str = "sword"
    accessory: str = "none"
    
    # Progressão
    skill_points: int = 5
    gold: int = 100
    
    def get_max_health(self) -> int:
        return 80 + (self.vitality * 8) + (self.level * 5)
    
    def get_max_mana(self) -> int:
        return 30 + (self.intelligence * 5) + (self.level * 3)
    
    def get_attack_power(self) -> int:
        return self.strength + (self.level * 2)
    
    def get_magic_power(self) -> int:
        return self.intelligence + (self.level * 2)

class AnimatedSprite:
    def __init__(self, x: int, y: int, frames: List[pygame.Surface], frame_duration: int = 100):
        self.x = x
        self.y = y
        self.frames = frames
        self.current_frame = 0
        self.frame_duration = frame_duration
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 1.0
    
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration / self.animation_speed:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = now
    
    def draw(self, surface: pygame.Surface):
        if self.frames:
            surface.blit(self.frames[self.current_frame], (self.x, self.y))

class ModernButton:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 style: str = "primary", icon: Optional[str] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.style = style
        self.icon = icon
        self.is_hovered = False
        self.is_pressed = False
        self.animation_progress = 0.0
        self.glow_radius = 0
        
        # Estilos
        self.styles = {
            "primary": {"bg": Colors.PRIMARY, "text": Colors.TEXT_PRIMARY, "hover": (66, 145, 180)},
            "secondary": {"bg": Colors.SURFACE, "text": Colors.TEXT_PRIMARY, "hover": (48, 48, 50)},
            "success": {"bg": Colors.SUCCESS, "text": Colors.TEXT_PRIMARY, "hover": (96, 195, 100)},
            "danger": {"bg": Colors.DANGER, "text": Colors.TEXT_PRIMARY, "hover": (255, 87, 74)}
        }
    
    def update(self, dt: float):
        target = 1.0 if self.is_hovered else 0.0
        self.animation_progress += (target - self.animation_progress) * dt * 8
        
        if self.is_hovered:
            self.glow_radius = min(self.glow_radius + dt * 50, 10)
        else:
            self.glow_radius = max(self.glow_radius - dt * 50, 0)
    
    def draw(self, surface: pygame.Surface):
        style = self.styles.get(self.style, self.styles["primary"])
        
        # Efeito de glow
        if self.glow_radius > 0:
            glow_rect = self.rect.inflate(self.glow_radius * 2, self.glow_radius * 2)
            glow_surface = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*style["bg"], 50), 
                           pygame.Rect(0, 0, glow_rect.width, glow_rect.height), 
                           border_radius=12)
            surface.blit(glow_surface, glow_rect.topleft)
        
        # Cor do botão com animação
        bg_color = [
            int(style["bg"][i] + (style["hover"][i] - style["bg"][i]) * self.animation_progress)
            for i in range(3)
        ]
        
        # Desenhar botão
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, Colors.BORDER, self.rect, 2, border_radius=8)
        
        # Texto
        text_surface = font_body.render(self.text, True, style["text"])
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event, mouse_pos: Tuple[int, int]) -> bool:
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            self.is_pressed = True
        elif event.type == MOUSEBUTTONUP and event.button == 1 and self.is_pressed:
            self.is_pressed = False
            return self.is_hovered
        
        return False

class ModernInputBox:
    def __init__(self, x: int, y: int, width: int, height: int, placeholder: str = "", 
                 is_password: bool = False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.is_password = is_password
        self.is_focused = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.animation_progress = 0.0
    
    def update(self, dt: float):
        self.cursor_timer += dt * 1000
        if self.cursor_timer >= 1000:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
        
        target = 1.0 if self.is_focused else 0.0
        self.animation_progress += (target - self.animation_progress) * dt * 8
    
    def handle_event(self, event: pygame.event.Event, mouse_pos: Tuple[int, int]) -> Optional[str]:
        if event.type == MOUSEBUTTONDOWN:
            self.is_focused = self.rect.collidepoint(mouse_pos)
        
        if self.is_focused and event.type == KEYDOWN:
            if event.key == K_RETURN:
                return "enter"
            elif event.key == K_TAB:
                return "tab"
            elif event.key == K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if event.unicode.isprintable():
                    self.text += event.unicode
        
        return None
    
    def draw(self, surface: pygame.Surface):
        # Cor da borda com animação
        border_color = [
            int(Colors.BORDER[i] + (Colors.PRIMARY[i] - Colors.BORDER[i]) * self.animation_progress)
            for i in range(3)
        ]
        
        # Fundo
        pygame.draw.rect(surface, Colors.SURFACE, self.rect, border_radius=6)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=6)
        
        # Texto
        display_text = self.text if not self.is_password else '*' * len(self.text)
        if not display_text and not self.is_focused:
            display_text = self.placeholder
            text_color = Colors.TEXT_SECONDARY
        else:
            text_color = Colors.TEXT_PRIMARY
        
        if display_text:
            text_surface = font_body.render(display_text, True, text_color)
            text_rect = text_surface.get_rect()
            text_rect.centery = self.rect.centery
            text_rect.x = self.rect.x + 12
            surface.blit(text_surface, text_rect)
        
        # Cursor
        if self.is_focused and self.cursor_visible:
            cursor_x = self.rect.x + 12 + font_body.size(display_text)[0]
            pygame.draw.line(surface, Colors.TEXT_PRIMARY, 
                           (cursor_x, self.rect.y + 8), 
                           (cursor_x, self.rect.bottom - 8), 2)

class ModernSlider:
    def __init__(self, x: int, y: int, width: int, min_val: int = 1, 
                 max_val: int = 20, initial_val: int = 10, step: int = 1):
        self.rect = pygame.Rect(x, y, width, 24)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.step = step
        self.is_dragging = False
        self.thumb_radius = 12
        self.animation_progress = 0.0
    
    def update(self, dt: float):
        target = 1.0 if self.is_dragging else 0.0
        self.animation_progress += (target - self.animation_progress) * dt * 10
    
    def handle_event(self, event: pygame.event.Event, mouse_pos: Tuple[int, int]) -> bool:
        thumb_x = self.rect.x + (self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        thumb_rect = pygame.Rect(thumb_x - self.thumb_radius, self.rect.centery - self.thumb_radius,
                               self.thumb_radius * 2, self.thumb_radius * 2)
        
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if thumb_rect.collidepoint(mouse_pos) or self.rect.collidepoint(mouse_pos):
                self.is_dragging = True
                self._update_value(mouse_pos[0])
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                return True
        elif event.type == MOUSEMOTION and self.is_dragging:
            self._update_value(mouse_pos[0])
        
        return False
    
    def _update_value(self, mouse_x: int):
        relative_x = max(0, min(self.rect.width, mouse_x - self.rect.x))
        percentage = relative_x / self.rect.width
        raw_val = self.min_val + percentage * (self.max_val - self.min_val)
        self.val = round(raw_val / self.step) * self.step
        self.val = max(self.min_val, min(self.max_val, self.val))
    
    def draw(self, surface: pygame.Surface, label: str = ""):
        # Track
        track_rect = pygame.Rect(self.rect.x, self.rect.centery - 3, self.rect.width, 6)
        pygame.draw.rect(surface, Colors.BORDER, track_rect, border_radius=3)
        
        # Filled track
        thumb_x = self.rect.x + (self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        filled_rect = pygame.Rect(self.rect.x, self.rect.centery - 3, thumb_x - self.rect.x, 6)
        pygame.draw.rect(surface, Colors.PRIMARY, filled_rect, border_radius=3)
        
        # Thumb
        thumb_color = [
            int(Colors.PRIMARY[i] + (Colors.ACCENT[i] - Colors.PRIMARY[i]) * self.animation_progress)
            for i in range(3)
        ]
        pygame.draw.circle(surface, thumb_color, (int(thumb_x), self.rect.centery), self.thumb_radius)
        pygame.draw.circle(surface, Colors.TEXT_PRIMARY, (int(thumb_x), self.rect.centery), self.thumb_radius, 2)
        
        # Label
        if label:
            label_surface = font_body.render(f"{label}: {self.val}", True, Colors.TEXT_PRIMARY)
            surface.blit(label_surface, (self.rect.x, self.rect.y - 25))

class ModernCharacterRenderer:
    def __init__(self):
        self.animation_time = 0
        self.idle_animation_speed = 2.0
        
        # Paletas de cores expandidas
        self.skin_colors = [
            (255, 213, 170), (210, 180, 140), (170, 140, 110), 
            (140, 100, 70), (90, 60, 40), (240, 190, 150),
            (200, 160, 120), (160, 120, 90)
        ]
        
        self.hair_colors = [
            (50, 50, 50), (139, 69, 19), (222, 184, 135), 
            (255, 215, 0), (165, 42, 42), (128, 0, 128),
            (255, 140, 0), (70, 130, 180), (255, 20, 147)
        ]
        
        self.eye_colors = [
            (70, 130, 180), (34, 139, 34), (139, 69, 19),
            (128, 0, 128), (255, 140, 0), (220, 20, 60),
            (0, 128, 128), (105, 105, 105)
        ]
    
    def update(self, dt: float):
        self.animation_time += dt * self.idle_animation_speed
    
    def draw_character(self, surface: pygame.Surface, character: Character, x: int, y: int, scale: float = 1.0):
        # Animação de idle
        bob_offset = math.sin(self.animation_time) * 2
        
        # Dimensões base
        head_size = int(60 * scale)
        body_width = int(40 * scale)
        body_height = int(80 * scale)
        
        char_y = y + bob_offset
        
        # Sombra
        shadow_y = y + 200 * scale
        shadow_ellipse = pygame.Rect(x + 10, shadow_y, 80 * scale, 20 * scale)
        pygame.draw.ellipse(surface, (0, 0, 0, 50), shadow_ellipse)
        
        # Corpo (armadura)
        body_rect = pygame.Rect(x + 20, char_y + head_size, body_width, body_height)
        pygame.draw.rect(surface, character.armor_color, body_rect, border_radius=int(5 * scale))
        
        # Braços
        arm_width = int(15 * scale)
        arm_height = int(50 * scale)
        # Braço esquerdo
        left_arm = pygame.Rect(x + 5, char_y + head_size + 10, arm_width, arm_height)
        pygame.draw.rect(surface, character.skin_color, left_arm, border_radius=int(7 * scale))
        # Braço direito
        right_arm = pygame.Rect(x + 60, char_y + head_size + 10, arm_width, arm_height)
        pygame.draw.rect(surface, character.skin_color, right_arm, border_radius=int(7 * scale))
        
        # Pernas
        leg_width = int(18 * scale)
        leg_height = int(60 * scale)
        # Perna esquerda
        left_leg = pygame.Rect(x + 22, char_y + head_size + body_height - 10, leg_width, leg_height)
        pygame.draw.rect(surface, character.armor_color, left_leg, border_radius=int(5 * scale))
        # Perna direita
        right_leg = pygame.Rect(x + 42, char_y + head_size + body_height - 10, leg_width, leg_height)
        pygame.draw.rect(surface, character.armor_color, right_leg, border_radius=int(5 * scale))
        
        # Cabeça
        head_rect = pygame.Rect(x + 15, char_y, head_size, head_size)
        pygame.draw.ellipse(surface, character.skin_color, head_rect)
        
        # Cabelo (estilo baseado no hair_style)
        hair_styles = [
            # Estilo 0: Cabelo curto
            lambda: pygame.draw.ellipse(surface, character.hair_color, 
                                      pygame.Rect(x + 10, char_y - 5, head_size + 10, head_size // 2)),
            # Estilo 1: Cabelo longo
            lambda: pygame.draw.ellipse(surface, character.hair_color, 
                                      pygame.Rect(x + 8, char_y - 10, head_size + 14, head_size + 20)),
            # Estilo 2: Cabelo spiky
            lambda: [pygame.draw.polygon(surface, character.hair_color, 
                                       [(x + 20 + i * 10, char_y - 8), (x + 25 + i * 10, char_y - 18), 
                                        (x + 30 + i * 10, char_y - 8)]) for i in range(4)]
        ]
        
        if character.hair_style < len(hair_styles):
            hair_styles[character.hair_style]()
        
        # Olhos
        eye_size = int(8 * scale)
        eye_y = char_y + head_size // 3
        # Olho esquerdo
        pygame.draw.ellipse(surface, Colors.TEXT_PRIMARY, 
                          pygame.Rect(x + 25, eye_y, eye_size, eye_size))
        pygame.draw.ellipse(surface, character.eye_color, 
                          pygame.Rect(x + 27, eye_y + 2, eye_size - 4, eye_size - 4))
        # Olho direito
        pygame.draw.ellipse(surface, Colors.TEXT_PRIMARY, 
                          pygame.Rect(x + 45, eye_y, eye_size, eye_size))
        pygame.draw.ellipse(surface, character.eye_color, 
                          pygame.Rect(x + 47, eye_y + 2, eye_size - 4, eye_size - 4))
        
        # Boca
        mouth_rect = pygame.Rect(x + 35, char_y + head_size // 2, int(10 * scale), int(4 * scale))
        pygame.draw.ellipse(surface, (255, 100, 100), mouth_rect)
        
        # Arma (baseada no tipo)
        self._draw_weapon(surface, character, x, char_y, scale)
    
    def _draw_weapon(self, surface: pygame.Surface, character: Character, x: int, y: int, scale: float):
        weapon_x = x + 85
        weapon_y = y + 80
        
        if character.weapon_type == "sword":
            # Espada
            blade = pygame.Rect(weapon_x, weapon_y, int(8 * scale), int(60 * scale))
            handle = pygame.Rect(weapon_x + 2, weapon_y + 50, int(4 * scale), int(20 * scale))
            pygame.draw.rect(surface, (192, 192, 192), blade)
            pygame.draw.rect(surface, (139, 69, 19), handle)
            
        elif character.weapon_type == "staff":
            # Cajado
            staff = pygame.Rect(weapon_x + 3, weapon_y - 10, int(3 * scale), int(80 * scale))
            orb = pygame.Rect(weapon_x, weapon_y - 15, int(10 * scale), int(10 * scale))
            pygame.draw.rect(surface, (139, 69, 19), staff)
            pygame.draw.ellipse(surface, Colors.PRIMARY, orb)
            
        elif character.weapon_type == "bow":
            # Arco
            pygame.draw.arc(surface, (139, 69, 19), 
                          pygame.Rect(weapon_x, weapon_y, int(15 * scale), int(50 * scale)), 
                          0, math.pi, int(3 * scale))

class ModernRPGGame:
    def __init__(self):
        self.current_screen = Screen.LOGIN
        self.logged_in_user = None
        self.users = self.load_users()
        self.current_character = Character()
        self.character_renderer = ModernCharacterRenderer()
        
        self.clock = pygame.time.Clock()
        self.dt = 0
        
        self._init_ui_elements()
        
        # Configurações de tela
        self.screen_transitions = {}
        self.transition_progress = 0.0
        
        # Partículas para efeitos
        self.particles = []
        
        # Sons (opcional)
        try:
            # pygame.mixer.Sound seria usado aqui
            pass
        except:
            pass
    
    def _init_ui_elements(self):
        # Tela de Login
        self.login_username = ModernInputBox(WIDTH//2 - 150, HEIGHT//2 - 60, 300, 50, "Username")
        self.login_password = ModernInputBox(WIDTH//2 - 150, HEIGHT//2 + 10, 300, 50, "Password", True)
        self.login_button = ModernButton(WIDTH//2 - 100, HEIGHT//2 + 80, 200, 50, "Login", "primary")
        self.register_button = ModernButton(WIDTH//2 - 100, HEIGHT//2 + 140, 200, 50, "Register", "secondary")
        
        # Tela de Registro
        self.reg_username = ModernInputBox(WIDTH//2 - 150, HEIGHT//2 - 120, 300, 50, "Username")
        self.reg_password = ModernInputBox(WIDTH//2 - 150, HEIGHT//2 - 60, 300, 50, "Password", True)
        self.reg_confirm = ModernInputBox(WIDTH//2 - 150, HEIGHT//2, 300, 50, "Confirm Password", True)
        self.reg_submit = ModernButton(WIDTH//2 - 100, HEIGHT//2 + 80, 200, 50, "Create Account", "success")
        self.reg_back = ModernButton(WIDTH//2 - 100, HEIGHT//2 + 140, 200, 50, "Back", "secondary")
        
        # Menu Principal
        self.customize_btn = ModernButton(WIDTH//2 - 120, HEIGHT//2 - 100, 240, 60, "Customize Character", "primary")
        self.inventory_btn = ModernButton(WIDTH//2 - 120, HEIGHT//2 - 30, 240, 60, "Inventory", "secondary")
        self.battle_btn = ModernButton(WIDTH//2 - 120, HEIGHT//2 + 40, 240, 60, "Battle Arena", "danger")
        self.logout_btn = ModernButton(WIDTH//2 - 120, HEIGHT//2 + 110, 240, 60, "Logout", "secondary")
        
        # Customização
        slider_x = WIDTH//2 + 200
        self.strength_slider = ModernSlider(slider_x, 150, 200, 1, 20, 10)
        self.intelligence_slider = ModernSlider(slider_x, 200, 200, 1, 20, 10)
        self.agility_slider = ModernSlider(slider_x, 250, 200, 1, 20, 10)
        self.charisma_slider = ModernSlider(slider_x, 300, 200, 1, 20, 10)
        self.vitality_slider = ModernSlider(slider_x, 350, 200, 1, 20, 10)
        self.luck_slider = ModernSlider(slider_x, 400, 200, 1, 20, 10)
        
        # Botões de aparência
        appearance_x = WIDTH//2 + 200
        self.skin_prev = ModernButton(appearance_x, 480, 80, 40, "◀ Skin", "secondary")
        self.skin_next = ModernButton(appearance_x + 100, 480, 80, 40, "Skin ▶", "secondary")
        self.hair_prev = ModernButton(appearance_x, 530, 80, 40, "◀ Hair", "secondary")
        self.hair_next = ModernButton(appearance_x + 100, 530, 80, 40, "Hair ▶", "secondary")
        self.eye_prev = ModernButton(appearance_x, 580, 80, 40, "◀ Eyes", "secondary")
        self.eye_next = ModernButton(appearance_x + 100, 580, 80, 40, "Eyes ▶", "secondary")
        
        self.save_character_btn = ModernButton(WIDTH//2 - 100, HEIGHT - 150, 200, 50, "Save Character", "success")
        self.back_to_menu_btn = ModernButton(WIDTH//2 - 100, HEIGHT - 90, 200, 50, "Back to Menu", "secondary")
    
    def load_users(self) -> Dict:
        try:
            if os.path.exists("users_v2.json"):
                with open("users_v2.json", 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_users(self):
        try:
            with open("users_v2.json", 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar usuários: {e}")
    
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        if not username or not password:
            return False, "Username and password required"
        
        if username in self.users:
            return False, "Username already exists"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        # Criar usuário com personagem padrão
        default_character = asdict(Character(name=username))
        
        self.users[username] = {
            "password": self.hash_password(password),
            "character": default_character,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "achievements": [],
            "total_playtime": 0
        }
        
        self.save_users()
        return True, "Account created successfully!"
    
    def login_user(self, username: str, password: str) -> Tuple[bool, str]:
        if not username or not password:
            return False, "Username and password required"
        
        if username not in self.users:
            return False, "Username not found"
        
        if self.users[username]["password"] != self.hash_password(password):
            return False, "Incorrect password"
        
        # Atualizar último login
        self.users[username]["last_login"] = datetime.now().isoformat()
        self.logged_in_user = username
        
        # Carregar personagem
        self.load_character()
        self.save_users()
        
        return True, "Login successful!"
    
    def load_character(self):
        if self.logged_in_user and "character" in self.users[self.logged_in_user]:
            char_data = self.users[self.logged_in_user]["character"]

        # Converter listas para tuplas nas cores
        for color_attr in ["skin_color", "hair_color", "eye_color", "armor_color"]:
            if color_attr in char_data and isinstance(char_data[color_attr], list):
                char_data[color_attr] = tuple(char_data[color_attr])

        self.current_character = Character(**char_data)
        # ...restante do código...
    
    def save_character(self):
        if self.logged_in_user:
            # Atualizar personagem com valores dos sliders
            self.current_character.strength = self.strength_slider.val
            self.current_character.intelligence = self.intelligence_slider.val
            self.current_character.agility = self.agility_slider.val
            self.current_character.charisma = self.charisma_slider.val
            self.current_character.vitality = self.vitality_slider.val
            self.current_character.luck = self.luck_slider.val
            
            # Salvar no arquivo
            self.users[self.logged_in_user]["character"] = asdict(self.current_character)
            self.save_users()
    
    def create_particles(self, x: int, y: int, count: int = 10, color: Tuple[int, int, int] = Colors.ACCENT):
        """Criar partículas para efeitos visuais"""
        for _ in range(count):
            particle = {
                "x": x + random.randint(-20, 20),
                "y": y + random.randint(-20, 20),
                "vx": random.randint(-50, 50),
                "vy": random.randint(-50, -20),
                "life": 1.0,
                "color": color,
                "size": random.randint(2, 6)
            }
            self.particles.append(particle)
    
    def update_particles(self, dt: float):
        """Atualizar partículas"""
        for particle in self.particles[:]:
            particle["x"] += particle["vx"] * dt
            particle["y"] += particle["vy"] * dt
            particle["vy"] += 100 * dt  # Gravidade
            particle["life"] -= dt * 2
            
            if particle["life"] <= 0:
                self.particles.remove(particle)
    
    def draw_particles(self, surface: pygame.Surface):
        """Desenhar partículas"""
        for particle in self.particles:
            alpha = int(255 * particle["life"])
            color = (*particle["color"], alpha)
            
            # Criar surface com alpha
            particle_surface = pygame.Surface((particle["size"] * 2, particle["size"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, 
                             (particle["size"], particle["size"]), particle["size"])
            
            surface.blit(particle_surface, (particle["x"], particle["y"]))
    
    def draw_background(self, surface: pygame.Surface):
        """Desenhar fundo com gradiente"""
        # Gradiente de fundo
        for y in range(HEIGHT):
            color_ratio = y / HEIGHT
            r = int(Colors.BACKGROUND[0] + (Colors.SURFACE[0] - Colors.BACKGROUND[0]) * color_ratio)
            g = int(Colors.BACKGROUND[1] + (Colors.SURFACE[1] - Colors.BACKGROUND[1]) * color_ratio)
            b = int(Colors.BACKGROUND[2] + (Colors.SURFACE[2] - Colors.BACKGROUND[2]) * color_ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))
        
        # Efeito de estrelas
        star_time = pygame.time.get_ticks() / 1000
        for i in range(50):
            star_x = (i * 47) % WIDTH
            star_y = (i * 31) % HEIGHT
            brightness = abs(math.sin(star_time + i * 0.5)) * 100 + 50
            color = (int(brightness), int(brightness), int(brightness))
            pygame.draw.circle(surface, color, (star_x, star_y), 1)
    
    def draw_ui_panel(self, surface: pygame.Surface, x: int, y: int, width: int, height: int, 
                      title: str = "", alpha: int = 200):
        """Desenhar painel de UI moderno"""
        # Fundo do painel
        panel_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (*Colors.CARD, alpha), 
                        (0, 0, width, height), border_radius=12)
        pygame.draw.rect(panel_surface, Colors.BORDER, 
                        (0, 0, width, height), 2, border_radius=12)
        
        surface.blit(panel_surface, (x, y))
        
        # Título do painel
        if title:
            title_surface = font_header.render(title, True, Colors.TEXT_PRIMARY)
            surface.blit(title_surface, (x + 20, y + 15))
            
            # Linha decorativa
            line_y = y + 50
            pygame.draw.line(surface, Colors.PRIMARY, (x + 20, line_y), (x + width - 20, line_y), 2)
    
    def draw_character_stats(self, surface: pygame.Surface, x: int, y: int):
        """Desenhar estatísticas do personagem"""
        self.draw_ui_panel(surface, x, y, 300, 400, "Character Stats")
        
        stats = [
            ("Level", self.current_character.level),
            ("Experience", f"{self.current_character.experience}/100"),
            ("Health", f"{self.current_character.health}/{self.current_character.get_max_health()}"),
            ("Mana", f"{self.current_character.mana}/{self.current_character.get_max_mana()}"),
            ("Gold", self.current_character.gold),
            ("", ""),  # Espaço
            ("Strength", self.current_character.strength),
            ("Intelligence", self.current_character.intelligence),
            ("Agility", self.current_character.agility),
            ("Charisma", self.current_character.charisma),
            ("Vitality", self.current_character.vitality),
            ("Luck", self.current_character.luck),
        ]
        
        for i, (stat_name, stat_value) in enumerate(stats):
            if stat_name:  # Pular linhas vazias
                stat_y = y + 70 + i * 25
                name_surface = font_body.render(f"{stat_name}:", True, Colors.TEXT_SECONDARY)
                value_surface = font_body.render(str(stat_value), True, Colors.TEXT_PRIMARY)
                
                surface.blit(name_surface, (x + 25, stat_y))
                surface.blit(value_surface, (x + 200, stat_y))
    
    def draw_login_screen(self, surface: pygame.Surface):
        """Tela de login moderna"""
        self.draw_background(surface)
        
        # Título principal
        title_surface = font_title.render("EPIC RPG", True, Colors.PRIMARY)
        title_rect = title_surface.get_rect(center=(WIDTH//2, 150))
        surface.blit(title_surface, title_rect)
        
        subtitle_surface = font_header.render("Character Creator v2.0", True, Colors.TEXT_SECONDARY)
        subtitle_rect = subtitle_surface.get_rect(center=(WIDTH//2, 190))
        surface.blit(subtitle_surface, subtitle_rect)
        
        # Painel de login
        self.draw_ui_panel(surface, WIDTH//2 - 200, HEIGHT//2 - 150, 400, 350, "Login")
        
        # Labels
        username_label = font_body.render("Username", True, Colors.TEXT_PRIMARY)
        surface.blit(username_label, (WIDTH//2 - 150, HEIGHT//2 - 80))
        
        password_label = font_body.render("Password", True, Colors.TEXT_PRIMARY)
        surface.blit(password_label, (WIDTH//2 - 150, HEIGHT//2 - 9))
        
        # Desenhar elementos
        self.login_username.draw(surface)
        self.login_password.draw(surface)
        self.login_button.draw(surface)
        self.register_button.draw(surface)
    
    def draw_register_screen(self, surface: pygame.Surface):
        """Tela de registro"""
        self.draw_background(surface)
        
        # Título
        title_surface = font_title.render("Create Account", True, Colors.SUCCESS)
        title_rect = title_surface.get_rect(center=(WIDTH//2, 120))
        surface.blit(title_surface, title_rect)
        
        # Painel
        self.draw_ui_panel(surface, WIDTH//2 - 200, HEIGHT//2 - 200, 400, 450, "Registration")
        
        # Labels
        labels = [
            ("Username", HEIGHT//2 - 150),
            ("Password", HEIGHT//2 - 90),
            ("Confirm Password", HEIGHT//2 - 30)
        ]
        
        for label, y_pos in labels:
            label_surface = font_body.render(label, True, Colors.TEXT_PRIMARY)
            surface.blit(label_surface, (WIDTH//2 - 150, y_pos))
        
        # Elementos
        self.reg_username.draw(surface)
        self.reg_password.draw(surface)
        self.reg_confirm.draw(surface)
        self.reg_submit.draw(surface)
        self.reg_back.draw(surface)
    
    def draw_main_menu(self, surface: pygame.Surface):
        """Menu principal"""
        self.draw_background(surface)
        
        # Título de boas-vindas
        welcome_text = f"Welcome back, {self.current_character.name}!"
        welcome_surface = font_header.render(welcome_text, True, Colors.TEXT_PRIMARY)
        welcome_rect = welcome_surface.get_rect(center=(WIDTH//2, 100))
        surface.blit(welcome_surface, welcome_rect)
        
        # Personagem grande no centro
        char_x = WIDTH//2 - 60
        char_y = 150
        self.character_renderer.draw_character(surface, self.current_character, char_x, char_y, 1.5)
        
        # Painel de estatísticas
        self.draw_character_stats(surface, 50, 200)
        
        # Painel de menu
        self.draw_ui_panel(surface, WIDTH - 350, 200, 300, 400, "Actions")
        
        # Botões do menu
        self.customize_btn.draw(surface)
        self.inventory_btn.draw(surface)
        self.battle_btn.draw(surface)
        self.logout_btn.draw(surface)
        
        # Informações adicionais
        info_y = HEIGHT - 100
        class_text = f"Class: {self.current_character.class_type.title()}"
        class_surface = font_body.render(class_text, True, Colors.TEXT_SECONDARY)
        surface.blit(class_surface, (WIDTH//2 - 100, info_y))
        
        level_text = f"Level {self.current_character.level} | {self.current_character.gold} Gold"
        level_surface = font_body.render(level_text, True, Colors.TEXT_SECONDARY)
        surface.blit(level_surface, (WIDTH//2 - 100, info_y + 25))
    
    def draw_customize_screen(self, surface: pygame.Surface):
        """Tela de customização"""
        self.draw_background(surface)
        
        # Título
        title_surface = font_header.render("Character Customization", True, Colors.PRIMARY)
        title_rect = title_surface.get_rect(center=(WIDTH//2, 50))
        surface.blit(title_surface, title_rect)
        
        # Personagem grande
        char_x = 100
        char_y = 150
        self.character_renderer.draw_character(surface, self.current_character, char_x, char_y, 2.0)
        
        # Painel de atributos
        self.draw_ui_panel(surface, WIDTH//2 + 50, 100, 500, 450, "Attributes")
        
        # Sliders de atributos
        sliders = [
            (self.strength_slider, "Strength"),
            (self.intelligence_slider, "Intelligence"),
            (self.agility_slider, "Agility"),
            (self.charisma_slider, "Charisma"),
            (self.vitality_slider, "Vitality"),
            (self.luck_slider, "Luck")
        ]
        
        for slider, label in sliders:
            slider.draw(surface, label)
        
        # Seção de aparência
        appearance_y = 450
        appearance_surface = font_body.render("Appearance", True, Colors.TEXT_PRIMARY)
        surface.blit(appearance_surface, (WIDTH//2 + 70, appearance_y))
        
        # Botões de aparência
        self.skin_prev.draw(surface)
        self.skin_next.draw(surface)
        self.hair_prev.draw(surface)
        self.hair_next.draw(surface)
        self.eye_prev.draw(surface)
        self.eye_next.draw(surface)
        
        # Mostrar cores atuais
        color_preview_x = WIDTH//2 + 300
        
        # Preview de cor da pele
        pygame.draw.rect(surface, self.current_character.skin_color, 
                        (color_preview_x, 485, 30, 30))
        pygame.draw.rect(surface, Colors.BORDER, 
                        (color_preview_x, 485, 30, 30), 2)
        
        # Preview de cor do cabelo  
        pygame.draw.rect(surface, self.current_character.hair_color, 
                        (color_preview_x, 535, 30, 30))
        pygame.draw.rect(surface, Colors.BORDER, 
                        (color_preview_x, 535, 30, 30), 2)
        
        # Preview de cor dos olhos
        pygame.draw.rect(surface, self.current_character.eye_color, 
                        (color_preview_x, 585, 30, 30))
        pygame.draw.rect(surface, Colors.BORDER, 
                        (color_preview_x, 585, 30, 30), 2)
        
        # Botões de ação
        self.save_character_btn.draw(surface)
        self.back_to_menu_btn.draw(surface)
        
        # Pontos de atributo restantes
        total_points = (self.current_character.strength + self.current_character.intelligence + 
                       self.current_character.agility + self.current_character.charisma +
                       self.current_character.vitality + self.current_character.luck)
        max_points = 60 + self.current_character.skill_points
        remaining = max_points - total_points
        
        points_text = f"Skill Points Remaining: {remaining}"
        points_color = Colors.SUCCESS if remaining >= 0 else Colors.DANGER
        points_surface = font_body.render(points_text, True, points_color)
        surface.blit(points_surface, (WIDTH//2 + 70, 120))
    
    def handle_events(self):
        """Gerenciar eventos"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            
            # Atualizar elementos baseado na tela atual
            if self.current_screen == Screen.LOGIN:
                self._handle_login_events(event, mouse_pos)
            elif self.current_screen == Screen.REGISTER:
                self._handle_register_events(event, mouse_pos)
            elif self.current_screen == Screen.MAIN_MENU:
                self._handle_main_menu_events(event, mouse_pos)
            elif self.current_screen == Screen.CUSTOMIZE:
                self._handle_customize_events(event, mouse_pos)
        
        return True
    
    def _handle_login_events(self, event: pygame.event.Event, mouse_pos: Tuple[int, int]):
        # Input boxes
        self.login_username.handle_event(event, mouse_pos)
        self.login_password.handle_event(event, mouse_pos)
        
        # Botões
        if self.login_button.handle_event(event, mouse_pos):
            success, message = self.login_user(
                self.login_username.text, 
                self.login_password.text
            )
            if success:
                self.current_screen = Screen.MAIN_MENU
                self.create_particles(WIDTH//2, HEIGHT//2 - 50, 20, Colors.SUCCESS)
            else:
                self.create_particles(WIDTH//2, HEIGHT//2 + 80, 10, Colors.DANGER)
        
        elif self.register_button.handle_event(event, mouse_pos):
            self.current_screen = Screen.REGISTER
    
    def _handle_register_events(self, event: pygame.event.Event, mouse_pos: Tuple[int, int]):
        # Input boxes
        self.reg_username.handle_event(event, mouse_pos)
        self.reg_password.handle_event(event, mouse_pos)
        self.reg_confirm.handle_event(event, mouse_pos)
        
        # Botões
        if self.reg_submit.handle_event(event, mouse_pos):
            if self.reg_password.text != self.reg_confirm.text:
                self.create_particles(WIDTH//2, HEIGHT//2 + 80, 10, Colors.DANGER)
            else:
                success, message = self.register_user(
                    self.reg_username.text,
                    self.reg_password.text
                )
                if success:
                    self.current_screen = Screen.LOGIN
                    self.create_particles(WIDTH//2, HEIGHT//2, 20, Colors.SUCCESS)
                else:
                    self.create_particles(WIDTH//2, HEIGHT//2 + 80, 10, Colors.DANGER)
        
        elif self.reg_back.handle_event(event, mouse_pos):
            self.current_screen = Screen.LOGIN
    
    def _handle_main_menu_events(self, event: pygame.event.Event, mouse_pos: Tuple[int, int]):
        if self.customize_btn.handle_event(event, mouse_pos):
            self.current_screen = Screen.CUSTOMIZE
        elif self.inventory_btn.handle_event(event, mouse_pos):
            # TODO: Implementar tela de inventário
            self.create_particles(mouse_pos[0], mouse_pos[1], 15, Colors.WARNING)
        elif self.battle_btn.handle_event(event, mouse_pos):
            # TODO: Implementar tela de batalha
            self.create_particles(mouse_pos[0], mouse_pos[1], 15, Colors.DANGER)
        elif self.logout_btn.handle_event(event, mouse_pos):
            self.logged_in_user = None
            self.current_screen = Screen.LOGIN
    
    def _handle_customize_events(self, event: pygame.event.Event, mouse_pos: Tuple[int, int]):
        # Sliders
        sliders = [
            self.strength_slider, self.intelligence_slider, self.agility_slider,
            self.charisma_slider, self.vitality_slider, self.luck_slider
        ]
        
        for slider in sliders:
            if slider.handle_event(event, mouse_pos):
                self.create_particles(mouse_pos[0], mouse_pos[1], 5, Colors.PRIMARY)
        
        # Botões de aparência
        if self.skin_prev.handle_event(event, mouse_pos):
            skin_colors = self.character_renderer.skin_colors
            current_index = skin_colors.index(self.current_character.skin_color)
            self.current_character.skin_color = skin_colors[(current_index - 1) % len(skin_colors)]
        elif self.skin_next.handle_event(event, mouse_pos):
            skin_colors = self.character_renderer.skin_colors
            current_index = skin_colors.index(self.current_character.skin_color)
            self.current_character.skin_color = skin_colors[(current_index + 1) % len(skin_colors)]
        
        elif self.hair_prev.handle_event(event, mouse_pos):
            hair_colors = self.character_renderer.hair_colors
            current_index = hair_colors.index(self.current_character.hair_color)
            self.current_character.hair_color = hair_colors[(current_index - 1) % len(hair_colors)]
        elif self.hair_next.handle_event(event, mouse_pos):
            hair_colors = self.character_renderer.hair_colors  
            current_index = hair_colors.index(self.current_character.hair_color)
            self.current_character.hair_color = hair_colors[(current_index + 1) % len(hair_colors)]
        
        elif self.eye_prev.handle_event(event, mouse_pos):
            eye_colors = self.character_renderer.eye_colors
            current_index = eye_colors.index(self.current_character.eye_color)
            self.current_character.eye_color = eye_colors[(current_index - 1) % len(eye_colors)]
        elif self.eye_next.handle_event(event, mouse_pos):
            eye_colors = self.character_renderer.eye_colors
            current_index = eye_colors.index(self.current_character.eye_color)
            self.current_character.eye_color = eye_colors[(current_index + 1) % len(eye_colors)]
        
        # Botões de ação
        if self.save_character_btn.handle_event(event, mouse_pos):
            self.save_character()
            self.create_particles(WIDTH//2, HEIGHT - 150, 25, Colors.SUCCESS)
        elif self.back_to_menu_btn.handle_event(event, mouse_pos):
            self.current_screen = Screen.MAIN_MENU
    
    def update(self):
        """Atualizar estado do jogo"""
        self.dt = self.clock.tick(60) / 1000.0  # Delta time em segundos
        
        # Atualizar renderizador de personagem
        self.character_renderer.update(self.dt)
        
        # Atualizar partículas
        self.update_particles(self.dt)
        
        # Atualizar elementos de UI baseado na tela atual
        if self.current_screen == Screen.LOGIN:
            self.login_username.update(self.dt)
            self.login_password.update(self.dt)
            self.login_button.update(self.dt)
            self.register_button.update(self.dt)
        
        elif self.current_screen == Screen.REGISTER:
            self.reg_username.update(self.dt)
            self.reg_password.update(self.dt)
            self.reg_confirm.update(self.dt)
            self.reg_submit.update(self.dt)
            self.reg_back.update(self.dt)
        
        elif self.current_screen == Screen.MAIN_MENU:
            self.customize_btn.update(self.dt)
            self.inventory_btn.update(self.dt)
            self.battle_btn.update(self.dt)
            self.logout_btn.update(self.dt)
        
        elif self.current_screen == Screen.CUSTOMIZE:
            # Atualizar sliders
            sliders = [
                self.strength_slider, self.intelligence_slider, self.agility_slider,
                self.charisma_slider, self.vitality_slider, self.luck_slider
            ]
            for slider in sliders:
                slider.update(self.dt)
            
            # Atualizar botões
            buttons = [
                self.skin_prev, self.skin_next, self.hair_prev, self.hair_next,
                self.eye_prev, self.eye_next, self.save_character_btn, self.back_to_menu_btn
            ]
            for button in buttons:
                button.update(self.dt)
    
    def draw(self):
        """Desenhar tudo na tela"""
        if self.current_screen == Screen.LOGIN:
            self.draw_login_screen(janela)
        elif self.current_screen == Screen.REGISTER:
            self.draw_register_screen(janela)
        elif self.current_screen == Screen.MAIN_MENU:
            self.draw_main_menu(janela)
        elif self.current_screen == Screen.CUSTOMIZE:
            self.draw_customize_screen(janela)
        
        # Desenhar partículas por último
        self.draw_particles(janela)
        
        # Atualizar display
        pygame.display.flip()
    
    def run(self):
        """Loop principal do jogo"""
        running = True
        
        print("🎮 Epic RPG Character Creator v2.0")
        print("🚀 Iniciando jogo...")
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
        
        print("👋 Obrigado por jogar!")
        pygame.quit()

# Executar o jogo
if __name__ == "__main__":
    try:
        game = ModernRPGGame()
        game.run()
    except Exception as e:
        print(f"❌ Erro ao executar o jogo: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
