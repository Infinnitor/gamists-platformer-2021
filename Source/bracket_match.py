def read_brackets(string, split_on=",", chars=("(", ")"), t=int):
    r = match_brackets(string, *chars)
    split_r = r.split(split_on)
    return [t(i) for i in split_r]


def match_brackets(string, o_char="(", c_char=")"):
    open_b = False
    match_offset = 0
    b_string = ""
    for iter, b in enumerate(string):

        if open_b is False:
            if b == o_char:
                open_b = True

        else:
            if b == o_char:
                match_offset += 1

            if b == c_char:
                if match_offset == 0:
                    return b_string
                else:
                    match_offset -= 1
            b_string += b
