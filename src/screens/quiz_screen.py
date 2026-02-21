import pygame
import config
import ui_elements
import time
import os
import json
import importlib

correct_sound = None
wrong_sound = None


def set_sounds(correct, wrong):
    """Gán âm thanh cho đúng/sai"""
    global correct_sound, wrong_sound
    correct_sound = correct
    wrong_sound = wrong


# --- Fallback wrap_text: dùng khi ui_elements không có wrap_text ---
def _wrap_text(text: str, font: pygame.font.Font, max_width: int):
    """
    Trả về danh sách các dòng đã được wrap để vừa max_width.
    Xử lý newline trong text, và tách từ nếu một từ dài hơn max_width.
    """
    if text is None:
        return [""]
    lines = []
    paragraphs = text.split("\n")
    for para in paragraphs:
        words = para.split(" ")
        if not words:
            lines.append("")
            continue
        cur_line = ""
        for w in words:
            test = (cur_line + " " + w) if cur_line else w
            if font.size(test)[0] <= max_width:
                cur_line = test
            else:
                if cur_line:
                    lines.append(cur_line)
                # nếu từ w vẫn quá dài, tách theo ký tự
                if font.size(w)[0] > max_width:
                    part = ""
                    for ch in w:
                        if font.size(part + ch)[0] <= max_width:
                            part += ch
                        else:
                            if part:
                                lines.append(part)
                            part = ch
                    if part:
                        cur_line = part
                    else:
                        cur_line = ""
                else:
                    cur_line = w
        if cur_line:
            lines.append(cur_line)
    return lines or [""]


def _get_wrap_func():
    """Trả về hàm wrap từ ui_elements nếu có, còn không trả về fallback."""
    if hasattr(ui_elements, "wrap_text") and callable(getattr(ui_elements, "wrap_text")):
        return ui_elements.wrap_text
    return _wrap_text


def _ensure_quiz_state(game_state):
    """Đảm bảo game_state.quiz_state có cấu trúc cần thiết."""
    if not hasattr(game_state, "quiz_state") or not isinstance(game_state.quiz_state, dict):
        game_state.quiz_state = {
            "bai": getattr(game_state, "current_lesson_id", None),
            "index": 0,
            "answered": False,
            "selected": None,
            "feedback": ""
        }
    else:
        for k, v in [("bai", getattr(game_state, "current_lesson_id", None)),
                     ("index", 0), ("answered", False),
                     ("selected", None), ("feedback", "")]:
            if k not in game_state.quiz_state:
                game_state.quiz_state[k] = v


