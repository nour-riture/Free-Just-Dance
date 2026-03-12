import cv2
import numpy as np
import time

SONGS = [
    {
        "name": "Work From Home",
        "artist": "Fifth Harmony",
        "video": "videos/dance1.mp4",
        "poses": "poses/dance1.json"
    },
    {
        "name": "Physical",
        "artist": "Dua Lipa",
        "video": "videos/dance2.mp4",
        "poses": "poses/dance2.json"
    },
    {
        "name": "Get Low",
        "artist": "Dillon Francis & DJ Snake",
        "video": "videos/dance3.mp4",
        "poses": "poses/dance3.json"
    }
]

COLORS = {
    "bg": (50, 50, 50),
    "title": (51, 68, 255),
    "border_outer": (1, 0, 0),
    "border_inner": (250, 10, 250),
    "song1": (0, 0, 255),
    "song2": (255, 128, 0),
    "song3": (0, 180, 0),
    "selected_bg": (170, 170, 170),
    "unselected_bg": (210, 210, 210),
    "section_title": (250, 250, 250),
    "instructions": (250, 250, 250),
}

SONG_COLORS = [COLORS["song1"], COLORS["song2"], COLORS["song3"]]

def px(img, letter, x, y, color, size=8):
    """Dessine une lettre pixel art avec des rectangles"""
    pixels = {
        'F': ["###  ", "#    ", "###  ", "#    ", "#    "],
        'R': ["###  ", "#  # ", "#### ", "#   #", "#   #"],
        'E': ["#### ", "#    ", "###  ", "#    "," ####"],
        'E2':["#### ", "#    ", "###  ", "#    ", "####"],
        'J': ["  ## ", "   # ", "   # ", "#  # ", " ##  "],
        'U': ["# #  ", "# #  ", "# #  ", "# #  ", " ##  "],
        'S': [" ### ", "#    ", " ##  ", "   # ", "###  "],
        'T': ["#####", "  #  ", "  #  ", "  #  ", "  #  "],
        'D': ["###  ", "# #  ", "# #  ", "# #  ", "###  "],
        'A': [" ##  ", "# #  ", "#####", "# #  ", "# #  "],
        'N': ["# #  ", "## # ", "# ## ", "#  # ", "#  # "],
        'C': [" ### ", "#    ", "#    ", "#    ", " ### "],
        'E3':["#### ", "#    ", "###  ", "#    ", "####"],
        ' ': ["     ", "     ", "     ", "     ", "     "],
        '!': ["  #  ", "  #  ", "  #  ", "     ", "  #  "],
    }
    
    grid = pixels.get(letter, pixels[' '])
    for row_idx, row in enumerate(grid):
        for col_idx, cell in enumerate(row):
            if cell == '#':
                px_x = x + col_idx * size
                px_y = y + row_idx * size
                cv2.rectangle(img, (px_x, px_y), (px_x + size - 1, px_y + size - 1), color, -1)

def draw_pixel_title(img, y_center):
    """Dessine FREE JUST DANCE en pixel art centré"""
    words = [
        ("FREE", ["F", "R", "E2", "E"]),
        ("JUST", ["J", "U", "S", "T"]),
        ("DANCE!", ["D", "A", "N", "C", "E3", "!"]),
    ]
    size = 10
    letter_w = 6 * size
    gap = size * 2
    word_gap = size * 4
    word_colors = [COLORS["song1"], COLORS["song2"], COLORS["song3"]]

    total_w = sum(len(w[1]) * letter_w + (len(w[1])-1) * gap for w in words) + (len(words)-1) * word_gap
    start_x = (1280 - total_w) // 2

    x = start_x
    for word_idx, (word_str, letters) in enumerate(words):
        color = word_colors[word_idx]
        for letter in letters:
            px(img, letter, x, y_center - 25, color, size)
            x += letter_w + gap
        x += word_gap - gap

