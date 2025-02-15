class CubeState:
    int_color_dict = {
            0: "orange",
            1: "red",
            2: "yellow",
            3: "white",
            4: "green",
            5: "blue"
        }
    color_int_dict = {
            "orange": 0,
            "red":    1,
            "yellow": 2,
            "white":  3,
            "green":  4,
            "blue":   5
        }

    white  = [0x03] * 9
    red    = [0x01] * 9
    green  = [0x04] * 9
    yellow = [0x02] * 9
    orange = [0x00] * 9
    blue   = [0x05] * 9

    def is_solved(self):
        return (
            (self.white  == ([0x03] * 9)) and
            (self.red    == ([0x01] * 9)) and
            (self.green  == ([0x04] * 9)) and
            (self.yellow == ([0x02] * 9)) and
            (self.orange == ([0x00] * 9)) and
            (self.blue   == ([0x05] * 9))
        )

    def print_state_bytes(self):
        print(*self.white)
        print(*self.red)
        print(*self.green)
        print(*self.yellow)
        print(*self.orange)
        print(*self.blue)

    def decode(self, data):
        split_bytes_array = []
        for b in data:
            split_bytes_array += [b & 0xf]
            split_bytes_array += [(b >> 4) & 0xf]

        self.white = split_bytes_array[0:9]
        self.red = split_bytes_array[9:18]
        self.green = split_bytes_array[18:27]
        self.yellow = split_bytes_array[27:36]
        self.orange = split_bytes_array[36:45]
        self.blue = split_bytes_array[45:54]

    def encode_single_color(self, color_range):
        data  = [color_range[0] << 4 | (0xF & color_range[1])]
        data += [color_range[2] << 4 | (0xF & color_range[3])]
        data += [color_range[4] << 4 | (0xF & color_range[6])]
        data += [color_range[6] << 4 | (0xF & color_range[7])]

        return data

    def encode(self):
        data = []

        data += self.encode_single_color(self.white[0:8])
        data += [self.red[8] << 4 | (0xF & self.white[0])]
        data += self.encode_single_color(self.red[1:])

        data += self.encode_single_color(self.green[0:8])
        data += [self.yellow[8] << 4 | (0xF & self.green[0])]
        data += self.encode_single_color(self.yellow[1:])

        data += self.encode_single_color(self.orange[0:8])
        data += [self.blue[8] << 4 | (0xF & self.orange[0])]
        data += self.encode_single_color(self.blue[1:])

        return data
