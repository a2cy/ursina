# this will clear the scene and try to execute the main.py code without
# restarting the program

import ast
import time
from pathlib import Path

from ursina import Entity, application, camera, mesh_importer, print_on_screen, scene, texture_importer, window


def is_valid_python(code):
   try:
       ast.parse(code)
   except Exception as e:
       return False, e

   return True


def make_code_reload_safe(code):
    newtext = ''
    dedent_next = False

    for line in code.split('\n'):
        if line.strip().endswith('app.run()') or line.strip().endswith('HotReloader()'):
            continue
        if 'eternal=True' in line:
            continue
        if line.startswith('''if __name__ == '__main__':'''):
            dedent_next = True
            continue
        if line and line[0] != ' ':
            dedent_next = False

        if line.strip().startswith('#'):
            newtext += '\n'
            continue
        # if line.strip().startswith('EditorCamera(') and not 'eternal=False' in line: # EditorCamera is eternal, so don't create multiple ones
        #     newtext += '\n'
        #     continue

        if dedent_next:
            newtext += line[4:] + '\n'
        else:
            newtext += line + '\n'

    return newtext



class HotReloader(Entity):
    def __init__(self, path=__file__, **kwargs):
        super().__init__(parent=camera.ui, eternal=True, ignore_paused=True)
        self.path = path

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.path = Path(self.path)
        self.hotreload = False   # toggle with f9
        self._original_source_code_content = ''
        # self.text_editor = InGameTextEditor(path=self.path, enabled=False)
        self._i = 0
        self.hotkeys = {
            'ctrl+r' : self.reload_code,
            'f5'     : self.reload_code,
            'f6'     : self.reload_textures,
            'f7'     : self.reload_models,
            'f8'     : self.reload_shaders,
            'f9'     : self.toggle_hotreloading,
            }

        self.hotreload_window_settings = dict(size=(window.size[0]/2,window.size[1]/2), always_on_top=True, position=(window.fullscreen_size[0]-window.size[0]/22, 0))


    def input(self, key):
        if key in self.hotkeys:
            self.hotkeys[key]()

        # if key == '|':
        #     if not self.text_editor.enabled:
        #         invoke(setattr, self.text_editor, 'enabled', not self.text_editor.enabled, delay=.1)
        #     else:
        #         self.text_editor.enabled = not self.text_editor.enabled

    def update(self):
        if self.hotreload:
            self._i += time.dt
            if self._i > .2:
                current_source_code = self.get_source_code()

                if current_source_code != self._original_source_code_content:
                    self.reload_code()
                    self._original_source_code_content = current_source_code

                self._i = 0

    def get_source_code(self):
        with open(self.path, encoding='utf8') as file:
            text = file.read()
        return text


    def toggle_hotreloading(self):
        self.hotreload = not self.hotreload
        print_on_screen(f'<azure>hotreloading: {self.hotreload}')
        if self.hotreload_window_settings:
            for key, value in self.hotreload_window_settings.items():
                setattr(window, key, value)



    def reload_code(self, reset_camera=True):
        if not self.path.exists:
            print('trying to reload, but path does not exist:', self.path)
            return


        with open(self.path, encoding='utf8') as file:
            text = file.read()
            text = make_code_reload_safe(text)


        if not is_valid_python(text):
            print('invalid python code')
            return

        scene.clear()
        if reset_camera:
            camera.position = (0, 0, -20)

        t = time.time()
        try:
            d = dict(locals(), **globals())
            d['__name__'] = '__main__'
            application.paused = True
            exec(text, d, d)

            import __main__
            for key, value in d.items():
                if key in dir(__main__) or key in ('update', 'input'):
                    setattr(__main__, key, value)

            application.paused = False

        except Exception as e:
            print(e)

        print('reloaded in:', time.time() - t)


    def reload_textures(self):
        textured_entities = [e for e in scene.entities if e.texture]
        reloaded_textures = list()

        for e in textured_entities:
            if e.texture.name in reloaded_textures or not hasattr(e.texture, 'path') or not e.texture.path:
                continue

            if e.texture.path.parent.name == application.textures_compressed_folder.name:
                print('texture is made from .psd file', e.texture.path.stem + '.psd')
                texture_importer.compress_textures(e.texture.path.stem)
            print('reloaded texture:', e.texture.path)
            e.texture._texture.reload()
            reloaded_textures.append(e.texture.name)

        return reloaded_textures


    def reload_models(self):
        print('reloading models...')
        entities = [e for e in scene.entities if e.model]
        unique_names = list(set(e.model.name.split('.')[0] for e in entities))
        # print(unique_names)
        changed_models = []

        for name in unique_names:
            matches = [e for e in application.asset_folder.glob(f'**/{name}.blend')]

            if not matches or not application.blender_paths:    # reload bam files converted from obj
                [e for e in application.asset_folder.glob(f'**/{name}.obj')]
                if matches:
                    m = mesh_importer.load_model(f'{matches[0]}.obj')
                    print('-----------------load:', f'{matches[0]}.obj', m)
                    mesh_importer.imported_meshes[name] = m
                    changed_models.append(name)
                    continue

            if not matches:
                continue

            model_path = matches[0]
            # ignore internal models
            if model_path.parent == application.internal_models_folder or '/build/' in str(model_path):
                continue

            if name in mesh_importer.imported_meshes:
                mesh_importer.imported_meshes.pop(name, None)

            # print('model is made from .blend file:', model_path)
            mesh_importer.blend_to_obj(model_path)
            mesh_importer.obj_to_ursinamesh(application.models_compressed_folder, application.models_compressed_folder, return_mesh=True, save_to_file=False, delete_obj=True).save(f'{name}.bam')
            # print(f'compressed {name}.blend sucessfully')
            changed_models.append(name)


        for e in entities:
            if e.model:
                name = e.model.name.split('.')[0]
                # print(name, changed_models, name in changed_models)
                if name in changed_models:
                    e.model = None
                    e.model = name
                    e.origin = e.origin
                    print('reloaded model:', name)


    def reload_shaders(self):
        import ursina

        for shader in ursina.shader.imported_shaders.values():
            # print(shader, shader.path)
            # TODO: check if file has changed

            with open(shader.path, encoding='utf8') as f:
                try:
                    print('trying to reload:', shader.path.name)
                    text = f.read()

                    geom = ''
                    if r"geometry='''" in text:
                        geom = text.split(r"geometry='''", 1)[1].split("'''", 1)[0]
                        print('geommmmmmmmmmmmmmm', geom)

                    vert = ''
                    if r"verte ='''" in text:
                        vert = text.split(r"vertex='''", 1)[1].split("'''", 1)[0]

                    frag = text.split(r"fragment='''", 1)[1].split("'''", 1)[0]

                    if geom:
                        shader.geometry = geom
                    if vert:
                        shader.vertex = vert
                    shader.fragment = frag

                    shader.compile()

                    for e in scene.entities:
                        if hasattr(e, '_shader') and e.shader == shader:
                            e.clearShader()
                            e.shader = e.shader

                    print('reloaded shader:', shader.path.name)
                except Exception as e:
                    print('failed to reload shader:', shader.path.name, 'error:', e)
                    pass

