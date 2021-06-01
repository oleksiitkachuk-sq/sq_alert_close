import logging
import time

import cv2
import pyautogui
import win32gui
from comtypes.safearray import numpy as np

sleep_for_repeat_search = 60  # sec
long_sleep = 1
wait_for_elems = 0.2
log_format = '[%(asctime)s] [%(levelname)s] - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)


def get_screen_resolution():
    from screeninfo import get_monitors
    return get_monitors()[0]


def get_screenshot(window_title=None):
    logging.info('Get screenshot...!')
    if window_title:
        handle = win32gui.FindWindow(None, window_title)
        if handle:
            win32gui.SetForegroundWindow(handle)
            time.sleep(long_sleep)
            x, y, x1, y1 = win32gui.GetClientRect(handle)
            x, y = win32gui.ClientToScreen(handle, (x, y))
            x1, y1 = win32gui.ClientToScreen(handle, (x1 - x, y1 - y))
            return pyautogui.screenshot(region=(x, y, x1, y1))
        else:
            logging.warning('Window not found!')
    else:
        screen = get_screen_resolution()
        return pyautogui.screenshot(region=(0, 0, screen.width, screen.height))


def get_element_coordinates(path_to_image):
    """ This method returns coordinates of object on screen"""
    return pyautogui.center(pyautogui.locateOnScreen(path_to_image, confidence=0.9))


def click_to_coordinates(coord_x, coord_y):
    logging.info(f'Click to coordinates: x [{coord_x}], y [{coord_y}]')
    pyautogui.click(coord_x, coord_y, clicks=2, interval=1)


def is_image_exist(path_to_image, threshold=0.8, window_title=None):
    """ This method checks if an image exists on screen"""
    image_rgb = get_screenshot(window_title)
    image_rgb = np.array(image_rgb)
    image_gray = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(path_to_image, 0)
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(image_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        cv2.rectangle(image_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
    flag = False
    if np.amax(res) > threshold:
        flag = True
    return flag


def click_to_elem(path_to_image, expected_img_path=None):
    """expected_img_path -- expected image state. This variable verifies was object state changed or nor."""
    logging.info(f"Click to element [{path_to_image}]")
    coord_x, coord_y = get_element_coordinates(path_to_image)
    click_to_coordinates(coord_x, coord_y)
    if expected_img_path:
        wait_for_screen(expected_img_path, wait_for=long_sleep)
        return is_image_exist(expected_img_path)


def wait_and_click_to_elem(path_to_images, verify_img=None):
    logging.info(f"Wait and click to element [{path_to_images}]")
    is_exist = False
    if len(path_to_images) > 1:
        for path_to_image in path_to_images:
            is_exist = wait_for_screen(path_to_image, wait_for=long_sleep)
            if is_exist:
                path_to_images = path_to_image
                break
    else:
        is_exist = wait_for_screen(path_to_images[0], verify_img)
        if is_exist:
            path_to_images = path_to_images[0]
    if is_exist:
        click_to_elem(path_to_images, verify_img)
    else:
        logging.warning(f"[{path_to_images}] not found!")


def wait_for_screen(path_to_image, window_title=None, wait_for=long_sleep, threshold=0.8):
    logging.info(f"Wait for screen: [{path_to_image}]")
    for x in range(wait_for):
        if is_image_exist(path_to_image, threshold, window_title):
            return True
        time.sleep(wait_for_elems)
    return False


if __name__ == "__main__":
    logging.info(f"Window alert search started...")
    while True:
        is_exist = wait_for_screen("images/alert_icon.png")
        if is_exist:
            wait_and_click_to_elem(["images/ok_button.png",
                                    "images/ok_button_not_active.png",
                                    "images/ok_button_win10.png",
                                    "images/ok_button_not_active_win10.png",
                                    "ok_button_win10_2.png"])
            # If the popup does not close, the cursor will be on the button OK,
            # this making impossible to find the OK button.
            # Move cursor to top left corner.
            pyautogui.moveTo(10, 10)
        time.sleep(sleep_for_repeat_search)
