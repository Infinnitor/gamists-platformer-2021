def text_clean(file):
    text = file.readlines()
    valid_text = []
    for f in range(len(text)):
        if text[f].startswith("#"):
            continue
        text[f] = text[f].replace("\n", "")

        if not text[f].replace(" ", "") == "":
            valid_text.append(text[f])

    return valid_text


def read_brackets(string):
    b_values = []
    for iter, char in enumerate(string):
        if char == "(":
            b_iter = iter
            b_char = ""
            while b_char != ")":
                b_iter += 1
                b_char = string[b_iter]
            b_values.append(string[iter + 1 : b_iter])

    return b_values


class text_player():
    def __init__(self):
        file = text_clean(open("data/config/player.txt", "r"))

        values = {}
        for val in file:
            val = val.replace(" ", "")
            k, v = val.split(":")
            values[k] = float(v)

        self.x_acceleration = values["horizontal_acceleration"]
        self.gravity = values["gravity"]
        self.terminal_velocity = values["vertical_speed_cap"]
        self.speed_cap = values["horizontal_speed_cap"]

        self.walljump_speed = values['walljump_speed']

        self.jumps = values["extra_jumps"]
        self.jump_str = values["jump_strength"]
        self.held_jump_str = values["held_jump_strength"]
        self.held_jump_min = values["held_jump_min"]
        self.held_jump_max = values["held_jump_max"]

        self.x = values["start_x"]
        self.y = values["start_y"]
        self.w = values["player_width"]
        self.h = values["player_height"]


def text_level(path):
    file = text_clean(open(path, "r"))

    terrain = []
    for val in file:
        line = read_brackets(val.replace(" ", ""))

        items = []
        items.append([int(i) for i in line[0].split(",")]) # Pos
        items.append([int(i) for i in line[1].split(",")]) # Size
        items.append(line[2]) # Element type

        terrain.append(items)

    return terrain


def load():
    global player; global level
    player = text_player()


load()