def show_menu(num_players, selected_idx, blink_on):
    img = np.ones((720, 1280, 3), dtype=np.uint8)
    img[:] = COLORS["bg"]

    # Border
    cv2.rectangle(img, (0, 0), (1279, 719), COLORS["border_outer"], 12)
    cv2.rectangle(img, (6, 6), (1273, 713), COLORS["section_title"], 4)

    # Title and subtitle
    draw_pixel_title(img, 80)

    sub = "MAYBE you should start considering saving some money... made by nour-riture all credits to Danefano"
    tw = cv2.getTextSize(sub, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)[0][0]
    cv2.putText(img, sub, ((1280 - tw) // 2, 145),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (250, 250, 250), 1)

    # THE GREAT SEPARATION LINEEE
    cv2.line(img, (20, 165), (1260, 165), COLORS["section_title"], 3)

    # Nb of players
    label = "NUMBER OF PLAYERS :"
    lw = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.85, 2)[0][0]
    cv2.putText(img, label, ((1280 - lw) // 2, 210),
        cv2.FONT_HERSHEY_SIMPLEX, 0.85, COLORS["section_title"], 2)

    btn_w, btn_h = 200, 55
    total_btn = btn_w * 2 + 40
    btn_start = (1280 - total_btn) // 2
    for i, label_btn in enumerate(["1 PLAYER", "2 PLAYERS"]):
        x = btn_start + i * (btn_w + 40)
        bg = COLORS["selected_bg"] if num_players == i+1 else COLORS["unselected_bg"]
        cv2.rectangle(img, (x, 225), (x + btn_w, 225 + btn_h), bg, -1)
        cv2.rectangle(img, (x, 225), (x + btn_w, 225 + btn_h), COLORS["section_title"], 3)
        tw = cv2.getTextSize(label_btn, cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2)[0][0]
        text_color = (255, 255, 255) if num_players == i+1 else (50, 50, 50)
        cv2.putText(img, label_btn, (x + (btn_w - tw) // 2, 260),
            cv2.FONT_HERSHEY_SIMPLEX, 0.75, text_color, 2)

    # THE LINEEEEE
    cv2.line(img, (20, 300), (1260, 300), COLORS["section_title"], 2)

    # songs
    label2 = "CHOOSE YOUR SONG :"
    lw2 = cv2.getTextSize(label2, cv2.FONT_HERSHEY_SIMPLEX, 0.85, 2)[0][0]
    cv2.putText(img, label2, ((1280 - lw2) // 2, 340),
        cv2.FONT_HERSHEY_SIMPLEX, 0.85, COLORS["section_title"], 2)

    keys = ["A", "B", "C"]
    card_w = 900
    card_x = (1280 - card_w) // 2

    for i, song in enumerate(SONGS):
        y = 360 + i * 100
        color = SONG_COLORS[i]
        is_selected = selected_idx == i
        bg = COLORS["selected_bg"] if is_selected else COLORS["unselected_bg"]

        cv2.rectangle(img, (card_x, y), (card_x + card_w, y + 80), bg, -1)
        cv2.rectangle(img, (card_x, y), (card_x + card_w, y + 80), color, 3)

        cv2.rectangle(img, (card_x + 10, y + 10), (card_x + 60, y + 70), color, -1)
        kw = cv2.getTextSize(keys[i], cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)[0][0]
        cv2.putText(img, keys[i], (card_x + 10 + (50 - kw) // 2, y + 57),
            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

        cv2.putText(img, song["name"], (card_x + 80, y + 38),
            cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)

        cv2.putText(img, song["artist"], (card_x + 80, y + 65),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1)

        if is_selected and blink_on:
            cv2.putText(img, "<<< CHOOSEN", (card_x + 620, y + 45),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)

    # memo key instructions
    cv2.line(img, (20, 670), (1260, 670), COLORS["section_title"], 2)
    instructions = [
        "A / B / C  ->  choose a song",
        "1 / 2  ->  number of players",
        "Q  ->  quit"
    ]
    total_iw = sum(cv2.getTextSize(t, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)[0][0] for t in instructions) + 120
    ix = (1280 - total_iw) // 2
    for t in instructions:
        cv2.putText(img, t, (ix, 695), cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLORS["instructions"], 1)
        ix += cv2.getTextSize(t, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)[0][0] + 60

    return img

def run_menu():
    num_players = 1
    selected_song = None
    selected_idx = 0
    blink_on = True
    last_blink = time.time()

    cv2.namedWindow("Free Just Dance", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Free Just Dance", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while selected_song is None:
        if time.time() - last_blink > 0.5:
            blink_on = not blink_on
            last_blink = time.time()

        menu_img = show_menu(num_players, selected_idx, blink_on)
        cv2.imshow("Free Just Dance", menu_img)
        key = cv2.waitKey(30) & 0xFF

        if key == ord('1'):
            num_players = 1
        elif key == ord('2'):
            num_players = 2
        elif key == ord('a'):
            selected_idx = 0
            selected_song = SONGS[0]
        elif key == ord('b'):
            selected_idx = 1
            selected_song = SONGS[1]
        elif key == ord('c'):
            selected_idx = 2
            selected_song = SONGS[2]
        elif key == ord('q'):
            return None, None

    cv2.destroyAllWindows()
    return selected_song, num_players