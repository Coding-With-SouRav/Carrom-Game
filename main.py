import os
import sys
if getattr(sys, 'frozen', False):
    os.environ['PATH'] = sys._MEIPASS + os.pathsep + os.environ['PATH']

# Workaround for NumPy/PyInstaller conflict
try:
    import numpy
    numpy.core._multiarray_umath._reload()
except (ImportError, AttributeError):
    pass

os.environ["NUMPY_NO_CPU_FEATURES"] = "1"
import ctypes
import configparser
import random
import time
import tkinter as tk
from PIL import Image, ImageTk
import math
import pygame
import json

if sys.platform == "win32":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.jeet.CarromGame")

def resource_path(relative_path):

    try:
        base_path = sys._MEIPASS

    except Exception:
        base_path = os.path.abspath(".")
    full_path = os.path.join(base_path, relative_path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Resource not found: {full_path}")
    return full_path

class CarromGame:

    def __init__(self, root):
        self.root = root
        self.root.title("Gold Carrom")
        self.root.geometry("650x760")
        self.root.configure(bg="#393939")
        self.root.resizable(False, False)
        self.data_dir = os.path.join(os.path.expanduser("~"), ".CarromGame")
        os.makedirs(self.data_dir, exist_ok=True)

        if sys.platform == "win32":

            try:
                ctypes.windll.kernel32.SetFileAttributesW(self.data_dir, 2)

            except:
                pass
        self.config_file = os.path.join(self.data_dir, "config.ini")
        self.saved_game_file = os.path.join(self.data_dir, "saved_game.json")
        self.BOARD_SIZE = 600
        self.COIN_RADIUS = 12
        self.STRIKER_RADIUS = 15
        self.STRIKER_SCALE = 1.3
        self.coin_size = self.COIN_RADIUS * 2
        self.STRIKER_Y = self.BOARD_SIZE - 117
        self.CENTER_X = self.BOARD_SIZE // 2
        self.CENTER_Y = self.BOARD_SIZE // 2
        self.BOUNDARY_MARGIN = self.STRIKER_RADIUS + 29
        self.striker_id = None
        self.current_player = 0
        self.slider_drag_offset = 0
        self.aim_line = None
        self.drag_start = None
        self.win_animation_running = False
        self.rubbing_channel = None
        self.prevent_win_animation = False
        self.foul_text_id = None
        self.striker_moving = False
        self.timeout_in_progress = False
        self.slider_drag_sound_playing = False
        self.last_drag_time = 0
        self.drag_sound_timeout = None
        self.prevent_foul_animation = False
        self.prevent_queen_covered_animation = False
        self.board_rotated = False
        self.striker_velocity = [0, 0]
        self.friction = 0.96
        self.coins = []
        self.arc = None
        self.update_angle = 0
        self.animation_running = True
        self.timer_active = False
        self.timer_id = None
        self.timer_start_time = 0
        self.paused = False
        self.pause_frame = None
        self.border_canvas_for_player1 = None
        self.border_rect = None
        self.border_animation_id = None
        self.border_start_time = 0
        self.last_pocketed_coin_for_queen = None
        self.arc_color = "#ff0000"
        self.player_coin_colors = {0: 'white', 1: 'black'}
        self.player_scored_in_turn = False
        self.foul_by_own_coin = False
        self.foul_coin = None
        self.queen_pocketed_last_turn = False
        self.pocketed_player_coins_this_turn = 0
        self.queen_pocketed_this_turn = False
        self.player1_score = 0
        self.player2_score = 0
        self.turn_incomplete = False
        self.rotation_slider = None
        self.rotation_angle = 0
        self.rotation_active = False
        self.player1_queen_covered = False
        self.player2_queen_covered = False
        self.player1_queen_label = None
        self.player2_queen_label = None
        self.original_coin_positions = []
        self.pocket_positions = [
            (45, 48),
            (self.BOARD_SIZE - 50, 50),
            (48, 548),
            (self.BOARD_SIZE - 52, self.BOARD_SIZE - 52)
        ]
        self.POCKET_RADIUS = 12
        pygame.mixer.init()
        self.rubbing_sound = pygame.mixer.Sound(resource_path(r"assets\sounds\dragging.wav"))
        self.coin_collision_sounds = [
            pygame.mixer.Sound(resource_path(r"assets\sounds\collision1.wav")),
            pygame.mixer.Sound(resource_path(r"assets\sounds\collision2.wav")),
            pygame.mixer.Sound(resource_path(r"assets\sounds\collision2.wav"))
        ]
        self.edge_collision_sounds = [
            pygame.mixer.Sound(resource_path(r"assets\sounds\collision1.wav")),
            pygame.mixer.Sound(resource_path(r"assets\sounds\collision2.wav")),
            pygame.mixer.Sound(resource_path(r"assets\sounds\collision2.wav"))
        ]
        self.coin_pocket_sounds = [
            pygame.mixer.Sound(resource_path(r"assets\sounds\coin_pocket1.mp3")),
            pygame.mixer.Sound(resource_path(r"assets\sounds\coin_pocket2.mp3")),
            pygame.mixer.Sound(resource_path(r"assets\sounds\coin_pocket3.mp3"))
        ]
        self.foul_sounds = [
            pygame.mixer.Sound(resource_path(r"assets\sounds\foul.mp3")),
            pygame.mixer.Sound(resource_path(r"assets\sounds\foul.mp3")),
            pygame.mixer.Sound(resource_path(r"assets\sounds\foul.mp3"))
        ]
        self.timer_sound = pygame.mixer.Sound(resource_path(r"assets\sounds\timer.mp3"))
        self.timeout_sound = pygame.mixer.Sound(resource_path(r"assets\sounds\time_out.mp3"))
        self.slider_drag_sound = pygame.mixer.Sound(resource_path(r"assets\sounds\dragging.wav"))
        self.queen_pocketed_sound = pygame.mixer.Sound(resource_path(r"assets\sounds\queen_pocket.mp3"))
        self.queen_covered_sound = pygame.mixer.Sound(resource_path(r"assets\sounds\queen_cover.mp3"))
        self.win_sound = pygame.mixer.Sound(resource_path(r"assets\sounds\win.mp3"))
        self.load_window_geometry()
        select_game_mode_bg_image = Image.open(resource_path(r"assets\images\starting_img.png")).resize((self.BOARD_SIZE, self.BOARD_SIZE))
        self.select_game_mode_bg_photo = ImageTk.PhotoImage(select_game_mode_bg_image)
        self.select_game_mode_bg_label= tk.Label(root, image=self.select_game_mode_bg_photo,bg='#393939')
        self.select_game_mode_bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.main_frame1 = tk.Frame(root, bg="#393939")
        self.main_frame1.place(relx=0.5,rely=0.5,anchor='center', width=300, height=150)
        self.main_frame2 = tk.Frame(root, bg="#393939")
        self.game_mode_frame = tk.Frame(self.main_frame1, bg="#393939")
        self.game_mode_frame.place(relx=0.5, rely=0.5, anchor="center", width=300, height=150)
        self.top_frame = tk.Frame(self.main_frame2, bg="#393939", height=60)
        self.canvas_frame = tk.Frame(self.main_frame2, bg="#393939")
        self.bottom_frame = tk.Frame(self.main_frame2, bg="#393939")
        bg_image = Image.open(resource_path(r"assets\images\carrom_board.png")).resize((self.BOARD_SIZE, self.BOARD_SIZE))
        self.bg_photo = ImageTk.PhotoImage(bg_image)
        self.create_game_mode_ui()
        self.create_ui_elements()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_game_mode_ui(self):
        tk.Label(
            self.game_mode_frame,
            text="Select Game Mode",
            font=("times new roman", 24, "bold"),
            fg="white",
            bg="#393939"
        ).pack(pady=(15, 5))
        self.new_game_btn = tk.Button(
            self.game_mode_frame,
            text="New Game",
            command=self.start_new_game_with_rotation,
            width=15,
            bg="#0BF113",
            fg="black",
            activebackground="#E9DE0B",
            activeforeground="black",
            border=0,
            font=("Arial", 10, "bold")
        )
        self.new_game_btn.pack(pady=5)
        continue_btn = tk.Button(
            self.game_mode_frame,
            text="Continue Playing",
            command=self.load_saved_game,
            width=15,
            bg="#160AF8",
            fg="white",
            activebackground="#426BF2",
            activeforeground="white",
            border=0,
            font=("Arial", 10, "bold")
        )
        continue_btn.pack(pady=5)

        if not os.path.exists(self.saved_game_file):
            continue_btn.config(state=tk.DISABLED)

    def create_ui_elements(self):
        self.player_label_frame = tk.Frame(self.top_frame, bg="#393939")
        self.player_label_frame.pack(fill='x')
        player1_frame = tk.Frame(self.player_label_frame, bg="#393939")
        player1_frame.pack(side='left', padx=(30, 0))
        player2_frame = tk.Frame(self.player_label_frame, bg="#393939")
        player2_frame.pack(side='right', padx=(0, 30))
        self.border_canvas_for_player1 = tk.Canvas(player1_frame, width=60, height=60, bg="#393939", highlightthickness=0)
        self.border_canvas_for_player1.pack(side='left')
        self.border_canvas_for_player2 = tk.Canvas(player2_frame, width=60, height=60, bg="#393939", highlightthickness=0)
        self.border_canvas_for_player2.pack(side='right')
        self.border_poly1 = self.border_canvas_for_player1.create_line(
            0, 0, 0, 0,
            width=3,
            fill="",
            tags="border",
            capstyle=tk.ROUND,
        )
        self.border_rect1 = self.border_canvas_for_player1.create_rectangle(
            5, 5, 55, 55,
            outline="",
            width=5,
            tags="border"
        )
        self.border_poly2 = self.border_canvas_for_player2.create_line(
            0, 0, 0, 0,
            width=3,
            fill="",
            tags="border",
            capstyle=tk.ROUND,
        )
        self.border_rect2 = self.border_canvas_for_player2.create_rectangle(
            5, 5, 55, 55,
            outline="",
            width=5,
            tags="border"
        )
        player_image1 = Image.open(resource_path(r"assets\images\player1.png")).resize((40, 40))
        self.player_photo1 = ImageTk.PhotoImage(player_image1)
        player_image2 = Image.open(resource_path(r"assets\images\player2.png")).resize((40, 40))
        self.player_photo2 = ImageTk.PhotoImage(player_image2)
        self.player_label1 = tk.Label(self.border_canvas_for_player1, bg="#393939", image=self.player_photo1)
        self.player_label1.place(x=30, y=30, anchor="center")
        self.player_label2 = tk.Label(self.border_canvas_for_player2, bg="#393939", image=self.player_photo2)
        self.player_label2.place(x=30, y=30, anchor="center")
        self.canvas = tk.Canvas(self.canvas_frame, width=self.BOARD_SIZE, height=self.BOARD_SIZE, highlightthickness=0)
        self.canvas.pack(side="top", pady=(5, 0))
        striker_img_size = int(2 * self.STRIKER_RADIUS * self.STRIKER_SCALE)
        striker_img = Image.open(resource_path(r"assets\images\striker.png")).resize((striker_img_size, striker_img_size), Image.Resampling.LANCZOS)
        self.striker_photo = ImageTk.PhotoImage(striker_img)
        self.white_coin_img = ImageTk.PhotoImage(Image.open(resource_path(r"assets\images\white_coin.png")).resize((self.coin_size, self.coin_size), Image.Resampling.LANCZOS))
        self.black_coin_img = ImageTk.PhotoImage(Image.open(resource_path(r"assets\images\black_coin.png")).resize((self.coin_size, self.coin_size), Image.Resampling.LANCZOS))
        self.red_coin_img = ImageTk.PhotoImage(Image.open(resource_path(r"assets\images\queen.png")).resize((self.coin_size, self.coin_size), Image.Resampling.LANCZOS))
        white_red_coin_frame1 = tk.Frame(player1_frame, bg="#393939")
        white_red_coin_frame1.pack()
        white_coin_frame = tk.Frame(white_red_coin_frame1, bg="#393939")
        white_coin_frame.pack(side=tk.LEFT)
        red_coin_frame1 = tk.Frame(white_red_coin_frame1, bg="#393939")
        red_coin_frame1.pack(side=tk.LEFT)
        player1_coin_label = tk.Label(white_coin_frame, image=self.white_coin_img, bg="#393939")
        player1_coin_label.pack(padx=5)
        self.player1_score_label = tk.Label(white_coin_frame, text="0", font=('arial, 15'), fg='white', bg="#393939")
        self.player1_score_label.pack(padx=5)
        self.player1_queen_label = tk.Label(red_coin_frame1, image=self.red_coin_img, bg="#393939")
        self.player1_queen_label.pack()
        self.player1_queen_label.pack_forget()
        white_red_coin_frame2 = tk.Frame(player2_frame, bg="#393939")
        white_red_coin_frame2.pack()
        red_coin_frame2 = tk.Frame(white_red_coin_frame2, bg="#393939")
        red_coin_frame2.pack(side=tk.LEFT)
        black_coin_frame = tk.Frame(white_red_coin_frame2, bg="#393939")
        black_coin_frame.pack(side=tk.LEFT)
        player2_coin_label = tk.Label(black_coin_frame, image=self.black_coin_img, bg='#393939')
        player2_coin_label.pack(padx=5)
        self.player2_score_label = tk.Label(black_coin_frame, text="0", font=('arial, 15'), fg='white', bg='#393939')
        self.player2_score_label.pack(padx=5)
        self.player2_queen_label = tk.Label(red_coin_frame2, image=self.red_coin_img, bg='#393939')
        self.player2_queen_label.pack()
        self.player2_queen_label.pack_forget()
        self.start_pause_button = tk.Button(self.player_label_frame,text="||",font=('arial', 15),fg='white',bg='#393939',activebackground='#393939',activeforeground='white',command=self.toggle_pause,bd=0,width=2,height=1)
        self.start_pause_button.place(relx=0.5,rely=0.5,anchor='center')

    def toggle_pause(self):

        if self.paused:
            self.resume_game()
        else:
            self.pause_game()

    def pause_game(self):
        self.paused = True
        self.start_pause_button.config(text="▶")
        self.stop_turn_timer()
        self.animation_running = False
        self.pause_frame = tk.Frame(self.root, bg="#000000", bd=0, highlightthickness=0)
        self.pause_frame.place(relx=0.5, rely=0.5, anchor="center", width=300, height=200)
        pause_label = tk.Label(self.pause_frame, text="GAME PAUSED", font=("Arial", 24, "bold"),
                             fg="white", bg="#000000")
        pause_label.pack(pady=(20, 10))
        resume_btn = tk.Button(
            self.pause_frame,
            text="Resume",
            command=self.resume_game,
            width=15,
            bg="#0BF113",
            fg="black",
            font=("Arial", 12, "bold")
        )
        resume_btn.pack(pady=10)
        menu_btn = tk.Button(
            self.pause_frame,
            text="Main Menu",
            command=self.return_to_main_menu,
            width=15,
            bg="#160AF8",
            fg="white",
            font=("Arial", 12, "bold")
        )
        menu_btn.pack(pady=10)

    def resume_game(self):
        self.paused = False
        self.start_pause_button.config(text="||")

        if self.pause_frame:
            self.pause_frame.destroy()
            self.pause_frame = None
        self.animation_running = True
        self.rotate_arc()

        if self.timer_was_active:
            self.start_turn_timer()

    def return_to_main_menu(self):
        self.save_game_state()

        if self.pause_frame:
            self.pause_frame.destroy()
            self.pause_frame = None
        self.main_frame2.pack_forget()
        self.main_frame1.place(relx=0.5, rely=0.5, anchor='center', width=300, height=150)
        self.paused = False
        self.start_pause_button.config(text="||")

    def start_new_game_with_rotation(self):
        self.main_frame1.place_forget()
        self.main_frame2.pack(fill='both',expand=True)
        self.top_frame.pack(side="top", fill='x', pady=(10, 0))
        self.canvas_frame.pack(side="top")
        self.bottom_frame.pack(side="top", fill='x', pady=(0, 10))
        self.root.after(10, self.initialize_game)

    def initialize_game(self):
        self.timer_active = False
        self.timeout_in_progress = False
        self.create_board()
        self.place_coins()
        self.original_coin_positions = []
        for coin in self.coins:
            self.original_coin_positions.append((coin['x'], coin['y']))
        self.create_rotation_slider()
        self.root.after(200, self.update_scores_periodic)
        self.rotation_active = True

    def load_saved_game(self):

        try:
            self.main_frame1.place_forget()
            self.main_frame2.pack(fill='both',expand=True)
            self.top_frame.pack(side="top", fill='x', pady=(10, 0))
            self.canvas_frame.pack(side="top")
            self.bottom_frame.pack(side="top", fill='x', pady=(0, 10))

            with open(self.saved_game_file, 'r') as f:
                saved_data = json.load(f)
            self.current_player = saved_data.get('current_player', 0)
            self.board_rotated = saved_data.get('board_rotated', False)
            turn_incomplete = saved_data.get('turn_incomplete', False)
            self.player1_queen_covered = saved_data.get('player1_queen_covered', False)
            self.player2_queen_covered = saved_data.get('player2_queen_covered', False)

            if self.player1_queen_covered:
                self.show_player1_queen()

            if self.player2_queen_covered:
                self.show_player2_queen()

            if turn_incomplete:
                self.current_player = 1 - self.current_player
            self.create_board()
            self.create_slider()
            self.root.after(200, self.update_scores_periodic)
            self.coins = []
            for coin_data in saved_data.get('coins', []):
                coin_type = coin_data['type']
                img = self.white_coin_img if coin_type == 'white' else \
                      self.black_coin_img if coin_type == 'black' else \
                      self.red_coin_img
                coin_id = self.canvas.create_image(
                    coin_data['x'],
                    coin_data['y'],
                    image=img
                )
                self.coins.append({
                    'id': coin_id,
                    'x': coin_data['x'],
                    'y': coin_data['y'],
                    'radius': self.COIN_RADIUS,
                    'vx': 0.0,
                    'vy': 0.0,
                    'moving': False,
                    'type': coin_type
                })
            slider_knob_x = saved_data.get('slider_knob_x', 165)
            self.slider_canvas.coords(self.slider_knob, slider_knob_x, 17)

            if turn_incomplete:
                self.rotate_board_180()
            min_board_x = self.STRIKER_RADIUS + 126
            max_board_x = self.BOARD_SIZE - self.STRIKER_RADIUS - 127
            slider_ratio = (slider_knob_x - 18) / (330 - 36)
            striker_x = min_board_x + slider_ratio * (max_board_x - min_board_x)
            self.draw_striker(striker_x, self.STRIKER_Y)
            self.rotate_arc()
            self.root.after(1000, self.start_turn_timer)

        except Exception as e:
            print(f"Error loading saved game: {e}")
            self.start_new_game_with_rotation()

    def save_game_state(self):
        game_state = {
            'current_player': self.current_player,
            'board_rotated': self.board_rotated,
            'coins': [],
            'slider_knob_x': 165,
            'player1_queen_covered': self.player1_queen_covered,
            'player2_queen_covered': self.player2_queen_covered,
            'turn_incomplete': self.striker_moving or any(c['moving'] for c in self.coins)
        }

        if hasattr(self, 'slider_knob') and self.slider_knob:
            knob_x = self.slider_canvas.coords(self.slider_knob)[0]
            game_state['slider_knob_x'] = knob_x
        for coin in self.coins:
            game_state['coins'].append({
                'x': coin['x'],
                'y': coin['y'],
                'type': coin['type']
            })

        try:

            with open(self.saved_game_file, 'w') as f:
                json.dump(game_state, f, indent=4)

        except Exception as e:
            print(f"Error saving game state: {e}")

    def load_window_geometry(self):

        if os.path.exists(self.config_file):
            config = configparser.ConfigParser()
            config.read(self.config_file)

            if "Geometry" in config:
                geometry = config["Geometry"].get("size", "")
                state = config["Geometry"].get("state", "normal")

                if geometry:
                    self.root.geometry(geometry)
                    self.root.update_idletasks()
                    self.root.update()

                if state == "zoomed":
                    self.root.state("zoomed")
                elif state == "iconic":
                    self.root.iconify()

    def save_window_geometry(self):
        config = configparser.ConfigParser()
        config["Geometry"] = {
            "size": self.root.geometry(),
            "state": self.root.state()
        }

        with open(self.config_file, "w") as f:
            config.write(f)

    def on_close(self):

        if hasattr(self, 'canvas') and self.canvas:
            self.save_game_state()
        self.save_window_geometry()
        self.root.destroy()

    def create_ui(self):
        top_frame = tk.Frame(root, bg="#393939",height=60)
        top_frame.pack(side="top",fill='x', pady=(10,0))
        self.player_label_frame = tk.Frame(top_frame,bg="#393939")
        self.player_label_frame.pack(fill='x')
        player1_frame = tk.Frame(self.player_label_frame,bg="#393939")
        player1_frame.pack(side='left',padx=(30,0))
        player2_frame = tk.Frame(self.player_label_frame,bg="#393939")
        player2_frame.pack(side='right',padx=(0,30))
        self.border_canvas_for_player1 = tk.Canvas(player1_frame, width=60, height=60, bg="#393939", highlightthickness=0)
        self.border_canvas_for_player1.pack(side='left')
        self.border_canvas_for_player2 = tk.Canvas(player2_frame, width=60, height=60, bg="#393939", highlightthickness=0)
        self.border_canvas_for_player2.pack(side='right')
        self.border_poly1 = self.border_canvas_for_player1.create_line(
            0, 0, 0, 0,
            width=3,
            fill="",
            tags="border",
            capstyle=tk.ROUND,
        )
        self.border_rect1 = self.border_canvas_for_player1.create_rectangle(
            5, 5, 55, 55,
            outline="",
            width=5,
            tags="border"
        )
        self.border_poly2 = self.border_canvas_for_player2.create_line(
            0, 0, 0, 0,
            width=3,
            fill="",
            tags="border",
            capstyle=tk.ROUND,
        )
        self.border_rect2 = self.border_canvas_for_player2.create_rectangle(
            5, 5, 55, 55,
            outline="",
            width=5,
            tags="border"
        )
        player_image1 = Image.open(resource_path(r"assets\images\player1.png")).resize((40, 40))
        self.player_photo1 = ImageTk.PhotoImage(player_image1)
        player_image2 = Image.open(resource_path(r"assets\images\player2.png")).resize((40, 40))
        self.player_photo2 = ImageTk.PhotoImage(player_image2)
        self.player_label1 = tk.Label(self.border_canvas_for_player1,bg="#393939", image=self.player_photo1)
        self.player_label1.place(x=30, y=30, anchor="center")
        self.player_label2 = tk.Label(self.border_canvas_for_player2,bg="#393939", image=self.player_photo2)
        self.player_label2.place(x=30, y=30, anchor="center")
        self.canvas = tk.Canvas(self.root, width=self.BOARD_SIZE, height=self.BOARD_SIZE, highlightthickness=0)
        self.canvas.pack(side="top",pady=(5,0))
        striker_img_size = int(2 * self.STRIKER_RADIUS * self.STRIKER_SCALE)
        striker_img = Image.open(resource_path(r"assets\images\striker.png")).resize((striker_img_size, striker_img_size), Image.Resampling.LANCZOS)
        self.striker_photo = ImageTk.PhotoImage(striker_img)
        self.white_coin_img = ImageTk.PhotoImage(Image.open(resource_path(r"assets\images\white_coin.png")).resize((self.coin_size , self.coin_size ), Image.Resampling.LANCZOS))
        self.black_coin_img = ImageTk.PhotoImage(Image.open(resource_path(r"assets\images\black_coin.png")).resize((self.coin_size , self.coin_size ), Image.Resampling.LANCZOS))
        self.red_coin_img = ImageTk.PhotoImage(Image.open(resource_path(r"assets\images\queen.png")).resize((self.coin_size , self.coin_size ), Image.Resampling.LANCZOS))
        player1_coin_label = tk.Label(player1_frame,image=self.white_coin_img,bg='#393939')
        player1_coin_label.pack(padx=5)
        self.player1_score_label = tk.Label(player1_frame,text= "0",font=('arial, 15'),fg='white', bg='#393939')
        self.player1_score_label.pack(padx=5)
        player2_coin_label = tk.Label(player2_frame,image=self.black_coin_img,bg='#393939')
        player2_coin_label.pack(padx=5)
        self.player2_score_label = tk.Label(player2_frame,text= "0",font=('arial, 15'),fg='white', bg='#393939')
        self.player2_score_label.pack(padx=5)

    def create_board(self):
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_photo)
        pocket_radius = self.POCKET_RADIUS
        offset = 50
        for x, y in self.pocket_positions:
            self.canvas.create_arc(
                x - pocket_radius, y - pocket_radius,
                x + pocket_radius, y + pocket_radius,
                start=0, extent=359.9,
                fill='',
                outline=''
            )

    def create_rotation_slider(self):
        self.scale_frame = tk.Frame(self.bottom_frame, bg="#393939")
        self.scale_frame.pack(fill=tk.X, padx=40, pady=0)
        self.rotation_slider = tk.Scale(
            self.scale_frame,
            from_=0,
            to=360,
            length=250,
            orient=tk.HORIZONTAL,
            label="Rotate Coins",
            command=self.rotate_coins,
            background="#393939",
            troughcolor="#5757AA",
            highlightthickness=0,
            foreground="white",
            border=2,
            borderwidth=2,
            sliderrelief='flat',
            relief='flat',
            font=('arial', 12),
            activebackground="#2CE33E",
        )
        self.rotation_slider.pack(side='left', padx=(30, 10))
        apply_rotation_btn = tk.Button(
            self.scale_frame,
            text="Apply Rotation",
            command=self.apply_rotation,
            bg="#0CEF32",
            fg="black",
            activebackground="#E9F10C",
            activeforeground="black",
            border=0,
            font=("Arial", 10, "bold")
        )
        apply_rotation_btn.pack(side='left')
        cancel_rotation_btn = tk.Button(
            self.scale_frame,
            text="Cancel Rotation",
            command=self.cancel_rotation,
            bg="#F10B0B",
            fg="white",
            activebackground="#FE8A05",
            activeforeground="white",
            border=0,
            font=("Arial", 10, "bold")
        )
        cancel_rotation_btn.pack(side='left', padx=30)

    def apply_rotation(self):
        self.scale_frame.pack_forget()
        self.update_striker(self.CENTER_X)
        self.rotate_arc()
        self.create_slider()
        self.rotation_active = False
        self.root.after(1000, self.start_turn_timer)

    def cancel_rotation(self):
        self.rotation_slider.set(0)
        for i, coin in enumerate(self.coins):

            if not coin.get('pocketed'):
                orig_x, orig_y = self.original_coin_positions[i]
                coin['x'] = orig_x
                coin['y'] = orig_y
                self.canvas.coords(coin['id'], orig_x, orig_y)
        self.scale_frame.pack_forget()
        self.update_striker(self.CENTER_X)
        self.rotate_arc()
        self.create_slider()
        self.rotation_active = False
        self.root.after(1000, self.start_turn_timer)

    def rotate_coins(self, angle_str):

        if self.striker_moving or any(coin['moving'] for coin in self.coins):
            return
        angle = float(angle_str)
        angle_rad = math.radians(angle)
        red_queen = None
        for coin in self.coins:

            if coin['type'] == 'red' and not coin.get('pocketed'):
                red_queen = coin
                break

        if not red_queen:
            return
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        for coin in self.coins:

            if coin.get('pocketed') or coin['type'] == 'red':
                continue
            dx = coin['initial_dx']
            dy = coin['initial_dy']
            rot_x = dx * cos_a - dy * sin_a
            rot_y = dx * sin_a + dy * cos_a
            new_x = red_queen['x'] + rot_x
            new_y = red_queen['y'] + rot_y
            coin['x'] = new_x
            coin['y'] = new_y
            self.canvas.coords(coin['id'], new_x, new_y)

    def place_coins(self):
        self.coins = []
        self.relative_coin_positions = []
        spacing = self.COIN_RADIUS * 2 + 2
        base_angle_deg = 30
        red_coin_id = self.canvas.create_image(self.CENTER_X, self.CENTER_Y, image=self.red_coin_img)
        self.coins.append({
            'id': red_coin_id,
            'x': self.CENTER_X,
            'y': self.CENTER_Y,
            'radius': self.COIN_RADIUS,
            'vx': 0.0,
            'vy': 0.0,
            'moving': False,
            'type': 'red',
            'initial_dx': 0,
            'initial_dy': 0
        })
        directions = []
        for i in range(6):
            angle_deg = base_angle_deg + i * 60
            angle_rad = math.radians(angle_deg)
            dx = math.cos(angle_rad)
            dy = math.sin(angle_rad)
            directions.append((dx, dy))
        coin_colors = []
        relative_positions = []
        for layer in range(1, 3):
            angle_start = math.radians(base_angle_deg + 4 * 60)
            x = math.cos(angle_start) * spacing * layer
            y = math.sin(angle_start) * spacing * layer
            for dir_index in range(6):
                dx, dy = directions[dir_index]
                for _ in range(layer):
                    relative_positions.append((x, y))
                    x += dx * spacing
                    y += dy * spacing
        for i, (rel_x, rel_y) in enumerate(relative_positions):
            x = self.CENTER_X + rel_x
            y = self.CENTER_Y + rel_y
            color = 'white' if i % 2 == 0 else 'black'
            img = self.white_coin_img if color == 'white' else self.black_coin_img
            coin_id = self.canvas.create_image(x, y, image=img)
            self.coins.append({
                'id': coin_id,
                'x': x,
                'y': y,
                'radius': self.COIN_RADIUS,
                'vx': 0.0,
                'vy': 0.0,
                'moving': False,
                'type': color,
                'initial_dx': rel_x,
                'initial_dy': rel_y
            })

    def create_slider(self):
        track_img = Image.open(resource_path(r"assets\images\slider_bar.png")).resize((330, 35), Image.Resampling.LANCZOS)
        knob_img = Image.open(resource_path(r"assets\images\slider_knob.png")).resize((35, 35), Image.Resampling.LANCZOS)
        self.slider_track_photo = ImageTk.PhotoImage(track_img)
        self.slider_knob_photo = ImageTk.PhotoImage(knob_img)
        self.slider_canvas = tk.Canvas(self.bottom_frame, width=330, height=35, bg="#393939", highlightthickness=0)
        self.slider_canvas.pack(pady=(5, 10))
        self.slider_canvas.create_image(0, 0, anchor="nw", image=self.slider_track_photo)
        self.slider_knob = self.slider_canvas.create_image(165, 17, image=self.slider_knob_photo, anchor="center")
        self.slider_canvas.tag_bind(self.slider_knob, "<ButtonPress-1>", self.start_slider_drag)
        self.slider_canvas.tag_bind(self.slider_knob, "<B1-Motion>", self.slider_drag)
        self.slider_canvas.tag_bind(self.slider_knob, "<ButtonRelease-1>", self.on_slider_release)

    def check_drag_inactivity(self):

        if time.time() - self.last_drag_time > 0.1:
            self.stop_slider_drag_sound()
            self.drag_sound_timeout = None
        else:
            self.drag_sound_timeout = self.root.after(100, self.check_drag_inactivity)

    def on_slider_release(self, event):
        self.stop_slider_drag_sound()
        self.last_drag_time = 0

    def start_slider_drag(self, event):

        if self.timeout_in_progress or self.rotation_active or self.paused:
            self.slider_drag_offset = 0
            return
        self.slider_drag_offset = event.x - self.slider_canvas.coords(self.slider_knob)[0]
        self.slider_drag_sound_playing = False

    def slider_drag(self, event):

        if self.timeout_in_progress or not hasattr(self, 'slider_drag_offset'):
            return
        self.last_drag_time = time.time()

        if not self.drag_sound_timeout:
            self.drag_sound_timeout = self.root.after(100, self.check_drag_inactivity)

        if not self.slider_drag_sound_playing:
            self.slider_drag_sound.play(-1)
            self.slider_drag_sound_playing = True
        new_x = event.x - self.slider_drag_offset
        new_x = max(18, min(new_x, 330 - 18))
        self.slider_canvas.coords(self.slider_knob, new_x, 17)
        min_board_x = self.STRIKER_RADIUS + 126
        max_board_x = self.BOARD_SIZE - self.STRIKER_RADIUS - 127
        slider_ratio = (new_x - 18) / (330 - 36)
        mapped_board_x = min_board_x + slider_ratio * (max_board_x - min_board_x)
        self.update_striker(mapped_board_x)

    def stop_slider_drag_sound(self):

        if self.slider_drag_sound_playing:
            self.slider_drag_sound.stop()
            self.slider_drag_sound_playing = False

        if self.drag_sound_timeout:
            self.root.after_cancel(self.drag_sound_timeout)
            self.drag_sound_timeout = None

    def update_striker(self, x):

        if self.timeout_in_progress:
            return

        if self.striker_moving or any(c['moving'] for c in self.coins):
            return
        x = int(float(x))
        y = self.STRIKER_Y
        safe_x = self.find_safe_striker_position(x)
        self.draw_striker(safe_x, y)
        self.update_arc_position(safe_x)

    def find_safe_striker_position(self, target_x):
        min_x = self.STRIKER_RADIUS + 126
        max_x = self.BOARD_SIZE - self.STRIKER_RADIUS - 127

        if not self.is_colliding_with_coins(target_x, self.STRIKER_Y):
            return target_x
        left_search = target_x
        right_search = target_x
        found_left = False
        found_right = False

        while (left_search >= min_x or right_search <= max_x) and not (found_left or found_right):

            if left_search >= min_x:
                left_search -= 1

                if not self.is_colliding_with_coins(left_search, self.STRIKER_Y):
                    found_left = True

            if right_search <= max_x:
                right_search += 1

                if not self.is_colliding_with_coins(right_search, self.STRIKER_Y):
                    found_right = True

        if found_left and found_right:
            left_dist = abs(target_x - left_search)
            right_dist = abs(target_x - right_search)
            return left_search if left_dist < right_dist else right_search
        elif found_left:
            return left_search
        elif found_right:
            return right_search
        return target_x

    def is_colliding_with_coins(self, x, y):
        for coin in self.coins:

            if coin.get('pocketed'):
                continue
            dx = x - coin['x']
            dy = y - coin['y']
            distance = math.hypot(dx, dy)

            if distance < self.STRIKER_RADIUS + coin['radius']:
                return True
        return False

    def draw_striker(self, x, y):

        if self.striker_id:
            self.canvas.delete(self.striker_id)
        self.striker_id = self.canvas.create_image(x, y, image=self.striker_photo, anchor=tk.CENTER)
        self.canvas.tag_bind(self.striker_id, "<ButtonPress-1>", self.on_striker_press)
        self.canvas.tag_bind(self.striker_id, "<B1-Motion>", self.on_striker_drag)
        self.canvas.tag_bind(self.striker_id, "<ButtonRelease-1>", self.on_striker_release)

    def update_arc_position(self, x):

        if self.arc:
            self.canvas.delete(self.arc)

        if self.animation_running:
            arc_radius = self.STRIKER_RADIUS + 3
            self.arc = self.canvas.create_arc(
                x - arc_radius, self.STRIKER_Y - arc_radius,
                x + arc_radius, self.STRIKER_Y + arc_radius,
                start=self.update_angle, extent=250,
                style=tk.ARC, outline=self.arc_color, width=6
            )

    def rotate_arc(self):

        if self.animation_running:
            self.update_angle = (self.update_angle - 5) % 360
            striker_x = self.canvas.coords(self.striker_id)[0] if self.striker_id else self.get_slider_value()
            self.update_arc_position(striker_x)
            self.root.after(30, self.rotate_arc)

    def on_striker_press(self, event):

        if self.timeout_in_progress or self.rotation_active or self.paused:
            return

        if self.striker_moving or any(c['moving'] for c in self.coins):
            return
        self.drag_start = (event.x, event.y)
        self.update_arc_position(self.get_slider_value())

    def on_striker_drag(self, event):

        if self.timeout_in_progress or self.rotation_active or self.paused:
            return

        if self.striker_moving or any(c['moving'] for c in self.coins):
            return

        if self.arc_color != "#00ff33":
            self.arc_color = "#00ff33"
            self.update_arc_position(self.get_slider_value())
        self.canvas.delete("aim_dot")

        if self.drag_start:
            coords = self.canvas.coords(self.striker_id)

            if not coords:
                return
            striker_x = coords[0]
            striker_y = coords[1]
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            scale_factor = 2.0
            aim_dx = -dx * scale_factor
            aim_dy = -dy * scale_factor
            end_x = striker_x + aim_dx
            end_y = striker_y + aim_dy
            AIM_MARGIN = 22
            end_x = max(AIM_MARGIN, min(end_x, self.BOARD_SIZE - AIM_MARGIN))
            end_y = max(AIM_MARGIN, min(end_y, self.BOARD_SIZE - AIM_MARGIN))
            angle = math.atan2(end_y - striker_y, end_x - striker_x)
            distance = math.hypot(end_x - striker_x, end_y - striker_y)
            spacing = 12
            num_dots = int(distance // spacing)
            for i in range(num_dots):
                d = i * spacing
                t = d / distance if distance != 0 else 0
                dot_x = striker_x + math.cos(angle) * d
                dot_y = striker_y + math.sin(angle) * d
                radius = max(2, 6 * (0.8 - t))
                self.canvas.create_oval(
                    dot_x - radius, dot_y - radius,
                    dot_x + radius, dot_y + radius,
                    fill="white", outline="", tags="aim_dot"
                )
            self.aim_line = "aim_dot"

    def on_striker_release(self, event):

        if self.timeout_in_progress or self.rotation_active:
            return

        if self.drag_start and self.aim_line:
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            distance = math.sqrt(dx*dx + dy*dy)
            MIN_DRAG_DISTANCE = 20

            if distance < MIN_DRAG_DISTANCE:
                self.canvas.delete("aim_dot")
                self.aim_line = None
                self.drag_start = None
                self.arc_color = "#ff0000"  # Restore original arc color
                self.update_arc_position(self.get_slider_value())
                return
            self.animation_running = False

            if self.arc:
                self.canvas.delete(self.arc)
                self.arc = None
            speed = min(distance / 5, 35)
            self.striker_velocity = [
                -dx / distance * speed,
                -dy / distance * speed
            ]
            self.canvas.delete("aim_dot")
            self.aim_line = None
            self.drag_start = None
            self.striker_moving = True
            self.slider_canvas.pack_forget()
            self.move_objects()

        if self.striker_moving:
            self.stop_turn_timer()

    def play_coin_pocket_sound(self):
        sound = random.choice(self.coin_pocket_sounds)
        sound.set_volume(1.0)
        sound.play()

    def move_objects(self):

        if self.striker_moving:
            striker_coords = self.canvas.coords(self.striker_id)

            if striker_coords:
                striker_x, striker_y = striker_coords
                for pocket_x, pocket_y in self.pocket_positions:
                    distance = math.hypot(striker_x - pocket_x, striker_y - pocket_y)

                    if distance < self.POCKET_RADIUS + self.STRIKER_RADIUS / 2:
                        self.animate_into_pocket(self.striker_id, pocket_x, pocket_y, is_striker=True)
                        return
            striker_speed = math.sqrt(self.striker_velocity[0]**2 + self.striker_velocity[1]**2)

            if striker_speed < 80:
                volume = max(0.05, min(1.0, striker_speed / 8))
            else:

                if self.rubbing_channel and self.rubbing_channel.get_busy():
                    self.rubbing_channel.stop()
                    self.rubbing_channel = None
            x, y = self.canvas.coords(self.striker_id)
            vx, vy = self.striker_velocity
            steps = int(max(abs(vx), abs(vy)) // 4) + 1
            dx_step = vx / steps
            dy_step = vy / steps
            for i in range(steps):
                temp_x = x + dx_step * (i + 1)
                temp_y = y + dy_step * (i + 1)
                self.check_collisions(temp_x, temp_y)
            new_x = x + vx
            new_y = y + vy
            self.striker_velocity[0] *= self.friction
            self.striker_velocity[1] *= self.friction
            edge_collision = False

            if new_x < self.BOUNDARY_MARGIN or new_x > self.BOARD_SIZE - self.BOUNDARY_MARGIN:
                self.striker_velocity[0] = -self.striker_velocity[0] * 0.9
                edge_collision = True

            if new_y < self.BOUNDARY_MARGIN or new_y > self.BOARD_SIZE - self.BOUNDARY_MARGIN:
                self.striker_velocity[1] = -self.striker_velocity[1] * 0.9
                edge_collision = True

            if edge_collision and striker_speed > 3:
                self.play_edge_collision_sound(striker_speed)
            new_x = max(self.BOUNDARY_MARGIN, min(new_x, self.BOARD_SIZE - self.BOUNDARY_MARGIN))
            new_y = max(self.BOUNDARY_MARGIN, min(new_y, self.BOARD_SIZE - self.BOUNDARY_MARGIN))
            self.canvas.coords(self.striker_id, new_x, new_y)
        coins_moving = False
        pocket_positions = self.pocket_positions
        active_coins = [c for c in self.coins if not c.get('pocketed')]
        for coin in active_coins:

            if coin['moving']:
                coin['x'] += coin['vx']
                coin['y'] += coin['vy']
                coin['vx'] *= self.friction
                coin['vy'] *= self.friction
                coin_speed = math.sqrt(coin['vx']**2 + coin['vy']**2)
                edge_collision = False

                if coin['x'] < self.BOUNDARY_MARGIN or coin['x'] > self.BOARD_SIZE - self.BOUNDARY_MARGIN:
                    coin['vx'] = -coin['vx'] * 0.9
                    edge_collision = True

                if coin['y'] < self.BOUNDARY_MARGIN or coin['y'] > self.BOARD_SIZE - self.BOUNDARY_MARGIN:
                    coin['vy'] = -coin['vy'] * 0.9
                    edge_collision = True

                if edge_collision and coin_speed > 3:
                    self.play_edge_collision_sound(coin_speed)
                coin['x'] = max(self.BOUNDARY_MARGIN, min(coin['x'], self.BOARD_SIZE - self.BOUNDARY_MARGIN))
                coin['y'] = max(self.BOUNDARY_MARGIN, min(coin['y'], self.BOARD_SIZE - self.BOUNDARY_MARGIN))
                self.canvas.coords(coin['id'], coin['x'], coin['y'])
                speed = math.sqrt(coin['vx']**2 + coin['vy']**2)

                if speed < 0.5:
                    coin['moving'] = False
                else:
                    coins_moving = True
            for coin in active_coins[:]:
                for px, py in pocket_positions:
                    dist_to_pocket = math.hypot(coin['x'] - px, coin['y'] - py)

                    if dist_to_pocket < self.POCKET_RADIUS + coin['radius']:
                        coin['vx'] = 0
                        coin['vy'] = 0
                        coin['moving'] = False
                        coin['pocketed'] = True

                        if coin['type'] == self.player_coin_colors[self.current_player]:
                            self.last_pocketed_coin_for_queen = coin.copy()
                            self.player_scored_in_turn = True
                            self.foul_by_own_coin = True
                            self.foul_coin = coin
                            self.pocketed_player_coins_this_turn += 1
                        self.animate_into_pocket(coin['id'], px, py)
                        active_coins.remove(coin)

                        if coin['type'] == 'red':
                            self.queen_pocketed_sound.play()
                            self.queen_pocketed_this_turn = True
                        break
        self.check_coin_collisions(active_coins)
        striker_speed = math.sqrt(self.striker_velocity[0]**2 + self.striker_velocity[1]**2)

        if striker_speed <= 0.5:
            self.striker_velocity = [0, 0]
        all_coins_slow = True
        for coin in self.coins:
            speed = math.sqrt(coin['vx']**2 + coin['vy']**2)

            if speed > 0.5:
                all_coins_slow = False
            elif speed <= 0.5:
                coin['vx'], coin['vy'] = 0, 0
                coin['moving'] = False

        if self.striker_moving and all_coins_slow and striker_speed <= 0.5:

            if self.rubbing_channel:
                self.rubbing_channel.stop()
                self.rubbing_channel = None
            self.striker_moving = False
            self.animation_running = True
            self.arc_color = "#ff0000"
            self.update_striker(self.get_slider_value())
            self.rotate_arc()
            self.slider_canvas.pack(pady=(5, 20))

            def remove_pocketed():
                for coin in self.coins[:]:

                    if coin.get('pocketed'):
                        self.canvas.delete(coin['id'])
                        self.coins.remove(coin)
            self.root.after(1, remove_pocketed)
            self.update_scores_periodic()
            self.root.after(1, self.end_turn_reset)
            return

        if self.striker_moving or coins_moving:
            self.root.after(20, self.move_objects)

    def animate_into_pocket(self, obj_id, pocket_x, pocket_y, is_striker=False):

        if is_striker:
            self.striker_moving = False
            self.striker_velocity = [0, 0]
            sound = random.choice(self.foul_sounds)
            sound.set_volume(1.0)
            sound.play()
        else:
            self.play_coin_pocket_sound()
        current_x, current_y = self.canvas.coords(obj_id)
        distance = math.hypot(pocket_x - current_x, pocket_y - current_y)
        steps = max(5, int(distance / 5))
        dx = (pocket_x - current_x) / steps
        dy = (pocket_y - current_y) / steps
        scale_factor = 1.0
        scale_step = 0.9 ** (1/steps)

        def move_obj(step=0):

            if step < steps:
                new_x = current_x + dx * (step + 1)
                new_y = current_y + dy * (step + 1)
                scale_factor = scale_step ** step
                self.canvas.coords(obj_id, new_x, new_y)
                self.root.after(10, move_obj, step + 1)
            else:
                self.canvas.coords(obj_id, pocket_x, pocket_y)

                if is_striker:
                    self.handle_foul()
                else:
                    pass
        move_obj()

    def get_slider_value(self):
        knob_x = self.slider_canvas.coords(self.slider_knob)[0]
        slider_ratio = (knob_x - 18) / (330 - 36)
        min_board_x = self.STRIKER_RADIUS + 126
        max_board_x = self.BOARD_SIZE - self.STRIKER_RADIUS - 127
        return min_board_x + slider_ratio * (max_board_x - min_board_x)

    def check_collisions(self, striker_x, striker_y):
        striker_mass = 15
        coin_mass = 5
        for coin in [c for c in self.coins if not c.get('pocketed')]:
            coin_x, coin_y = coin['x'], coin['y']
            dx = coin_x - striker_x
            dy = coin_y - striker_y
            distance = math.sqrt(dx * dx + dy * dy)
            min_distance = self.STRIKER_RADIUS + coin['radius']

            if distance < 1e-10:
                dx = 0.1
                dy = 0.1
                distance = math.sqrt(dx*dx + dy*dy)

            if distance < min_distance:
                relative_speed = abs(coin['vx'] - self.striker_velocity[0]) + abs(coin['vy'] - self.striker_velocity[1])

                if relative_speed > 3:
                    self.play_coin_collision_sound(relative_speed)
                nx = dx / distance
                ny = dy / distance
                rvx = coin['vx'] - self.striker_velocity[0]
                rvy = coin['vy'] - self.striker_velocity[1]
                vel_along_normal = rvx * nx + rvy * ny

                if vel_along_normal > 0:
                    continue
                restitution = 0.9
                impulse = -(1 + restitution) * vel_along_normal
                impulse /= (1/coin_mass + 1/striker_mass)
                impulse_x = impulse * nx
                impulse_y = impulse * ny
                coin['vx'] += impulse_x / coin_mass
                coin['vy'] += impulse_y / coin_mass
                self.striker_velocity[0] -= impulse_x / striker_mass
                self.striker_velocity[1] -= impulse_y / striker_mass
                coin['moving'] = True

    def check_coin_collisions(self, coins):
        for i in range(len(coins)):
            coin1 = coins[i]
            for j in range(i + 1, len(coins)):
                coin2 = coins[j]
                dx = coin1['x'] - coin2['x']
                dy = coin1['y'] - coin2['y']
                distance = math.sqrt(dx*dx + dy*dy)
                min_distance = coin1['radius'] + coin2['radius']

                if distance < 1e-10:
                    dx = 0.1
                    dy = 0.1
                    distance = math.sqrt(dx*dx + dy*dy)

                if distance < min_distance:
                    relative_speed = abs(coin1['vx'] - coin2['vx']) + abs(coin1['vy'] - coin2['vy'])

                    if relative_speed > 3:
                        self.play_coin_collision_sound(relative_speed)
                    nx = dx / distance
                    ny = dy / distance
                    rvx = coin1['vx'] - coin2['vx']
                    rvy = coin1['vy'] - coin2['vy']
                    velocity_along_normal = rvx * nx + rvy * ny

                    if velocity_along_normal > 0:
                        continue
                    restitution = 0.9
                    impulse = -(1 + restitution) * velocity_along_normal / 2
                    coin1['vx'] += impulse * nx
                    coin1['vy'] += impulse * ny
                    coin2['vx'] -= impulse * nx
                    coin2['vy'] -= impulse * ny
                    coin1['moving'] = True
                    coin2['moving'] = True
                    overlap = min_distance - distance
                    correction = overlap / 2
                    coin1['x'] += nx * correction
                    coin1['y'] += ny * correction
                    coin2['x'] -= nx * correction
                    coin2['y'] -= ny * correction

    def play_coin_collision_sound(self, speed):
        sound = random.choice(self.coin_collision_sounds)
        volume = min(1.0, speed / 20)
        sound.set_volume(volume)
        sound.play()

    def play_edge_collision_sound(self, speed):
        sound = random.choice(self.edge_collision_sounds)
        volume = min(1.0, speed / 30)
        sound.set_volume(volume)
        sound.play()

    def animate_striker_pocket(self, pocket_x, pocket_y):
        self.striker_moving = False
        self.check_coin_pocket_collisions()
        striker_x, striker_y = self.canvas.coords(self.striker_id)
        distance = math.hypot(pocket_x - striker_x, pocket_y - striker_y)
        steps = int(distance / 5)

        if steps == 0:
            self.handle_foul()
            return
        dx = (pocket_x - striker_x) / steps
        dy = (pocket_y - striker_y) / steps
        scale_factor = 1.0
        scale_step = 0.9 ** (1/steps)

        def move_striker(step=0):

            if step < steps:
                new_x = striker_x + dx * (step + 1)
                new_y = striker_y + dy * (step + 1)
                scale_factor = scale_step ** step
                self.canvas.coords(self.striker_id, new_x, new_y)
                self.root.after(10, move_striker, step + 1)
            else:
                self.handle_foul()
        move_striker()

    def check_coin_pocket_collisions(self):
        for coin in self.coins:

            if coin.get('pocketed'):
                continue
            for pocket_x, pocket_y in self.pocket_positions:
                dist = math.hypot(coin['x'] - pocket_x, coin['y'] - pocket_y)

                if dist < self.POCKET_RADIUS:
                    coin['pocketed'] = True
                    coin['vx'] = 0
                    coin['vy'] = 0
                    coin['moving'] = False
                    coin['x'] = pocket_x
                    coin['y'] = pocket_y
                    self.canvas.coords(coin['id'], pocket_x, pocket_y)
                    break

    def handle_foul(self):
        self.prevent_win_animation = True
        self.striker_velocity = [0, 0]
        for coin in self.coins:
            coin['vx'] = 0
            coin['vy'] = 0
            coin['moving'] = False
        self.player_scored_in_turn = False

        if self.rubbing_channel:
            self.rubbing_channel.stop()
            self.rubbing_channel = None

        if not self.prevent_foul_animation:
            canvas_x = self.root.winfo_rootx() + self.canvas.winfo_x() + 25
            canvas_y = self.root.winfo_rooty() + self.canvas.winfo_y() + 70
            self.overlay_window = tk.Toplevel(self.root)
            self.overlay_window.overrideredirect(True)
            self.overlay_window.geometry(f"{self.BOARD_SIZE}x{self.BOARD_SIZE}+{canvas_x}+{canvas_y}")
            self.overlay_window.attributes('-alpha', 0.0)
            self.overlay_window.attributes('-topmost', True)
            self.overlay_window.configure(bg='black')
            self.foul_text_label = tk.Label(
                self.overlay_window,
                text="FOUL",
                font=("Arial", 70, "bold"),
                fg="#FF0000",
                bg='black'
            )
            self.foul_text_label.place(relx=0.5, rely=0.5, anchor='center')
        else:
            self.prevent_foul_animation = False
        self.animate_foul_text(0)
        self.fade_overlay(0)
        self.root.after(1500, self.reset_after_foul)

        if self.pocketed_player_coins_this_turn > 0:
            for i in range(self.pocketed_player_coins_this_turn):

                if self.count_player_coins() < 9:
                    pass
            self.player_scored_in_turn = True
        else:
            self.place_penalty_coin()

    def fade_overlay(self, alpha):

        if alpha <= 0.85:

            try:
                self.overlay_window.attributes('-alpha', alpha)
                self.root.after(20, lambda: self.fade_overlay(alpha + 0.05))

            except tk.TclError:
                pass

    def animate_foul_text(self, step):

        try:
            pulse = 10 * math.sin(step * 0.5)
            size = 70 + int(pulse)
            self.foul_text_label.config(font=("Arial", size, "bold"))

            if step < 20:
                self.root.after(50, lambda: self.animate_foul_text(step + 1))

        except (tk.TclError, AttributeError):
            pass

    def reset_after_foul(self):
        self.fade_out_overlay(0.7)

        def remove_and_reset():

            if self.striker_id:
                self.canvas.delete(self.striker_id)
                self.striker_id = None
            self.end_turn_reset()
        self.root.after(1, remove_and_reset)
        self.striker_moving = False
        self.animation_running = True
        self.arc_color = "#ff0000"
        self.update_striker(self.get_slider_value())
        self.rotate_arc()
        self.slider_canvas.pack(pady=(5, 20))
        self.foul_text_label = None

    def fade_out_overlay(self, alpha):

        if alpha >= 0:

            try:
                self.overlay_window.attributes('-alpha', alpha)
                self.root.after(20, lambda: self.fade_out_overlay(alpha - 0.05))

            except tk.TclError:
                pass
        else:

            try:
                self.overlay_window.destroy()
                self.overlay_window = None

            except tk.TclError:
                pass

    def rotate_board_180(self):
        for coin in self.coins:

            if not coin.get('pocketed'):
                coin['x'] = self.BOARD_SIZE - coin['x']
                coin['y'] = self.BOARD_SIZE - coin['y']
                self.canvas.coords(coin['id'], coin['x'], coin['y'])
        self.board_rotated = not self.board_rotated

    def end_turn_reset(self):
        self.timeout_in_progress = False
        self.prevent_win_animation = False
        queen_pocketed = self.queen_pocketed_this_turn
        current_player_score = self.player1_score if self.current_player == 0 else self.player2_score

        if queen_pocketed and current_player_score == 0:
            self.return_queen_to_center()
            self.queen_pocketed_this_turn = False
            self.queen_pocketed_last_turn = False

        if self.queen_pocketed_last_turn and not self.player_scored_in_turn:
            self.return_queen_to_center()

        if self.queen_pocketed_last_turn and self.player_scored_in_turn:

            if self.current_player == 0:
                self.show_player1_queen()
            else:
                self.show_player2_queen()
            self.show_queen_covered_animation()
        self.queen_pocketed_last_turn = self.queen_pocketed_this_turn
        self.queen_pocketed_this_turn = False

        if self.foul_by_own_coin:
            self.return_coin_to_center(self.foul_coin)

            if len(self.coins) >= 8:
                self.return_extra_penalty_coin()
        self.foul_by_own_coin = False
        self.foul_coin = None
        player_color = self.player_coin_colors[self.current_player]
        remaining = [c for c in self.coins if not c.get('pocketed') and c['type'] == player_color]
        queen_unhandled = any(c for c in self.coins if c['type'] == 'red' and not c.get('pocketed'))
        queen_uncovered = (self.current_player == 0 and not self.player1_queen_covered) or \
                        (self.current_player == 1 and not self.player2_queen_covered)

        if not remaining and queen_unhandled and queen_uncovered and self.last_pocketed_coin_for_queen:
            coin_data = self.last_pocketed_coin_for_queen
            coin_data['pocketed'] = False
            coin_data['vx'] = 0.0
            coin_data['vy'] = 0.0
            coin_data['moving'] = False
            center_free = True
            for coin in self.coins:

                if not coin.get('pocketed'):
                    dx = self.CENTER_X - coin['x']
                    dy = self.CENTER_Y - coin['y']

                    if math.hypot(dx, dy) < self.COIN_RADIUS * 2:
                        center_free = False
                        break

            if center_free:
                coin_data['x'] = self.CENTER_X
                coin_data['y'] = self.CENTER_Y
            else:
                CENTER_CIRCLE_RADIUS = 60
                max_attempts = 100
                for _ in range(max_attempts):
                    angle = random.uniform(0, 2 * math.pi)
                    distance = random.uniform(0, CENTER_CIRCLE_RADIUS)
                    x = self.CENTER_X + distance * math.cos(angle)
                    y = self.CENTER_Y + distance * math.sin(angle)
                    collision = False
                    for c in self.coins:

                        if not c.get('pocketed'):
                            dx = x - c['x']
                            dy = y - c['y']

                            if math.hypot(dx, dy) < self.COIN_RADIUS * 2:
                                collision = True
                                break

                    if not collision:
                        coin_data['x'] = x
                        coin_data['y'] = y
                        break
                else:
                    coin_data['x'] = self.CENTER_X
                    coin_data['y'] = self.CENTER_Y
            img = self.white_coin_img if coin_data['type'] == 'white' else self.black_coin_img
            coin_data['id'] = self.canvas.create_image(coin_data['x'], coin_data['y'], image=img)
            self.coins.append(coin_data)
            self.update_scores_periodic()
            self.last_pocketed_coin_for_queen = None
        for coin in self.coins[:]:

            if coin.get('pocketed'):
                self.canvas.delete(coin['id'])
                self.coins.remove(coin)

        if not self.player_scored_in_turn and not queen_pocketed:
            self.rotate_board_180()
            self.current_player = 1 - self.current_player
        self.player_scored_in_turn = False
        self.striker_moving = False
        self.animation_running = True
        self.pocketed_player_coins_this_turn = 0
        self.arc_color = "#ff0000"
        self.update_striker(self.get_slider_value())
        self.rotate_arc()
        self.slider_canvas.pack(pady=(5, 20))

        if not self.win_animation_running:
            self.start_turn_timer()

    def start_turn_timer(self):

        if self.rotation_active or self.paused:
            return

        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.timer_active = True
        self.timer_start_time = time.time()
        self.border_start_time = time.time()
        self.timer_sound.play(-1)
        self.animate_border()

        def update_timer():

            if not self.timer_active:
                return
            elapsed = time.time() - self.timer_start_time
            remaining = max(0, 10 - int(elapsed))

            if remaining == 0:
                self.timer_active = False
                self.timer_sound.stop()
                self.timeout_in_progress = True

                if self.aim_line:
                    self.canvas.delete("aim_dot")
                    self.aim_line = None
                    self.drag_start = None
                    self.arc_color = "#ff0000"
                    self.update_arc_position(self.get_slider_value())
                self.root.after(200, lambda: self.timeout_sound.play())
                self.root.after(2500, self.end_turn_reset)
            else:
                self.timer_id = self.root.after(1000, update_timer)
        update_timer()

    def stop_turn_timer(self):

        if self.rotation_active:
            return
        self.timer_was_active = self.timer_active
        self.timer_active = False

        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        if self.border_animation_id:
            self.root.after_cancel(self.border_animation_id)
            self.border_animation_id = None
        self.timer_sound.stop()

    def animate_border(self):

        if not self.timer_active:
            return
        elapsed = time.time() - self.border_start_time
        remaining = max(0, 10 - elapsed)

        if remaining <= 0:
            self.border_canvas_for_player1.itemconfig(self.border_poly1, fill="")
            self.border_canvas_for_player2.itemconfig(self.border_poly2, fill="")
            return

        if self.current_player == 0:
            border_canvas = self.border_canvas_for_player1
            border_poly = self.border_poly1
        else:
            border_canvas = self.border_canvas_for_player2
            border_poly = self.border_poly2
        green_val = int(255 * (remaining / 10))
        red_val = int(255 * (1 - remaining / 10))
        color = f'#{red_val:02x}{green_val:02x}00'
        total_perimeter = 200
        current_perimeter = total_perimeter * (remaining / 10.0)
        points = [30, 5]

        if current_perimeter > 0:
            top_length = min(25, current_perimeter)
            points.extend([30 + top_length, 5])
            current_perimeter -= top_length

        if current_perimeter > 0:
            right_length = min(50, current_perimeter)
            points.extend([55, 5 + right_length])
            current_perimeter -= right_length

        if current_perimeter > 0:
            bottom_length = min(50, current_perimeter)
            points.extend([55 - bottom_length, 55])
            current_perimeter -= bottom_length

        if current_perimeter > 0:
            left_length = min(50, current_perimeter)
            points.extend([5, 55 - left_length])
            current_perimeter -= left_length

        if current_perimeter > 0:
            top_left_length = min(25, current_perimeter)
            points.extend([5 + top_left_length, 5])
        border_canvas.coords(border_poly, *points)
        border_canvas.itemconfig(border_poly, fill=color)
        other_border = self.border_poly2 if self.current_player == 0 else self.border_poly1
        other_canvas = self.border_canvas_for_player2 if self.current_player == 0 else self.border_canvas_for_player1
        other_canvas.itemconfig(other_border, fill="")
        self.border_animation_id = self.root.after(50, self.animate_border)

    def return_coin_to_center(self, coin):
        coin['pocketed'] = False
        coin['x'] = self.CENTER_X
        coin['y'] = self.CENTER_Y
        self.canvas.coords(coin['id'], coin['x'], coin['y'])
        self.canvas.itemconfig(coin['id'], state=tk.NORMAL)

    def return_extra_penalty_coin(self):
        player_coin_type = self.player_coin_colors[self.current_player]
        for coin in self.coins:

            if coin.get('pocketed') and coin['type'] == player_coin_type:
                self.return_coin_to_center(coin)
                break

    def place_penalty_coin(self):

        if self.count_player_coins() >= 9:
            return
        player_color = self.player_coin_colors[self.current_player]
        img = self.white_coin_img if player_color == 'white' else self.black_coin_img
        CENTER_CIRCLE_RADIUS = 60
        max_attempts = 100
        placed = False
        for _ in range(max_attempts):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, CENTER_CIRCLE_RADIUS)
            x = self.CENTER_X + distance * math.cos(angle)
            y = self.CENTER_Y + distance * math.sin(angle)
            collision = False
            for coin in self.coins:

                if not coin.get('pocketed'):
                    dx = x - coin['x']
                    dy = y - coin['y']
                    distance_to_coin = math.hypot(dx, dy)

                    if distance_to_coin < self.COIN_RADIUS * 2:
                        collision = True
                        break

            if not collision:
                coin_id = self.canvas.create_image(x, y, image=img)
                self.coins.append({
                    'id': coin_id,
                    'x': x,
                    'y': y,
                    'radius': self.COIN_RADIUS,
                    'vx': 0.0,
                    'vy': 0.0,
                    'moving': False,
                    'type': player_color
                })
                placed = True
                self.update_scores_periodic()
                break

        if not placed:
            coin_id = self.canvas.create_image(self.CENTER_X, self.CENTER_Y, image=img)
            self.coins.append({
                'id': coin_id,
                'x': self.CENTER_X,
                'y': self.CENTER_Y,
                'radius': self.COIN_RADIUS,
                'vx': 0.0,
                'vy': 0.0,
                'moving': False,
                'type': player_color
            })
            self.update_scores_periodic()

    def count_player_coins(self):
        player_coin_type = self.player_coin_colors[self.current_player]
        count = 0
        for coin in self.coins:

            if not coin.get('pocketed') and coin['type'] == player_coin_type:
                count += 1
        return count

    def update_scores_periodic(self):
        white_count = sum(1 for coin in self.coins

                         if coin['type'] == 'white' and not coin.get('pocketed'))
        black_count = sum(1 for coin in self.coins

                         if coin['type'] == 'black' and not coin.get('pocketed'))
        self.player1_score = 9 - white_count
        self.player2_score = 9 - black_count
        self.player1_score_label.config(text=str(self.player1_score))
        self.player2_score_label.config(text=str(self.player2_score))

        if self.player1_score == 9 or self.player2_score == 9:

            try:

                if os.path.exists(self.saved_game_file):
                    os.remove(self.saved_game_file)

            except Exception as e:
                print(f"Error deleting saved game: {e}")

        if self.player1_score == 9 and (self.player1_queen_covered or self.player2_queen_covered or not self.queen_pocketed_this_turn):
            self.prevent_foul_animation_once()
            self.prevent_queen_covered_animation_once()
            self.show_win_animation("PLAYER 1")
        elif self.player2_score == 9 and (self.player1_queen_covered or self.player2_queen_covered or not self.queen_pocketed_this_turn):
            self.prevent_foul_animation_once()
            self.prevent_queen_covered_animation_once()
            self.show_win_animation("PLAYER 2")

    def return_queen_to_center(self):
        CENTER_CIRCLE_RADIUS = 60
        max_attempts = 100
        center_free = True
        for coin in self.coins:
            dx = self.CENTER_X - coin['x']
            dy = self.CENTER_Y - coin['y']
            distance = math.hypot(dx, dy)

            if distance < self.COIN_RADIUS * 2.5:
                center_free = False
                break

        if center_free:
            x, y = self.CENTER_X, self.CENTER_Y
        else:
            placed = False
            for _ in range(max_attempts):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(0, CENTER_CIRCLE_RADIUS)
                x = self.CENTER_X + distance * math.cos(angle)
                y = self.CENTER_Y + distance * math.sin(angle)
                collision = False
                for coin in self.coins:
                    dx = x - coin['x']
                    dy = y - coin['y']
                    distance_to_coin = math.hypot(dx, dy)

                    if distance_to_coin < self.COIN_RADIUS * 2.5:
                        collision = True
                        break

                if not collision:
                    placed = True
                    break

            if not placed:
                x, y = self.CENTER_X, self.CENTER_Y
        coin_id = self.canvas.create_image(x, y, image=self.red_coin_img)
        self.coins.append({
            'id': coin_id,
            'x': x,
            'y': y,
            'radius': self.COIN_RADIUS,
            'vx': 0.0,
            'vy': 0.0,
            'moving': False,
            'type': 'red'
        })

    def show_player1_queen(self):
        self.player1_queen_covered = True
        self.player1_queen_label.pack()

    def show_player2_queen(self):
        self.player2_queen_covered = True
        self.player2_queen_label.pack()

    def show_queen_covered_animation(self):

        if self.prevent_queen_covered_animation:
            self.prevent_queen_covered_animation = False
            return
        self.root.after(1,self.stop_turn_timer)
        self.queen_covered_sound.play()
        canvas_x = self.root.winfo_rootx() + self.canvas.winfo_x() + 25
        canvas_y = self.root.winfo_rooty() + self.canvas.winfo_y() + 70
        self.queen_overlay_window = tk.Toplevel(self.root)
        self.queen_overlay_window.overrideredirect(True)
        self.queen_overlay_window.geometry(f"{self.BOARD_SIZE}x{self.BOARD_SIZE}+{canvas_x}+{canvas_y}")
        self.queen_overlay_window.attributes('-alpha', 0.0)
        self.queen_overlay_window.attributes('-topmost', True)
        self.queen_overlay_window.configure(bg='#00FF00')  # Green background
        self.queen_text_label = tk.Label(
            self.queen_overlay_window,
            text="QUEEN COVERED",
            font=("Arial", 45, "bold"),
            fg="#0905F8",  # Dark green text
            bg='#00FF00'   # Green background
        )
        self.queen_text_label.place(relx=0.5, rely=0.5, anchor='center')
        self.fade_in_queen_overlay(0)

        def fade_out_queen_overlay(alpha):

            if alpha >= 0:

                try:
                    self.queen_overlay_window.attributes('-alpha', alpha)
                    self.root.after(20, lambda: fade_out_queen_overlay(alpha - 0.05))

                except tk.TclError:
                    pass
            else:

                try:
                    self.queen_overlay_window.destroy()
                    self.queen_overlay_window = None

                except tk.TclError:
                    pass
                self.root.after(100, self.start_turn_timer)
        self.root.after(2000, lambda: fade_out_queen_overlay(0.7))

    def fade_in_queen_overlay(self, alpha):

        if alpha <= 0.7:

            try:
                self.queen_overlay_window.attributes('-alpha', alpha)
                self.root.after(20, lambda: self.fade_in_queen_overlay(alpha + 0.05))

            except tk.TclError:
                pass

    def show_win_animation(self, winner_name="YOU"):
        self.win_animation_running = True
        self.stop_turn_timer()
        self.win_sound.play()
        canvas_x = self.root.winfo_rootx() + self.canvas.winfo_x() + 25
        canvas_y = self.root.winfo_rooty() + self.canvas.winfo_y() + 70
        self.win_overlay_window = tk.Toplevel(self.root)
        self.win_overlay_window.overrideredirect(True)
        self.win_overlay_window.geometry(f"{self.BOARD_SIZE}x{self.BOARD_SIZE}+{canvas_x}+{canvas_y}")
        self.win_overlay_window.attributes('-alpha', 0.0)
        self.win_overlay_window.attributes('-topmost', True)
        self.win_overlay_window.configure(bg='#00FF00')  # Faded green
        self.win_text_label = tk.Label(
            self.win_overlay_window,
            text=f"CONGRATULATIONS\n{winner_name} WINNN...!",
            font=("Arial", 45, "bold"),
            fg="#0905F8",
            bg="#00FF00"
        )
        self.win_text_label.place(relx=0.5, rely=0.5, anchor='center')
        self.animate_win_text(0)
        self.fade_in_win_overlay(0)
        self.root.after(5000, self.after_game_complete)

    def animate_win_text(self, step):

        try:
            pulse = 10 * math.sin(step * 0.5)
            size = 45 + int(pulse)
            self.win_text_label.config(font=("Arial", size, "bold"))

            if step < 20:
                self.root.after(50, lambda: self.animate_win_text(step + 1))

        except (tk.TclError, AttributeError):
            pass

    def fade_in_win_overlay(self, alpha):

        if alpha <= 0.85:

            try:
                self.win_overlay_window.attributes('-alpha', alpha)
                self.root.after(20, lambda: self.fade_in_win_overlay(alpha + 0.05))

            except tk.TclError:
                pass

    def after_game_complete(self):

        try:
            self.win_overlay_window.destroy()

        except tk.TclError:
            pass
        self.main_frame2.pack_forget()
        self.new_game_frame =tk.Frame(self.root, bg='#393939',width=20,height=20)
        self.new_game_frame.place(relx=0.5, rely=0.5, anchor='center', width=150, height=75)
        self.new_game_btn_after_game_complete = tk.Button(self.new_game_frame,
                   text="NEW GAME",
                   font=("Arial", 12, "bold"),
                   fg="black",
                   bg="#29D01A",
                   activebackground= "#B2D01A",
                   activeforeground="black",
                   bd=0,
                   command=self.start_new_game
                   )
        self.new_game_btn_after_game_complete.place(relx=0.5, rely=0.5, anchor='center')

    def start_new_game(self):
        self.stop_turn_timer()
        self.timer_active = False
        self.timeout_in_progress = False
        self.border_canvas_for_player1.pack(side='left')
        self.border_canvas_for_player2.pack(side='right')
        self.new_game_frame.place_forget()
        self.main_frame1.place_forget()
        self.main_frame2.pack(fill='both',expand=True)
        self.top_frame.pack(side="top", fill='x', pady=(10, 0))
        self.canvas_frame.pack(side="top")
        self.bottom_frame.pack(side="top", fill='x', pady=(0, 10))
        self.slider_canvas.pack_forget()
        self.animation_running = False

        if self.arc:
            self.canvas.delete(self.arc)
            self.arc = None
        self.root.after(10, self.new_game_ui)

    def new_game_ui(self):
        self.create_board()
        self.place_coins()
        self.original_coin_positions = []
        for coin in self.coins:
            self.original_coin_positions.append((coin['x'], coin['y']))
        self.create_rotation_slider()
        self.root.after(200, self.update_scores_periodic)
        self.rotation_active = True

    def prevent_foul_animation_once(self):
        self.prevent_foul_animation = True

    def prevent_queen_covered_animation_once(self):
        self.prevent_queen_covered_animation = True

if __name__ == "__main__":
    root = tk.Tk()

    try:
        icon_path = resource_path(r"assets\icon.ico")
        icon_img = Image.open(icon_path)
        icon_photo = ImageTk.PhotoImage(icon_img)
        root.wm_iconphoto(True, icon_photo)

    except Exception as e:
        print(f"Error loading icon: {e}")
    app = CarromGame(root)
    root.mainloop()
