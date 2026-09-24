from ursina import Entity, Button, camera, color, Func, Quad, Vec2, Vec3, hsv


main_keys = [
    [('ESC', 'escape', 1), ('F1', 'f1', 1), ('F2', 'f2', 1), ('F3', 'f3', 1), ('F4', 'f4', 1), ('F5', 'f5', 1), ('F6', 'f6', 1), ('F7', 'f7', 1), ('F8', 'f8', 1), ('F9', 'f9', 1), ('F10', 'f10', 1), ('F11', 'f11', 1), ('F12', 'f12', 1)],
    [('`', '`', 1), ('1', '1', 1), ('2', '2', 1), ('3', '3', 1), ('4', '4', 1), ('5', '5', 1), ('6', '6', 1), ('7', '7', 1), ('8', '8', 1), ('9', '9', 1), ('0', '0', 1), ('-', '-', 1), ('=', '=', 1), ('BACKSPACE', 'backspace', 2)],
    [('TAB', 'tab', 1.5), ('Q', 'q', 1), ('W', 'w', 1), ('E', 'e', 1), ('R', 'r', 1), ('T', 't', 1), ('Y', 'y', 1), ('U', 'u', 1), ('I', 'i', 1), ('O', 'o', 1), ('P', 'p', 1), ('[', '[', 1), (']', ']', 1), ('\\', '\\', 1.5)],
    [('CAPS', 'caps lock', 1.75), ('A', 'a', 1), ('S', 's', 1), ('D', 'd', 1), ('F', 'f', 1), ('G', 'g', 1), ('H', 'h', 1), ('J', 'j', 1), ('K', 'k', 1), ('L', 'l', 1), (';', ';', 1), ("'", "'", 1), ('ENTER', 'enter', 2.25)],
    [('SHIFT', 'left shift', 2.25), ('Z', 'z', 1), ('X', 'x', 1), ('C', 'c', 1), ('V', 'v', 1), ('B', 'b', 1), ('N', 'n', 1), ('M', 'm', 1), (',', ',', 1), ('.', '.', 1), ('/', '/', 1), ('SHIFT', 'right shift', 2.75)],
    [('CTRL', 'left control', 1.25), ('WIN', 'win', 1.25), ('ALT', 'left alt', 1.25), ('SPACE', 'space', 6), ('ALT', 'right alt', 1.25), ('WIN', 'win', 1.25), ('MENU', 'menu', 1.25), ('CTRL', 'right control', 1.25)]
]

navigation = [
    [('INSERT', 'insert', 1), ('HOME', 'home', 1), ('PAGE\nUP', 'page up', 1)],
    [('DELETE', 'delete', 1), ('END', 'end', 1), ('PAGE\nDOWN', 'page down', 1)],
    [(None, None, 1), ('UP', 'up arrow', 1), (None, None, 1)],
    [('LEFT', 'left arrow', 1), ('DOWN', 'down arrow', 1), ('RIGHT', 'right arrow', 1)]
]

numpad = [
    [('NUM', 'num lock', 1), ('/', '/', 1), ('*', '*', 1), ('-', '-', 1)],
    [('7', 'num 7', 1), ('8', 'num 8', 1), ('9', 'num 9', 1), ('+', '+', 1)],
    [('4', 'num 4', 1), ('5', 'num 5', 1), ('6', 'num 6', 1), ('+', '+', 1)],
    [('1', 'num 1', 1), ('2', 'num 2', 1), ('3', 'num 3', 1), ('ENTER', 'num enter', 1)],
    [('0', 'num 0', 2), ('.', 'num decimal', 1), ('ENTER', 'num enter', 1)]
]

