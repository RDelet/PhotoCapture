import logging
import os
from time import sleep

import gphoto2 as gp


log = logging.getLogger("GPhoto Python")
log.setLevel(logging.DEBUG)

directory, _ = os.path.split(__file__)
output_dir = os.path.join(directory, "TestHDR/Test_04")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


class Camera:

    def __init__(self):
        self._camera = None
        self._config = None
        self._init_camera()
    
    def _init_camera(self):
        log.debug(f"Init camera.")
        self._camera = gp.Camera()
        try:
            self._camera.init()
            self._config = self._camera.get_config()
        except Exception as e:
            self.exit()
            raise RuntimeError(e)
    
    @property
    def capture_settings(self):
        log.debug("Get capture settings config.")
        return self._config.get_child_by_name("capturesettings")
    
    @property
    def aperture_cfg(self):
        log.debug("Get aperture config.")
        return self.capture_settings.get_child_by_name('aperture')

    @property
    def aperture(self):
        log.debug("Get aperture value.")
        return self.aperture_cfg.get_value()
    
    @aperture.setter
    def aperture(self, value):
        log.debug("Set aperture value.")
        self.aperture_cfg.set_value(value)
        self.set()

    @property
    def shutter_speed_cfg(self):
        log.debug("Get shutter speed config.")
        return self.capture_settings.get_child_by_name("shutterspeed")
    
    @property
    def shutter_speed(self):
        log.debug("Get shutter speed value.")
        return self.shutter_speed_cfg.get_value()
    
    @shutter_speed.setter
    def shutter_speed(self, value):
        log.debug("Set shutter speed value.")
        self.shutter_speed_cfg.set_value(value)
        self.set()

    def get_choice(self, config):
        log.debug(f"Get choice of {config.get_name()}.")
        output = list()
        for i in range(config.count_choices()):
            choice = config.get_choice(i)
            if choice:
                output.append(choice)
        
        return output
    
    def braketing(self, shutter_min="1/50", shutter_max="10.3", aperture=None):
        if aperture:
            self.aperture = aperture

        shutter_speeds = self.get_choice(self.shutter_speed_cfg)
        print(shutter_speeds)
        start_index = shutter_speeds.index(shutter_max)
        end_index = shutter_speeds.index(shutter_min)

        for i, speed in enumerate(shutter_speeds[start_index: end_index + 1]):
            log.info(f"Braketing -> picture {i}, aperture {self.aperture}, shutter speed {speed}")
            self.shutter_speed = speed
            self.take_photo()

    def exit(self):
        if self._camera:
            self._camera.exit()
        
    def set(self):
        self._camera.set_config(self._config)
    
    def take_photo(self, output_path=None):
        log.debug("Capturing image")
        picture = self._camera.capture(gp.GP_CAPTURE_IMAGE)
        log.debug('Camera file path: {0}/{1}'.format(picture.folder, picture.name))
        target_path = os.path.join(output_dir, picture.name)
        log.debug('Copying image to', target_path)
        camera_file = self._camera.file_get(picture.folder,
                                            picture.name,
                                            gp.GP_FILE_TYPE_NORMAL)
        camera_file.save(target_path)
    
    def time_laps(self, count=20, time=0.5, aperture=None, shutter_speed=None):
        if aperture:
            self.aperture = aperture
        if shutter_speed:
            self.shutter_speed = shutter_speed

        for _ in range(count):
            self.take_photo()
            sleep(time)


camera = Camera()
camera.braketing(shutter_min="1/60", shutter_max="10.3")
# camera.time_laps(count=5)
