import dearpygui.dearpygui as dpg
import numpy as np
from array import array
from stylegan2 import Generator
import torch

device = 'cpu'
image_width, image_height, channel = 256, 256, 3
generator = Generator(256, 512, 8)

dpg.create_context()
dpg.create_viewport(title='DragGAN', width=800, height=650)

raw_data = array('f', [1]*(image_width*image_height*channel))
with dpg.texture_registry(show=False):
    dpg.add_raw_texture(
        width=image_width, height=image_height, default_value=raw_data,
        format=dpg.mvFormat_Float_rgb, tag="image"
    )

def update_image(sender, app_data, user_data):
    count = image_width*image_height*channel
    with torch.no_grad():
        z = torch.randn(1, 512)
        image = generator([z])[0][0].detach().cpu().permute(1, 2, 0).numpy()
    image = (image / 2 + 0.5).clip(0, 1).reshape(count)
    for i in range(0, count):
        raw_data[i] = image[i]

width, height = 200, 200
posx, posy = 0, 0
with dpg.window(
    label='Network & Latent', width=width, height=height, pos=(posx, posy),
    no_move=True, no_close=True, no_collapse=True, no_resize=True,
):
    dpg.add_text('device', pos=(5, 20))
    dpg.add_combo(
        ('cpu', 'cuda'), default_value='cuda', width=60, pos=(70, 20),
    )

    dpg.add_text('weight', pos=(5, 40))

    def select_cb(sender, app_data):
        selections = app_data['selections']
        if selections:
            for fn in selections:
                fp = selections[fn]
                print(f'loading checkpoint from {fp}...')
                ckpt = torch.load(fp, map_location=device)
                generator.load_state_dict(ckpt["g_ema"], strict=False)
                print('loading checkpoint successed!')
                break

    def cancel_cb(sender, app_data):
        ...

    with dpg.file_dialog(
        directory_selector=False, show=False, callback=select_cb, id='weight selector',
        cancel_callback=cancel_cb, width=700 ,height=400
    ):
        dpg.add_file_extension('.*')
    dpg.add_button(
        label="select weight", callback=lambda: dpg.show_item("weight selector"),
        pos=(70, 40),
    )

    dpg.add_text('latent', pos=(5, 60))
    dpg.add_button(label="generate", pos=(5, 80), callback=update_image)

posy += height + 2
with dpg.window(
    label='Drag', width=width, height=height, pos=(posx, posy),
    no_move=True, no_close=True, no_collapse=True, no_resize=True,
):
    ...

posy += height + 2
with dpg.window(
    label='Capture', width=width, height=height, pos=(posx, posy),
    no_move=True, no_close=True, no_collapse=True, no_resize=True,
):
    ...

posx, posy = 2 + width, 0
with dpg.window(
    label='Image', pos=(posx, posy),
    no_move=True, no_close=True, no_collapse=True, no_resize=True,
):
    dpg.add_image("image", show=True)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