# class InGameTextEditor(Entity):
#     def __init__(self, path, **kwargs):
#         super().__init__(parent=camera.ui, z=-10)
#         self.file_path = path
#
#         self.add_script(Scrollable(min=0, max=10))
#         self.bg = Entity(parent=self, model='quad', scale_x=camera.aspect_ratio, color=color.hsv(0,0,0,.9), z=1, collider='box', origin_y=.5, y=.5, scale_y=10, eternal=True)
#         self.header = Text(parent=self, x=-.5, y=.475, text=self.file_path.name)
#         self.text_editor = TextField(parent=self, font_size=14, max_lines=50)
#         self.text_editor.text_entity.text_colors['default'] = color.hsv(219, .0, .95)
#         self.text_editor.text_entity.text_colors['class_color'] = color.hsv(40, .61, .9)
#         self.text_editor.text_entity.text_colors['kw_color'] = color.hsv(210, .59, .94)
#         self.text_editor.text_entity.text_colors['func_color'] = color.hsv(250, .46, .87)
#         self.text_editor.text_entity.text_colors['param_clor'] = color.hsv(30, .71, .92)
#         self.text_editor.text_entity.text_colors['string_color'] = color.hsv(90, .48, .86)
#
#
#         self.text_editor.replacements = {
#
#             'from ':    f'☾kw_color☽from ☾default☽',
#             'import ':  f'☾kw_color☽import ☾default☽',
#             'def ':     f'☾kw_color☽def ☾default☽',
#             'for ':     f'☾kw_color☽for ☾default☽',
#             'if ':      f'☾kw_color☽if ☾default☽',
#             ' in ':     f'☾kw_color☽ in ☾default☽',
#
#             'print(':   f'☾func_color☽print☾default☽(',
#             'range(':   f'☾func_color☽range☾default☽(',
#             '__init__': f'☾func_color☽__init__☾default☽',
#             'super':    f'☾func_color☽super☾default☽',
#
#             'class ':   f'☾class_color☽class ☾default☽',
#             'Entity':   f'☾lime☽Entity☾default☽',
#             'self.':    f'☾class_color☽self☾default☽.',
#             '(self)':   f'(☾class_color☽self☾default☽)',
#             'self,':    f'☾class_color☽self☾default☽,',
#
#             'highlight_color = ':    f'☾param_clor☽highlight_color☾default☽ = ',
#
#             '\',':    f'\',☾default☽',   # end quote
#             '\':':    f'\':☾default☽',   # end quote
#             '\')':    f'\')☾default☽',   # end quote
#             '\'':    f'☾string_color☽\'', # start quote
#             }
#
#         self.eternal = True
#         self.ignore_paused = True
#
#         with self.file_path.open() as f:
#             self.text_editor.text = f.read()
#             self.text_editor.render()
#
#
#         for key, value in kwargs.items():
#             setattr(self, key, value)
#
#
#     def on_enable(self):
#         application.pause()
#         self.ignore_input = False
#
#
#     def on_disable(self):
#         application.resume()
#         self.ignore_input = True
#
#
#     def input(self, key):
#         if held_keys['control'] and key == 'enter':
#             if self.reload_code():
#                 if held_keys['shift']:
#                     self.enabled = False
#
#
#     def reload(self):
#         cleaned_text = make_code_reload_safe(self.text_editor.text)
#
#         try:
#             scene.clear()
#             exec(cleaned_text)
#             print('...............')
#             print(cleaned_text)
#             print('...............')
#             return True
#         except Exception as e:
#             # exception = is_valid_python(cleaned_text)
#             if type(e) == SyntaxError:
#                 print('Error on line:', e)
#             else:
#                 import traceback
#                 error_message = traceback.format_exc()
#                 print(error_message)
#
#             return False
#