def draw_quiz_screen(screen, font_title, font, font_small, colors, game_state,
                     handle_button_click_callback, all_quiz_data):
    """
    Vẽ màn hình quiz. Trả về danh sách các Button (ui_elements.Button)
    để hệ thống UI chính có thể kiểm tra click.
    """
    _ensure_quiz_state(game_state)
    wrap_func = _get_wrap_func()

    # Try-safe lấy mtime (tránh crash khi file không tồn tại)
    try:
        file_mtime = os.path.getmtime(config.QUIZ_DATA_FILE_PATH)
    except Exception:
        file_mtime = None

    try:
        if file_mtime is not None:
            if (not hasattr(game_state, 'last_quiz_update') or
                    game_state.last_quiz_update < file_mtime):
                reload_quiz_data(game_state)
                game_state.last_quiz_update = time.time()
    except Exception:
        # không để crash UI nếu việc check/migration gặp lỗi
        pass

    current_bai = game_state.quiz_state.get("bai")

    # Nếu không có dữ liệu quiz cho bài hiện tại
    if (not isinstance(all_quiz_data, dict) or
            current_bai not in all_quiz_data or
            not all_quiz_data.get(current_bai)):
        ui_elements.draw_text_centered(
            screen,
            "Không có bài tập cho bài này.",
            config.WIDTH // 2,
            config.HEIGHT // 2,
            font,
            colors.get("text", (0, 0, 0))
        )
        return []

    # bảo đảm index hợp lệ (phòng trường hợp dữ liệu thay đổi)
    current_index = game_state.quiz_state.get("index", 0)
    total_q = len(all_quiz_data[current_bai])
    if current_index < 0 or current_index >= total_q:
        current_index = 0
        game_state.quiz_state["index"] = 0

    q = all_quiz_data[current_bai][current_index]

    # Layout: chia màn hình làm hai cột
    margin = 40
    page_width = (config.WIDTH - margin * 3) // 2
    left_x = margin + 50
    right_x = left_x + page_width + margin - 25
    top_y = 150
    content_width = page_width - 70

    # Vẽ câu hỏi (dùng hàm có sẵn trong ui_elements để xuống dòng nếu có)
    # --- Vẽ tiêu đề "Câu thứ n" phía trên câu hỏi ---
    try:
        title_text = f"Câu {current_index + 1}"
        title_surf = font_title.render(title_text, True, colors.get("completed", (0, 0, 0)))
        screen.blit(title_surf, (left_x, top_y - title_surf.get_height() - 20))
    except Exception:
        pass

    # --- Vẽ câu hỏi ---
    try:
        ui_elements.draw_multiline_text(
            screen,
            q.get("question", ""),
            left_x,
            top_y,
            font,
            colors.get("text", (0, 0, 0)),
            content_width
        )
    except Exception:
        try:
            txt = q.get("question", "")[:200]
            t_surf = font.render(txt, True, colors.get("text", (0, 0, 0)))
            screen.blit(t_surf, (left_x, top_y))
        except Exception:
            pass


    # Vẽ đáp án bên phải, đảm bảo wrap nội dung trong box
    buttons = []
    choice_top_y = top_y
    choice_spacing = 20
    choice_height_min = 45

    choices = q.get("choices", [])
    # Precompute wrapped lines & heights
    wrappeds = [wrap_func(choice, font, content_width - 20) for choice in choices]

    # Tính tổng chiều cao cần thiết; nếu vượt quá vùng có thể, giảm khoảng cách
    total_req_height = 0
    for w in wrappeds:
        text_height = max(1, len(w)) * font.get_linesize()
        total_req_height += max(choice_height_min, text_height + 10)
    total_req_height += (len(choices) - 1) * choice_spacing

    available_height = config.HEIGHT - top_y - 140  # dành chỗ cho feedback & nút bấm dưới
    if total_req_height > available_height:
        # giảm spacing xuống mức tối thiểu
        choice_spacing = 8
        total_req_height = 0
        for w in wrappeds:
            text_height = max(1, len(w)) * font.get_linesize()
            total_req_height += max(choice_height_min, text_height + 10)
        total_req_height += (len(choices) - 1) * choice_spacing

    # Vẽ từng button
    y = choice_top_y
    for idx, wrapped in enumerate(wrappeds):
        text_height = max(1, len(wrapped)) * font.get_linesize()
        choice_height = max(choice_height_min, text_height + 10)

        # màu button tùy trạng thái
        if game_state.quiz_state.get("answered"):
            if idx == q.get("answer"):
                color = (120, 200, 120)
            elif idx == game_state.quiz_state.get("selected"):
                color = (220, 120, 120)
            else:
                color = (255, 228, 196)
        else:
            color = (250, 235, 215)

        # Tạo button (truyền text rỗng, vẽ text thủ công) để tránh giới hạn ký tự trong Button
        # IMPORTANT: freeze current_index/current_bai into default args to avoid late-binding issues
        btn = ui_elements.Button(
            right_x,
            y,
            content_width,
            choice_height,
            "",
            lambda i=idx, bai=current_bai, idx_q=current_index: handle_button_click_callback(
                check_answer_mcq,
                game_state,
                bai,
                idx_q,
                i
            ),
            color,
            8,
            None
        )
        try:
            btn.draw(screen)
        except Exception:
            pass

        # Vẽ text wrapped trong button, căn giữa
        line_y = y + 5
        for line in wrapped:
            try:
                text_surface = font.render(line, True, colors.get("text", (0, 0, 0)))
            except Exception:
                text_surface = font.render(line, True, (0, 0, 0))
            screen.blit(
                text_surface,
                (right_x + (content_width - text_surface.get_width()) // 2, line_y)
            )
            line_y += font.get_linesize()

        buttons.append(btn)
        y += choice_height + choice_spacing

    # Nếu đã trả lời → hiển thị feedback + nút next/finish
    if game_state.quiz_state.get("answered"):
        feedback = game_state.quiz_state.get("feedback", "")
        feedback_color = (80, 160, 80) if feedback == "Chính xác!" else (200, 80, 80)

        try:
            ui_elements.draw_text_centered(
                screen,
                feedback,
                right_x + content_width // 2,
                y + 10,
                font,
                feedback_color
            )
        except Exception:
            try:
                t = font.render(feedback, True, feedback_color)
                screen.blit(t, (right_x + (content_width - t.get_width()) // 2, y + 10))
            except Exception:
                pass

        # Nút tiếp theo / hoàn thành ở đáy
        button_width = 160
        button_height = 40
        next_btn_y = config.HEIGHT - button_height - 20
        button_x = right_x + (content_width - button_width) // 2

        if current_index < total_q - 1:
            next_btn = ui_elements.Button(
                button_x-15, next_btn_y-35,
                button_width + 30, button_height + 4,
                "Câu tiếp theo",
                lambda: handle_button_click_callback(next_quiz_question, game_state),
                (100, 180, 100), 14, None
            )
            try:
                next_btn.draw(screen)
            except Exception:
                pass
            buttons.append(next_btn)
        else:
            finish_btn = ui_elements.Button(
                button_x-15, next_btn_y-35,
                button_width + 10, button_height + 4,
                "Hoàn thành",
                lambda: handle_button_click_callback(finish_quiz_session, game_state),
                (100, 180, 100), 14, None
            )
            try:
                finish_btn.draw(screen)
            except Exception:
                pass
            buttons.append(finish_btn)

    # --- Vẽ tiến trình "Câu i/n" ở góc dưới bên trái ---
    try:
        prog_text = f"Câu {current_index + 1}/{total_q}"
        prog_surf = font_small.render(prog_text, True, colors.get("text", (0, 0, 0)))
        screen.blit(prog_surf, (10, config.HEIGHT - prog_surf.get_height() - 10))
    except Exception:
        pass

    return buttons


def reload_quiz_data(game_state):
    """Reload dữ liệu quiz khi file thay đổi (an toàn với lỗi file)."""
    try:
        if not hasattr(game_state, 'last_quiz_update'):
            game_state.last_quiz_update = 0

        current_time = time.time()
        try:
            file_mtime = os.path.getmtime(config.QUIZ_DATA_FILE_PATH)
        except OSError:
            return

        if file_mtime > game_state.last_quiz_update + 1:
            try:
                # kiểm tra JSON hợp lệ trước khi reload module
                with open(config.QUIZ_DATA_FILE_PATH, 'r', encoding='utf-8') as f:
                    _ = json.load(f)

                # reload module quiz_data (nếu bạn đang dùng quiz_data.py)
                try:
                    import quiz_data as quiz_data_module
                    importlib.reload(quiz_data_module)
                except Exception:
                    # nếu không có module, bỏ qua
                    pass

                # Nếu đang mở cùng một bài, reset trạng thái câu hỏi
                if (hasattr(game_state, 'quiz_state') and
                        game_state.quiz_state.get("bai") == getattr(game_state, "current_lesson_id", None)):
                    game_state.quiz_state.update({
                        "index": 0,
                        "answered": False,
                        "selected": None,
                        "feedback": ""
                    })

                game_state.last_quiz_update = current_time
                # force redraw
                pygame.event.post(pygame.event.Event(pygame.USEREVENT, {'force_redraw': True}))

            except (json.JSONDecodeError, ImportError, AttributeError) as e:
                print(f"[quiz_screen] Reload failed: {str(e)}")
    except Exception as e:
        print(f"[quiz_screen] Unexpected error in reload: {str(e)}")


def check_answer_mcq(game_state, bai, idx, selected):
    """Kiểm tra đáp án MCQ."""
    if game_state.quiz_state.get("answered"):
        return

    try:
        from quiz_data import quiz_data as all_quiz_data
    except Exception:
        all_quiz_data = {}

    if bai not in all_quiz_data or idx >= len(all_quiz_data.get(bai, [])):
        return

    q = all_quiz_data[bai][idx]

    game_state.quiz_state.update({
        "selected": selected,
        "answered": True,
        "feedback": "Chính xác!" if q.get("answer") == selected else "Sai rồi."
    })

    if q.get("answer") == selected:
        try:
            game_state.point += 10
        except Exception:
            pass
        if correct_sound:
            try:
                correct_sound.play()
            except Exception:
                pass
    else:
        if wrong_sound:
            try:
                wrong_sound.play()
            except Exception:
                pass

    pygame.event.post(pygame.event.Event(pygame.USEREVENT, {'force_redraw': True}))


def finish_quiz_session(game_state, bonus_points=50):
    """Kết thúc buổi quiz: cộng điểm thưởng, quay về màn lesson."""
    try:
        game_state.point += bonus_points
    except Exception:
        pass
    try:
        game_state.completed_lessons.append(game_state.quiz_state.get("bai"))
    except Exception:
        pass
    game_state.quiz_state = {
        "bai": None,
        "index": 0,
        "answered": False,
        "selected": None,
        "feedback": ""
    }
    game_state.current_screen = config.SCREEN_LESSON
    try:
        game_state.write_data()
    except Exception:
        pass


def next_quiz_question(game_state):
    """Chuyển sang câu tiếp theo."""
    try:
        from quiz_data import quiz_data as all_quiz_data
    except Exception:
        all_quiz_data = {}

    current_bai = game_state.quiz_state.get("bai")
    if current_bai not in all_quiz_data:
        return

    if game_state.quiz_state.get("index", 0) < len(all_quiz_data[current_bai]) - 1:
        game_state.quiz_state["index"] += 1
        game_state.quiz_state["answered"] = False
        game_state.quiz_state["selected"] = None
        game_state.quiz_state["feedback"] = ""
        try:
            game_state.write_data()
        except Exception:
            pass

    pygame.event.post(pygame.event.Event(pygame.USEREVENT, {'force_redraw': True}))
