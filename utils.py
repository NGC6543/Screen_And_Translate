

def dict_to_str(dc: dict[str, str]) -> str:
    'Transform dict to a plain text.'
    resutl_str = ''
    for key, value in dc.items():
        resutl_str += (f'{key.capitalize()}: {value}. ')
    return resutl_str


if __name__ == '__main__':
    test = {
        'глагол': 'выбирать, отбирать, подбирать',
        'имя прилагательное': 'избранный, отборный, доступный избранным'
    }
    print(dict_to_str(test))
