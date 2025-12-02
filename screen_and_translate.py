import asyncio
import json

import easyocr
from googletrans import Translator
from PIL import ImageGrab
from PyMultiDictionary import MultiDictionary, DICT_EDUCALINGO

from utils import dict_to_str


FILE_ONLY_TRANSLATION = 'english_base_dictionary.txt'
FILE_FULL_TRANSLATION = 'english_dict_with_definitions.json'


def get_screenshot(image_name: str) -> bool:
    'Get image (screenshot) from clipboard'
    im = ImageGrab.grabclipboard()
    if im:
        im.save(image_name, 'PNG')
        return True
    else:
        print('Its not an image.')
        return False


def read_text_from_image(image_name: str) -> list[str]:
    reader = easyocr.Reader(['en'])
    text = reader.readtext(image_name, detail=0)
    print('-----PROCESSING-----')
    return text


async def translate_text(text: str) -> tuple[str, dict, list]:
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


if __name__ == '__main__':
    screenshot_name = 'base_word.png'
    if get_screenshot(screenshot_name):
        text = read_text_from_image(screenshot_name)[0]
        text, translation, definition = asyncio.run(translate_text(text))
        # print(translation, definition)
        adding_word_and_translate_to_file(text, translation, definition)




### Get Definition of a word. Different approaches
# def send_request():

#     url = 'https://en.wiktionary.org/api/rest_v1/page/definition/run'
#     # url = "https://en.wiktionary.org/w/api.php?action=query&titles=Test&prop=revisions&rvprop=content&format=json"
#     url = 'https://en.wiktionary.org/w/api.php?action=query&titles=run&format=json'
#     url = 'https://en.wiktionary.org/api/rest_v1/page/definition/run'
#     url = 'https://api.dictionaryapi.dev/api/v2/entries/en/good'
#     # params = {
#     #     "action": "query",s
#     #     "titles": 'run',
#     #     "format": "json"
#     # }
#     headers = {
#         'Content-Type': 'application/json',
#         'User-Agent': 'Mozilla/5.0'
#     }

#     response = requests.get(url, headers=headers)
#     # print(response.text)
#     data = response.json()
#     with open('resp_json.json', 'w') as json_file:
#         json.dump(data, json_file, indent=4)
#     # print(data)


# def test(word):
#     dictionary = MultiDictionary(word)
#     dictionary.set_words_lang('en')
#     print(dictionary.get_meanings(dictionary=DICT_EDUCALINGO)) # This print the meanings of all the words
#     # print(dictionary.get_synonyms()) # Get synonyms list
#     # print(dictionary.get_antonyms()) # Get antonyms
#     # print(dictionary.get_translations()) # This will translate all words to over 20 languages
#     print(dictionary.get_translations(to='ru'))
#     # print(help(dictionary.translate))
#     # print(dictionary.translate('en', word=word))
#     # print(dictionary.meaning('en', word))