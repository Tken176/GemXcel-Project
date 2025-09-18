import os
import json
import time
from datetime import date, timedelta
import random
import config
import subprocess
import sys

class GameState:
    def __init__(self, file_path): # file_path sẽ là config.DATA_FILE_PATH
        self.click_sound = None
        self.owned_avatars = []
        self.avatar_path = os.path.join(config.AVATAR_DIR, "default_avatar.png")
        self.file_path = file_path
        self.completed_lessons = []
        self.exercise_state = None
        self.point = None
        self.energy = None
        self.streak = None
        self.the_streak = None
        self.last_day = None
        self.collected_gems = []
        self.viewing_gem = None
        self.just_closed_detail = False

        self.purchase_message = ""
        self.message_timer = 0
        self.buatangtoc_timer = None
        self.last_point_pack_time = 0

        self.current_screen = "home"

        self.current_lesson_id = 1
        self.current_page_index = 0
        self.quiz_state = {
            "bai": 1,
            "index": 0,
            "feedback": "",
            "answered": False,
            "selected": None
        }

        self.read_data()

        # Import GEM_TYPES here to avoid circular dependency with config.py
        from config import GEM_TYPES
        self.GEM_TYPES = GEM_TYPES

    def set_temp_screen(self, screen_name):
        self.temp_screen = screen_name

    def read_data(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.completed_lessons = data.get("completed_lessons", [])
                self.point = data.get("point", 100)
                self.energy = data.get("energy", 10)
                self.streak = data.get("streak", 1)
                self.the_streak = data.get("the_streak", 0)
                self.owned_avatars = data.get("owned_avatars", [self.avatar_path])
                
                # THÊM DÒNG NÀY ĐỂ LOAD AVATAR_PATH
                self.avatar_path = data.get("avatar_path", config.DEFAULT_DIR)

                last_day_str = data.get("last_day", date.today().isoformat())
                try:
                    self.last_day = date.fromisoformat(last_day_str)
                except ValueError: # Fallback if date string is invalid
                    self.last_day = date.today()

                self.collected_gems = data.get("collected_gems", [])
            except json.JSONDecodeError:
                print(f"Error decoding {self.file_path}. Data might be corrupted. Resetting to defaults.")
                self._set_default_data()
            except Exception as e:
                print(f"An unexpected error occurred while reading {self.file_path}: {e}. Resetting to defaults.")
                self._set_default_data()
        else:
            print(f"Data file not found at {self.file_path}. Creating with default values.")
            self._set_default_data()
            self.write_data() # Save defaults immediately

    def _set_default_data(self):
        self.completed_lessons = []
        self.point = 100
        self.energy = 10
        self.streak = 1
        self.the_streak = 0
        self.last_day = date.today()
        self.collected_gems = []
        self.owned_avatars = [self.avatar_path]
        self.avatar_path = config.DEFAULT_DIR

    def write_data(self):
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            data_to_save = {
                "completed_lessons": self.completed_lessons,
                "point": self.point,
                "energy": self.energy,
                "streak": self.streak,
                "the_streak": self.the_streak,
                "last_day": (self.last_day.isoformat() if self.last_day else date.today().isoformat()),
                "owned_avatars": self.owned_avatars,
                "avatar_path": self.avatar_path,
                "collected_gems": [{k: v for k, v in gem.items() if k != "rect"} for gem in self.collected_gems]
            }
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Lỗi khi ghi dữ liệu: {e}")

    def show_message(self, msg, duration=3):
        self.purchase_message = msg
        self.message_timer = time.time()

    # --- Background Update Threads ---
    def update_energy_thread(self):
        while True:
            time.sleep(60 * 20)  # Cập nhật mỗi 20 phút
            if self.energy < 10:
                self.energy += 1
            self.write_data()

    def update_point_thread(self):
        while True:
            sleep_time = 1 if self.buatangtoc_timer and time.time() < self.buatangtoc_timer else 5
            time.sleep(sleep_time)
            if self.point < 999999:
                self.point += 1
            self.write_data()

    def update_streak_thread(self):
        while True:
            time.sleep(10) # Check every 10 seconds
            today = date.today()
            if today != self.last_day:
                if today - self.last_day == timedelta(days=1):
                    self.streak += 1
                    self.point += 10 # Reward for maintaining streak
                else:
                    if self.the_streak > 0:
                        self.the_streak -= 1
                    else:
                        self.streak = 1 # Reset streak
                self.last_day = today
                self.write_data()

    # --- Game Actions (can be called by UI elements) ---
    def purchase_item(self, item_name, price):
        # Kiểm tra xem có đủ điểm không
        if self.point < price:
            self.show_message("Không đủ điểm!")
            return
        
        # Xử lý từng loại item
        if item_name == "Thẻ bảo vệ streak":
            self.the_streak += 1
            self.point -= price
            self.show_message("Đã mua thẻ bảo vệ streak!")
            
        elif item_name == "Tinh thể kỳ ảo(V.I.P)":
            # Logic mua tinh thể VIP
            missing_gems = [g for g in self.GEM_TYPES 
                          if not any(cg["id"] == g["id"] for cg in self.collected_gems)]
            
            if missing_gems:
                new_gem = random.choice(missing_gems).copy()
                new_gem["collected_date"] = date.today().isoformat()
                self.collected_gems.append(new_gem)
                self.point -= price
                self.show_message(f"Bạn nhận được: {new_gem['name']}!")
            else:
                self.show_message("Bạn đã sưu tập đủ 12 viên đá!")
                
        elif item_name == "Tinh thể kỳ ảo":
            # Logic mua tinh thể thường
            new_gem = random.choice(self.GEM_TYPES).copy()
            new_gem["collected_date"] = date.today().isoformat()
            self.collected_gems.append(new_gem)
            self.point -= price
            self.show_message(f"Bạn nhận được: {new_gem['name']}!")
            
            # Kiểm tra nếu đã đủ bộ sưu tập
            if len(set(g["id"] for g in self.collected_gems)) >= len(self.GEM_TYPES):
                self.show_message("Bạn đã sưu tập đủ 12 viên đá!")
                self.point += price
        
        elif item_name == "Gói điểm":
            # Logic mua gói điểm
            current_time = time.time()
            if current_time - self.last_point_pack_time >= 10:
                bonus = random.randint(0, 200)
                self.point += bonus - price  # Trừ điểm mua + cộng điểm nhận được
                self.last_point_pack_time = current_time
                self.show_message(f"Bạn nhận được {bonus} điểm!")
            else:
                remaining = int(10 - (current_time - self.last_point_pack_time))
                self.show_message(f"Vui lòng đợi {remaining} giây để mua lại")
                
        elif item_name == "Hồi năng lượng":
            # Logic hồi năng lượng
            if self.energy >= 10:
                self.show_message("Năng lượng đã đầy!")
            else:
                self.energy = 10
                self.point -= price
                self.show_message("Đã hồi đầy năng lượng!")
                
        elif item_name == "Bùa tăng tốc điểm":
            # Logic bùa tăng tốc
            self.buatangtoc_timer = time.time() + 60
            self.point -= price
            self.show_message("Điểm sẽ tăng nhanh trong 60 giây!")
            
        self.write_data()  # Lưu dữ liệu sau mỗi giao dịch
    def complete_lesson(self, lesson_id):
        if lesson_id not in self.completed_lessons:
            self.completed_lessons.append(lesson_id)
            self.write_data()
    def start_lesson(self, lesson_id):
        if self.energy > 0:
            self.energy -= 1
            self.current_lesson_id = lesson_id
            self.current_page_index = 0
            self.write_data()
            # self.show_message(f"Bắt đầu Bài {lesson_id}!")
            return True
        else:
            self.show_message("Không đủ năng lượng!")
            return False

    def goto_next_page(self):
        if self.current_page_index < len(self.lesson_pages) - 1:
            self.current_page_index += 1
        self.show_message("")  # Clear message

    def goto_prev_page(self):
        if self.current_page_index > 0:
            self.current_page_index -= 1
        self.show_message("")  # Clear message

    def start_quiz(self, lesson_id):
        self.quiz_state["bai"] = lesson_id
        self.quiz_state["index"] = 0
        self.reset_quiz_question_state()

    def reset_quiz_question_state(self):
        self.quiz_state["feedback"] = ""
        self.quiz_state["answered"] = False
        self.quiz_state["selected"] = None

    def quiz_next_question(self):
        self.quiz_state["index"] += 1
        self.reset_quiz_question_state()

    def quiz_finish_session(self, quiz_passed_bonus=0):
        self.point += quiz_passed_bonus
        if self.quiz_state["bai"] not in self.completed_lessons:
            self.completed_lessons.append(self.quiz_state["bai"])
        self.show_message("Hoàn thành bài tập!")
        self.reset_quiz_question_state()
        self.write_data()
    def switch_to_lesson_screen(self, screen_name):
        self.current_screen = screen_name
        self.quiz_state = {
            "bai": None,
            "index": 0,
            "answered": False,
            "selected": None,
            "feedback": ""
        }
        self.write_data()