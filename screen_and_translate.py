import asyncio
import json

import regex

import easyocr
from googletrans import Translator
from PIL import ImageGrab
from PyMultiDictionary import MultiDictionary, DICT_EDUCALINGO

from utils import dict_to_str


FILE_ONLY_TRANSLATION = 'english_base_dictionary.txt'
FILE_FULL_TRANSLATION = 'english_dict_with_definitions.json'


def extract_image(image_name: str) -> bool:
    'Get image (screenshot) from clipboard'
    im = ImageGrab.grabclipboard()
    if im:
        im.save(image_name, 'PNG')
        return True
    else:
        return False


def read_text_from_image(image_name: str) -> list[str]:
    reader = easyocr.Reader(['en'])
    text = reader.readtext(image_name, detail=0)
    print('-----RECOGNITION PROCESS-----')
    return text


async def translate_text(text: str) -> tuple[str, dict, list] | None:
    async with Translator() as translator:
        result = await translator.translate(text=text, dest='ru')
        if result.extra_data['see-also']:
            # If there see-also then translate word contains in see-also
            text = result.extra_data['see-also'][0][0]
            result = await translator.translate(
                text=text, dest='ru'
            )
        extra = result.extra_data
        all_translations = extra['all-translations']
        if not all_translations:
            return
        limit_translations = {}
        for translate in all_translations:
            limit_translations[translate[0]] = ', '.join(translate[1][:3])
        definitions = extra['definitions']
        limit_definitions = []
        for definition in definitions:
            limit_definitions.append(definition[1][0][0])
    return text, limit_translations, limit_definitions


def adding_word_and_translate_to_file(
        text: str, translate: dict, definition: list
):
    text = text.lower()
    return_str_from_dict: str = dict_to_str(translate)
    result_string = f'{text} -- {return_str_from_dict}'

    # Save into txt file
    with open(FILE_ONLY_TRANSLATION, mode='a', encoding='utf-8') as file:
        file.write(result_string)
        file.write('\n')

    # Save into JSON
    result_for_json = {text: [translate, definition]}
    with open(FILE_FULL_TRANSLATION, mode='a', encoding='utf-8') as file:
        json.dump(result_for_json, file, ensure_ascii=False, indent=4)
        file.write('\n')


def main(screenshot_name: str):
    get_image = extract_image(screenshot_name)
    if not get_image:
        return 'Its not an image'
    recognize_text = read_text_from_image(screenshot_name)
    if not recognize_text:
        return "There's not text."
    recognized_text = recognize_text[0]
    get_translate = asyncio.run(translate_text(recognized_text))
    if not get_translate:
        return 'Cannot translate this word.'
    text, translation, definition = get_translate
    # print(translation, definition)
    adding_word_and_translate_to_file(text, translation, definition)



if __name__ == '__main__':
    screenshot_name = 'base_word.png'
    main(screenshot_name)