class KeyboardButton(Button):
    def __init__(self, key_picker, key_name, key_code, text_size=.6, available=True, fill_color=color.hex('#373737'), **kwargs):
        kwargs['text'] = key_name if available else ''
        kwargs['color'] = fill_color if available else color.hex('#1d1d1d')
        kwargs['highlight_color'] = color.hex('#801c74') if available else color.hex('#191919')
        kwargs['pressed_color'] = color.hex('#6E6E6E') if available else color.hex('#191919')
        super().__init__(text_size=text_size, **kwargs)
        self.key_picker = key_picker
        self.key_name = key_name
        self.key_code = key_code
        self.available = available
        if self.available:
            self.up_button = Button(parent=self, scale_y=.25, position=(0,-.5,-.1), color=color.hsv(0,0,.05), highlight_color=self.highlight_color, on_click=Func(self.select_key, key_name=f'{self.key_name} up', key_code=f'{self.key_code} up'))
        else:
            self.collider = None

    def on_click(self):
        if self.available:
            self.select_key(self.key_name, self.key_code)

    def select_key(self, key_name, key_code):
        if self.key_picker.on_submit:
            print('Selected:', key_name, '| Ursina key:', key_code)
            self.key_picker.on_submit(key_name)
            self.key_picker.enabled = False

        if self.key_picker.target_field:
            self.key_picker.target_field.text = key_code