if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    # hot_reloader = HotReloader()
    # application.hot_reloader.path = application.asset_folder.parent.parent / 'samples' / 'platformer.py'
    # Sky()

    '''
    By default you can press F5 to reload the starting script, F6 to reimport textures and F7 to reload models.
    '''
    # window.size *= .5
    # window.position += Vec2(100,300)
    # bg = Sprite('shore')
    #
    # button = Button(text='test button', scale=.75, model=Circle(32), color=color.red)

    # test
    from ursina.shaders import lit_with_shadows_shader
    from ursina.prefabs.primitives import *

    shader = lit_with_shadows_shader

    a = AzureCube(shader=shader, texture='shore')
    b = WhiteSphere(shader=shader, rotation_y=180, x=3, texture='brick')
    b.texture.filtering = None
    GrayPlane(scale=10, y=-2, texture='shore', shader=shader)


    # Enable shadows; we need to set a frustum for that.
    from ursina.lights import DirectionalLight
    sun = DirectionalLight(y=10, rotation=(90+30,90,0))
    sun._light.show_frustum()


    Sky(color=color.light_gray)

    print(Sky.instances)
    EditorCamera()

    def update():
        a.x += (held_keys['d'] - held_keys['a']) * time.dt * 5
        a.y += (held_keys['e'] - held_keys['q']) * time.dt * 5
        a.z += (held_keys['w'] - held_keys['s']) * time.dt * 5


    app.run()
