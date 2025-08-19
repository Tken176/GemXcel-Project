import pygame
import config
import ui_elements
import time
import random
import os
import json
import importlib
    
correct_sound = None
wrong_sound = None

def set_sounds(correct, wrong):
    global correct_sound, wrong_sound
    correct_sound = correct
    wrong_sound = wrong

def draw_quiz_screen(screen, font_title, font, font_small, colors, game_state, handle_button_click_callback, all_quiz_data):
    # Kiểm tra và cập nhật dữ liệu quiz nếu cần
    current_bai = game_state.quiz_state["bai"]
    if not hasattr(game_state, 'last_quiz_update') or game_state.last_quiz_update < os.path.getmtime(config.QUIZ_DATA_FILE_PATH):
        reload_quiz_data(game_state)
        game_state.last_quiz_update = time.time()
    
    # Kiểm tra dữ liệu quiz hợp lệ
    if not isinstance(all_quiz_data, dict) or current_bai not in all_quiz_data or not all_quiz_data[current_bai]:
        ui_elements.draw_text_centered(
            screen, 
            "Không có bài tập cho bài này.", 
            config.WIDTH//2, 
            config.HEIGHT//2, 
            font, 
            colors["text"]
        )
        return
    
    current_index = game_state.quiz_state["index"]
    q = all_quiz_data[current_bai][current_index]
    
    # Background - chỉ fill phần bên phải (không đè lên menu)
    quiz_area_x = 190  # Bắt đầu từ sau menu
    quiz_area_width = config.WIDTH - 190
    pygame.draw.rect(screen, (235, 255, 235), (quiz_area_x, 0, quiz_area_width, config.HEIGHT))
    
    # Tính toán vị trí các thành phần dựa trên khu vực quiz
    content_x = quiz_area_x + 20  # Padding từ menu
    content_width = quiz_area_width - 40  # Trừ padding 2 bên
    
    # Thanh tiến trình
    progress_y = 30
    progress = (current_index + 1) / len(all_quiz_data[current_bai])
    pygame.draw.rect(screen, (220, 220, 220), (content_x, progress_y, content_width, 12), border_radius=6)
    pygame.draw.rect(screen, (100, 180, 100), (content_x, progress_y, int(content_width * progress), 12), border_radius=6)
    
    # Hiển thị số câu hỏi
    question_count_text = f"Câu hỏi {current_index + 1}/{len(all_quiz_data[current_bai])}"
    counter = font_small.render(question_count_text, True, (80, 120, 80))
    screen.blit(counter, (config.WIDTH - counter.get_width() - 30, progress_y - 5))
    
    # Thẻ câu hỏi
    question_card_y = progress_y + 30
    question_card_height = 120
    ui_elements.draw_rounded_rect(screen, (255, 255, 255), 
                                 (content_x, question_card_y, content_width, question_card_height), 
                                 20, 2, (220, 220, 220))
    
    # Nội dung câu hỏi
    question_lines = ui_elements.draw_multiline_text(
        screen, q["question"],
        content_x + 20, question_card_y + 20, font, (70, 70, 70), content_width - 40
    )
    
    # Các lựa chọn trả lời
    buttons = []
    choices_start_y = question_card_y + question_card_height + 20
    choice_height = 55
    choice_spacing = 10
    
    for idx, choice in enumerate(q["choices"]):
        choice_y = choices_start_y + idx * (choice_height + choice_spacing)
        
        # Xác định màu nút dựa trên trạng thái trả lời
        if game_state.quiz_state["answered"]:
            if idx == q["answer"]:
                color = (100, 200, 100)  # Đúng
            elif idx == game_state.quiz_state["selected"]:
                color = (255, 120, 120)  # Sai
            else:
                color = (220, 220, 220)  # Các lựa chọn khác
        else:
            color = (200, 230, 200)  # Màu mặc định
            
        btn = ui_elements.Button(
            content_x, choice_y, content_width, choice_height,
            choice,
            lambda i=idx: handle_button_click_callback(
                check_answer_mcq,
                game_state,
                current_bai,
                current_index,
                i
            ),
            color, 15, None
        )
        buttons.append(btn)
    
    # Vẽ tất cả nút
    for button in buttons:
        button.draw(screen)
    
    # Hiển thị phản hồi nếu đã trả lời
    if game_state.quiz_state["answered"]:
        feedback = game_state.quiz_state["feedback"]
        explanation = q.get("explanation", "")
        
        # Tính toán vị trí phản hồi (sau các lựa chọn)
        feedback_y = choices_start_y + len(q["choices"]) * (choice_height + choice_spacing) + 20
        
        # Hiển thị phản hồi
        ui_elements.draw_text_centered(
            screen, 
            feedback, 
            quiz_area_x + quiz_area_width//2,  # Căn giữa khu vực quiz
            feedback_y, 
            font, 
            (100, 180, 100) if feedback == "Chính xác!" else (255, 100, 100)
        )
        
        # Hiển thị giải thích nếu có
        explanation_height = 0
        if explanation:
            explanation_y = feedback_y + 30
            explanation_lines_count = ui_elements.draw_multiline_text(
                screen, 
                f"Giải thích: {explanation}", 
                content_x, 
                explanation_y, 
                font_small, 
                (100, 100, 100), 
                content_width
            )
            # Tính chiều cao dựa trên số dòng (nếu trả về int) hoặc độ dài văn bản
            if isinstance(explanation_lines_count, int):
                explanation_height = explanation_lines_count * 20 + 10
            else:
                # Ước tính dựa trên độ dài văn bản
                estimated_lines = max(1, len(explanation) // 80)  # Khoảng 80 ký tự/dòng
                explanation_height = estimated_lines * 20 + 10
            
        # Nút câu tiếp theo hoặc hoàn thành
        button_width = 180
        button_height = 45
        next_btn_y = feedback_y + 40 + explanation_height
        
        # Đảm bảo nút không bị đẩy ra khỏi màn hình
        max_button_y = config.HEIGHT - button_height - 20
        if next_btn_y > max_button_y:
            next_btn_y = max_button_y

        button_x = quiz_area_x + (quiz_area_width - button_width) // 2  # Căn giữa khu vực quiz

        if current_index < len(all_quiz_data[current_bai]) - 1:
            next_btn = ui_elements.Button(
                button_x, 
                next_btn_y,
                button_width, 
                button_height,
                "Câu tiếp theo",
                lambda: handle_button_click_callback(next_quiz_question, game_state),
                (100, 180, 100), 
                25, 
                None
            )
            next_btn.draw(screen)
            buttons.append(next_btn)
        else:
            finish_btn = ui_elements.Button(
                button_x, 
                next_btn_y,
                button_width, 
                button_height,
                "Hoàn thành",
                lambda: handle_button_click_callback(finish_quiz_session, game_state),
                (100, 180, 100), 
                25, 
                None
            )
            finish_btn.draw(screen)
            buttons.append(finish_btn)
    
    return buttons

def reload_quiz_data(game_state):
    try:
        if not hasattr(game_state, 'last_quiz_update'):
            game_state.last_quiz_update = 0
            
        current_time = time.time()
        try:
            file_mtime = os.path.getmtime(config.QUIZ_DATA_FILE_PATH)
        except OSError:
            return  # File không tồn tại hoặc không thể truy cập
            
        if file_mtime > game_state.last_quiz_update + 1:  # Thêm độ trễ 1s
            try:
                with open(config.QUIZ_DATA_FILE_PATH, 'r', encoding='utf-8') as f:
                    new_data = json.load(f)  # Validate JSON trước
                    
                import quiz_data as quiz_data_module
                importlib.reload(quiz_data_module)
                
                if (hasattr(game_state, 'quiz_state') and 
                    game_state.quiz_state["bai"] == game_state.current_lesson_id):
                    # Thay thế lệnh reset bằng cách trực tiếp gán giá trị mới
                    game_state.quiz_state = {
                        "bai": game_state.current_lesson_id,
                        "index": 0,
                        "answered": False,
                        "selected": None,
                        "feedback": ""
                    }
                
                game_state.last_quiz_update = current_time
                pygame.event.post(pygame.event.Event(pygame.USEREVENT, {'force_redraw': True}))
                
            except (json.JSONDecodeError, ImportError, AttributeError) as e:
                print(f"Reload failed: {str(e)}")
    except Exception as e:
        print(f"Unexpected error in reload: {str(e)}")

def check_answer_mcq(game_state, bai, idx, selected):
    """Kiểm tra đáp án MCQ"""
    if game_state.quiz_state["answered"]:  # Đã trả lời rồi thì không xử lý nữa
        return
        
    from quiz_data import quiz_data as all_quiz_data
    
    if bai not in all_quiz_data or idx >= len(all_quiz_data[bai]):
        return
        
    q = all_quiz_data[bai][idx]
    
    # Cập nhật trạng thái ngay lập tức
    game_state.quiz_state.update({
        "selected": selected,
        "answered": True,
        "feedback": "Chính xác!" if q["answer"] == selected else "Sai rồi."
    })
    
    if q["answer"] == selected:
        game_state.point += 10
        if correct_sound:
            correct_sound.play()
    else:
        if wrong_sound:
            wrong_sound.play()
    
    # Gửi sự kiện cập nhật giao diện
    pygame.event.post(pygame.event.Event(pygame.USEREVENT, {'force_redraw': True}))

# Thay đổi phần khởi tạo quiz_state trong các hàm
def finish_quiz_session(game_state, bonus_points=50):
    """Kết thúc phiên làm quiz và cập nhật điểm thưởng"""
    game_state.point += bonus_points
    game_state.completed_lessons.append(game_state.quiz_state["bai"])  # Sửa từ lesson_number thành bai
    game_state.quiz_state = {
        "bai": None,  # Đảm bảo dùng bai thay vì lesson_number
        "index": 0,
        "answered": False,
        "selected": None,
        "feedback": ""
    }
    game_state.current_screen = config.SCREEN_LESSON
    game_state.write_data()

def next_quiz_question(game_state):
    """Chuyển đến câu hỏi tiếp theo"""
    from quiz_data import quiz_data as all_quiz_data
    
    current_bai = game_state.quiz_state["bai"]
    if current_bai not in all_quiz_data:
        return
        
    if game_state.quiz_state["index"] < len(all_quiz_data[current_bai]) - 1:
        game_state.quiz_state["index"] += 1
        game_state.quiz_state["answered"] = False
        game_state.quiz_state["selected"] = None
        game_state.quiz_state["feedback"] = ""
        game_state.write_data()
        
    pygame.event.post(pygame.event.Event(pygame.USEREVENT, {'force_redraw': True}))