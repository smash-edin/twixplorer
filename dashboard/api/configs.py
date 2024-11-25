from dotenv import load_dotenv
import os
import secrets
import secrets

load_dotenv()

dotenvPath = ".env"
env_set = True
env_settings = {'SECRET_KEY':'', 'ACCESS_TOKEN_SECRET':'', 'REFRESH_TOKEN_SECRET':'', 'FLASK_DEBUG':''}
try:
    if os.path.exists(dotenvPath):
        try:
            if 'SECRET_KEY' in os.environ:
                env_settings['SECRET_KEY'] = os.environ['SECRET_KEY']
            if 'ACCESS_TOKEN_SECRET' in os.environ:
                env_settings['ACCESS_TOKEN_SECRET'] = os.environ['ACCESS_TOKEN_SECRET']
            if 'REFRESH_TOKEN_SECRET' in os.environ:
                env_settings['REFRESH_TOKEN_SECRET'] = os.environ['REFRESH_TOKEN_SECRET']
            if 'FLASK_DEBUG' in os.environ:
                env_settings['FLASK_DEBUG'] = os.environ['FLASK_DEBUG']
            for k in env_settings.keys():
                env_set &= env_settings[k] != ''
        except Exception as exp:
            print(f"ERROR: {exp}")
    else:
        env_set = False
except Exception as exp:
    print(f"Error : {exp}")
if not env_set:
    for k in env_settings.keys():
        if env_settings[k] == '':
            env_settings[k] = secrets.token_hex(64) if k != 'FLASK_DEBUG' else 1
    with open(dotenvPath, 'w', encoding='utf-8')as fout:
        for k in env_settings.keys():
            fout.write(f"{k}={env_settings[k]}\n")

load_dotenv()


class ApplicationConfig_DATABASE:
    USERNAME_MIN_LENGTH = 5
    USERNAME_MAX_LENGTH = 12
    PASSWORD_MIN_LENGTH = 6
    PASSWORD_MAX_LENGTH = 12


class ApplicationConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///./db.db'
    ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']
    REFRESH_TOKEN_SECRET = os.environ['REFRESH_TOKEN_SECRET']
    SECRET_KEY = os.environ['SECRET_KEY']
    REFRESH_TOKEN_TIMER = 4
    ACCESS_TOKEN_TIMER = 4
    SOLR_URL = 'http://127.0.0.1'
    SOLR_PORT = 10196
    SOLR_PATH = '../../../solr-9.3.0/'
    SOLR_CORES = ['new_core']
    SOLR_NETWORKS = {'reply': {'field': 'replies_times', 'time': True},
        'retweet': {'field': 'retweet_times', 'time': True}}
    SOLR_COMMUNITIES = {'reply': {'field': 'reply_community'}, 'retweet': {
        'field': 'retweet_community'}}
    SA_URL = 'http://127.0.0.1:10055/api/predict'
    LOCATION_URL = 'http://127.0.0.1:10066/api/get_locations'
    LOG_FOLDER = '../.log/'
    LANGUAGE_DICT = {'Non_Text': 'Non_Text', 'af': 'afrikaans', 'sq':
        'albanian', 'am': 'amharic', 'ar': 'arabic', 'arz': 'arabic', 'an':
        'aragonese', 'hy': 'armenian', 'as': 'assamese', 'av': 'avaric',
        'az': 'azerbaijani', 'ba': 'bashkir', 'eu': 'basque', 'be':
        'belarusian', 'bn': 'bengali', 'bh': 'bihari', 'bs': 'bosnian',
        'br': 'breton', 'bg': 'bulgarian', 'my': 'burmese', 'ca': 'catalan',
        'ce': 'chechen', 'zh': 'chinese', 'cv': 'chuvash', 'kw': 'cornish',
        'co': 'corsican', 'hr': 'croatian', 'cs': 'czech', 'da': 'danish',
        'dv': 'divehi', 'nl': 'dutch', 'en': 'english', 'eo': 'esperanto',
        'et': 'estonian', 'fi': 'finnish', 'fr': 'french', 'gl': 'galician',
        'ka': 'georgian', 'de': 'german', 'el': 'greek', 'gn': 'guarani',
        'gu': 'gujarati', 'ht': 'haitian', 'he': 'hebrew', 'hi': 'hindi',
        'hu': 'hungarian', 'ia': 'interlingua', 'id': 'indonesian', 'ie':
        'interlingue', 'ga': 'irish', 'io': 'ido', 'is': 'icelandic', 'it':
        'italian', 'ja': 'japanese', 'jv': 'javanese', 'kn': 'kannada',
        'kk': 'kazakh', 'km': 'khmer', 'ky': 'kirghiz', 'kv': 'komi', 'ko':
        'korean', 'ku': 'kurdish', 'la': 'latin', 'lb': 'luxembourgish',
        'li': 'limburgan', 'lo': 'lao', 'lt': 'lithuanian', 'lv': 'latvian',
        'gv': 'manx', 'mk': 'macedonian', 'mg': 'malagasy', 'ms': 'malay',
        'ml': 'malayalam', 'mt': 'maltese', 'mr': 'marathi', 'mn':
        'mongolian', 'ne': 'nepali', 'nn': 'norwegian', 'no': 'norwegian',
        'oc': 'occitan', 'or': 'oriya', 'os': 'ossetian', 'pa': 'punjabi',
        'fa': 'persian', 'pl': 'polish', 'ps': 'pashto', 'pt': 'portuguese',
        'qu': 'quechua', 'rm': 'romansh', 'ro': 'romanian', 'ru': 'russian',
        'sa': 'sanskrit', 'sc': 'sardinian', 'sd': 'sindhi', 'sr':
        'serbian', 'gd': 'gaelic', 'si': 'sinhala', 'sk': 'slovak', 'sl':
        'slovenian', 'so': 'somali', 'es': 'spanish', 'su': 'sundanese',
        'sw': 'swahili', 'sv': 'swedish', 'ta': 'tamil', 'te': 'telugu',
        'tg': 'tajik', 'th': 'thai', 'bo': 'tibetan', 'tk': 'turkmen', 'tl':
        'tagalog', 'tr': 'turkish', 'tt': 'tatar', 'ug': 'uyghur', 'uk':
        'ukrainian', 'ur': 'urdu', 'uz': 'uzbek', 'vi': 'vietnamese', 'wa':
        'walloon', 'cy': 'welsh', 'fy': 'frisian', 'yi': 'yiddish', 'yo':
        'yoruba', 'lang': 'english'}
    LANGUAGE_DICT_INV = {v: k for k, v in LANGUAGE_DICT.items() if k not in
        ['arz', 'no', 'lang']}
