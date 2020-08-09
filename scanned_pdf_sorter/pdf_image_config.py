import os
import configparser


def default_config_create(filename='config.ini'):
    if os.path.isfile(filename) is False:
        config = configparser.ConfigParser()
        config.read(filename)
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'poppler_path', "r'./poppler/bin'")
        config.set('SETTINGS', 'create_dict_json', 'no')
        config.set('SETTINGS', 'tmp_dir_select', 'no')
        config.set('SETTINGS', 'crop_select_divisor', '3')
        config.set('SETTINGS', 'crop_display_divisor', '2')
        config.set('SETTINGS', 'main_display_divisor', '8')
        config.set('SETTINGS', 'dpi', '200')
        config.set('SETTINGS', 'image_type', 'png')
        config.set('SETTINGS', 'file_initial_search_dir', "''")
        config.add_section('CROP_BOX')
        config.set('CROP_BOX', 'start_x', '0')
        config.set('CROP_BOX', 'start_y', '0')
        config.set('CROP_BOX', 'end_x', '100')
        config.set('CROP_BOX', 'end_y', '100')

        with open(filename, 'w') as f:
            config.write(f)