class KeyPicker(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, enabled=True)
        self.keys = []
        self.key_width = .045
        self.key_height = .04
        self.gap = Vec2(.005, .01)
        self.target_field = None

        self.available_keys = (
            'escape', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
            '`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'backspace',
            'tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\',
            'caps lock', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", 'enter',
            'left shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'right shift', 'left control', 'right control', 'left alt', 'right alt',
            'space', 'left arrow', 'right arrow', 'up arrow', 'down arrow', 'page up', 'page down'
        )

        navigation_width = 3 * self.key_width + 2 * self.gap.x
        # numpad_width = 4 * self.key_width + 3 * self.gap

        section_gap = .1
        main_width = self.get_section_width(main_keys)
        total_width = main_width + navigation_width + section_gap

        # main_x = -total_width / 2 + main_width / 2
        # navigation_x = -total_width / 2 + main_width + section_gap + navigation_width / 2
        # numpad_x = -total_width / 2 + main_width + section_gap + navigation_width + section_gap + numpad_width / 2

        # start_y = .125
        row_spacing = self.key_height + self.gap.y

        self.keyboard = Entity(parent=self, x=-.15, y=.0)
        center = Entity(parent=self.keyboard, model='quad', color=color.red, scale=.01)

        # main_keyboard
        main_width = self.get_section_width(main_keys)
        navigation_width = 3 * self.key_width + 2 * self.gap.x

        section_gap = .1
        total_width = main_width + navigation_width + section_gap
        main_x = -total_width / 2 + main_width / 2

        start_y = .125
        row_spacing = self.key_height + self.gap.y

        row_offsets = [-.005, 0, .018, .035, .052, .075]
        for row_index, row in enumerate(main_keys):
            row_width = sum(width * self.key_width for _, _, width in row) + (len(row) - 1) * self.gap.x
            x = main_x - row_width / 2 + row_offsets[row_index]
            y = start_y - row_index * row_spacing

            for key_name, key_code, width in row:
                button_width = width * self.key_width
                # self.create_key(key_name, key_code, x + button_width / 2, y, button_width, self.key_height)
                KeyboardButton(key_picker=self, parent=self.keyboard, scale=(button_width, self.key_height), position=(x+button_width/2,y), key_name=key_name, key_code=key_code, available=key_code in self.available_keys)
                x += button_width + self.gap.x



        # navigation
        row_width = 3 * self.key_width + 2 * self.gap.x
        for row_index, row in enumerate(navigation):
            x = (- row_width / 2) +.425
            y = - row_index * row_spacing + .0275

            for key_name, key_code, width in row:
                button_width = width * self.key_width

                if key_name is not None:
                    available = key_code in self.available_keys
                    # self.create_key(key_name, key_code, x + button_width / 2, y, button_width, self.key_height, text_size=.5)
                    key = KeyboardButton(key_picker=self, parent=self.keyboard, scale=(button_width, self.key_height), position=(x, y), key_name=key_name, key_code=key_code, available=available, text_size=.5)

                x += button_width + self.gap.x

        # # numpad
        # # numpad_width = 4 * self.key_width + 3 * self.gap.x
        # # numpad_x = -total_width / 2 + main_width + section_gap + navigation_width + section_gap + numpad_width / 2

        # row_width = 4 * self.key_width + 3 * self.gap.x

        # for row_index, row in enumerate(numpad):
        #     x = - row_width / 2 +.4
        #     y = - row_index * row_spacing +.125

        #     for key_name, key_code, width in row:
        #         button_width = width * self.key_width
        #         self.create_key(key_name, key_code, x + button_width / 2, y, button_width, self.key_height)
        #         x += button_width + self.gap.x


        self.create_mouse()
        # self.create_numpad(numpad_x, start_y, row_spacing)

        self.keyboard_width = total_width + .04
        self.keyboard_height = 6 * row_spacing + .025
        self.keyboard_background = Entity(parent=self.keyboard, model=Quad(aspect=self.keyboard_width / self.keyboard_height, radius=.025), color=color.rgba32(20, 20, 20, 240), scale=(self.keyboard_width, self.keyboard_height), z=.01, collider='box')
        self.background = Entity(parent=self, color=color.hsv(0,0,.15), scale=(self.keyboard_width+.35, self.keyboard_height+.05), z=.5, collider='box')
        self.background.model = Quad(aspect=self.background.scale.x / self.background.scale.y, radius=.025)
        self.bg = Entity(parent=self, collider='box', z=1, scale=Vec2(100,100), on_click=self.disable)

        for key, value in kwargs.items():
            setattr(self, key, value)


    def get_section_width(self, section):
        return max(sum(width * self.key_width for _, _, width in row) + (len(row) - 1) * self.gap.x for row in section)


    def create_mouse(self):
        mouse_base = Entity(parent=self, position=(.525, .08, -.01), scale=.16)
        mouse_upper = Entity(parent=mouse_base, model=Quad(radius=.08), scale=(1, .75), color=color.hex('#141414'))
        mouse_lower = Entity(parent=mouse_base, model='quad', position=(0,-.75,0), scale_y=.75, color=mouse_upper.color)
        mouse_lower_circle = Entity(parent=mouse_base, model='circle', position=(0,mouse_lower.y-.25,0), color=mouse_upper.color)

        left_button = KeyboardButton(parent=mouse_upper, position=(-.25, .0, -.1), scale=(.48, 1), text_size=.6, key_picker=self, key_name='LM', key_code='left mouse down')
        right_button = KeyboardButton(parent=mouse_upper, position=(.25, .0, -.1), scale=(.48, 1), text_size=.6, key_picker=self, key_name='RM', key_code='right mouse down')
        wheel = KeyboardButton(parent=mouse_upper, position=(0,-.5,-.5), scale=(.16, .5), text_size=.5, fill_color=hsv(0,0,.5), key_picker=self, key_name='MW', key_code='middle mouse down')

        mouse_4 = KeyboardButton(parent=mouse_lower, position=(-.5, -.3, -.1), scale=(.125, .4), text_size=.45, key_picker=self, key_name='M4', key_code='mouse4')
        mouse_5 = KeyboardButton(parent=mouse_lower, position=(-.5, .15, -.1), scale=(.125, .4), text_size=.45, key_picker=self, key_name='M5', key_code='mouse5')

    def create_key(self, key_name, key_code, x, y, width, height, text_size=.6):
        if key_name is None:
            return

        available = key_code in self.available_keys

        key = KeyboardButton(key_picker=self, parent=self, scale=(width, height), position=(x, y), key_name=key_name, key_code=key_code, available=available)
        # key_up = KeyboardButton(key_picker=self, parent=key, scale=(width, height), position=Vec3(0,-.5,-.1), key_name=f'{key_name} up', key_code=f'{key_code} up', available=available, color=color.hsv(0,1,.5))


    def on_submit(self, new_key):
        print(new_key)


if __name__ == '__main__':
    from ursina import Ursina
    app = Ursina()
    field = Button(scale=(.2,.05), position=(-.4,-.3))
    key_picker = KeyPicker()
    key_picker.target_field = field

    def on_submit(new_key):
        print('unbind:', key_picker.old_key)
        print(f'action: {key_picker.action}: {key_picker.old_key} -> {new_key}')
        field.text = new_key

    def open_key_picker(field):
        key_picker.target_field = field
        key_picker.enabled = True
        key_picker.action = 'action'
        key_picker.old_key = field.text
        key_picker.on_submit = on_submit

    field.on_click = Func(open_key_picker, field)

    # Text(text='KEY BINDINGS', y=.4, origin=(0, 0), scale=1.5)

    def input(key):
        print('---', key)

    app.run()