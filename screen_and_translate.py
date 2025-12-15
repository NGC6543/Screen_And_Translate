import asyncio
import json
import ctypes
import ctypes.wintypes as wt

import easyocr
from googletrans import Translator
from PIL import ImageGrab

from utils import dict_to_str


FILE_ONLY_TRANSLATION = 'english_base_dictionary.txt'
FILE_FULL_TRANSLATION = 'english_dict_with_definitions.json'


def extract_image(image_name: str) -> bool:
    "Get image (screenshot) from clipboard."
    im = ImageGrab.grabclipboard()
    if im:
        im.save(image_name, 'PNG')
        return True
    else:
        return False


def read_text_from_image(image_name: str) -> list[str]:
    "Recognize text from the image."
    reader = easyocr.Reader(['en'])
    text = reader.readtext(image_name, detail=0)
    return text


async def translate_text(text: str) -> tuple[str, dict, list | None] | None:
    "Get translate of the word from the text."
    async with Translator() as translator:
        result = await translator.translate(text=text, dest='ru')
        if result.extra_data['see-also']:
            # If there see-also then translate word contains in see-also
            text = result.extra_data['see-also'][0][0]
            result = await translator.translate(
                text=text, dest='ru'
            )
        extra: dict = result.extra_data
        all_translations: list | None = extra.get('all-translations')

        if not all_translations:
            return text, result.text, None

        limit_translations = {}  # part_of_speech: translation_of_this_word
        if all_translations:
            for translate in all_translations:
                limit_translations[translate[0]] = ', '.join(translate[1][:3])

        definitions = extra['definitions']
        if not definitions:
            return text, limit_translations, []

        limit_definitions = []
        for definition in definitions:
            limit_definitions.append(definition[1][0][0])

    return text, limit_translations, limit_definitions


def adding_word_and_translate_to_file(
        text: str, translate: dict | str, definition: list | None = None
):
    "Save recieved data into files."
    text = text.lower()

    get_str_view = ''
    if isinstance(translate, str):
        get_str_view = translate
    if isinstance(translate, dict):
        get_str_view: str = dict_to_str(translate)

    result_string = f'{text} -- {get_str_view}'

    # Save into txt file
    with open(FILE_ONLY_TRANSLATION, mode='a', encoding='utf-8') as file:
        file.write(result_string)
        file.write('\n')

    # Save into JSON
    result_for_json = {text: [translate, definition]}
    with open(FILE_FULL_TRANSLATION, mode='a', encoding='utf-8') as file:
        json.dump(result_for_json, file, ensure_ascii=False, indent=4)
        file.write('\n')


def main(screenshot_name: str) -> str | None:
    "Handle all events and return error message if needed."
    get_image = extract_image(screenshot_name)
    if not get_image:
        return 'Its not an image'
    recognize_text = read_text_from_image(screenshot_name)
    print('-----RECOGNITION PROCESS-----')
    if not recognize_text:
        return "There's not text."
    recognized_text = recognize_text[0]
    print('-----RECOGNITION DONE-----')
    get_translate = asyncio.run(translate_text(recognized_text))
    if not get_translate:
        return 'Cannot translate this word.'
    text, translation, definition = get_translate
    adding_word_and_translate_to_file(text, translation, definition)

    return 'Done'


def run_script(screenshot_name):
    """Running script and answer to a hotkey."""
    user32 = ctypes.windll.user32

    # Key For ALT and Control
    MOD_ALT = 0x0001
    MOD_CONTROL = 0x0002

    # Virtual key code for "Q"
    VK_Q = 0x51

    # Windows message for hotkeys
    WM_HOTKEY = 0x0312

    # Register hotkey: CTRL + ALT + Q
    if not user32.RegisterHotKey(None, 1, MOD_CONTROL | MOD_ALT, VK_Q):
        print("Failed to register hotkey")

    msg = wt.MSG()

    print('Script runs')
    while True:
        if user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == WM_HOTKEY:
                print(main(screenshot_name))
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))


if __name__ == '__main__':
    screenshot_name = 'base_word.png'
    main(screenshot_name)
    run_script(screenshot_name)
