from dotenv import load_dotenv
import os

load_dotenv()

class ApplicationConfig_DATABASE:
    USERNAME_MIN_LENGTH = 5
    USERNAME_MAX_LENGTH = 12
    PASSWORD_MIN_LENGTH = 6
    PASSWORD_MAX_LENGTH = 12

class ApplicationConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = r"sqlite:///./db.db"
    ACCESS_TOKEN_SECRET=os.environ["ACCESS_TOKEN_SECRET"]
    REFRESH_TOKEN_SECRET=os.environ["REFRESH_TOKEN_SECRET"]
    SECRET_KEY=os.environ["SECRET_KEY"]
    REFRESH_TOKEN_TIMER=4
    ACCESS_TOKEN_TIMER=4
    SOLR_URL=r"<PLACEHOLDER, replace with IP address of Solr>"
    SOLR_PORT=r"<PLACEHOLDER, replace with port number of Solr (as integer)>"
    SOLR_PATH=r"../../../Tools/solr-9.3.0"
    SOLR_CORES=r"<PLACEHOLDER, replace with list of Solr core names>"
    SOLR_NETWORKS = {'reply': {'field': 'replies_times', 'time': True}, 'retweet': {'field': 'retweet_times', 'time': True}}
    SOLR_COMMUNITIES = {'reply': {'field': 'reply_community'}, 'retweet': {'field': 'retweet_community'}}
    SA_URL=r"<PLACEHOLDER, replace with API endpoint for Sentiment Analysis>"
    LOCATION_URL = r"<PLACEHOLDER, replace with API endpoint for Location Detection>"
    LOG_FOLDER="../.log/"
    LANGUAGE_DICT =     {'Non_Text':'Non_Text', 'af':'afrikaans','sq':'albanian','am':'amharic','ar':'arabic','arz':'arabic','an':'aragonese','hy':'armenian','as':'assamese','av':'avaric','az':'azerbaijani','ba':'bashkir','eu':'basque','be':'belarusian','bn':'bengali','bh':'bihari','bs':'bosnian','br':'breton','bg':'bulgarian','my':'burmese','ca':'catalan','ce':'chechen','zh':'chinese','cv':'chuvash','kw':'cornish','co':'corsican','hr':'croatian','cs':'czech','da':'danish','dv':'divehi','nl':'dutch','en':'english','eo':'esperanto','et':'estonian','fi':'finnish','fr':'french','gl':'galician','ka':'georgian','de':'german','el':'greek','gn':'guarani','gu':'gujarati','ht':'haitian','he':'hebrew','hi':'hindi','hu':'hungarian','ia':'interlingua','id':'indonesian','ie':'interlingue','ga':'irish','io':'ido','is':'icelandic','it':'italian','ja':'japanese','jv':'javanese','kn':'kannada','kk':'kazakh','km':'khmer','ky':'kirghiz','kv':'komi','ko':'korean','ku':'kurdish','la':'latin','lb':'luxembourgish','li':'limburgan','lo':'lao','lt':'lithuanian','lv':'latvian','gv':'manx','mk':'macedonian','mg':'malagasy','ms':'malay','ml':'malayalam','mt':'maltese','mr':'marathi','mn':'mongolian','ne':'nepali','nn':'norwegian','no':'norwegian','oc':'occitan','or':'oriya','os':'ossetian','pa':'punjabi','fa':'persian','pl':'polish','ps':'pashto','pt':'portuguese','qu':'quechua','rm':'romansh','ro':'romanian','ru':'russian','sa':'sanskrit','sc':'sardinian','sd':'sindhi','sr':'serbian','gd':'gaelic','si':'sinhala','sk':'slovak','sl':'slovenian','so':'somali','es':'spanish','su':'sundanese','sw':'swahili','sv':'swedish','ta':'tamil','te':'telugu','tg':'tajik','th':'thai','bo':'tibetan','tk':'turkmen','tl':'tagalog','tr':'turkish','tt':'tatar','ug':'uyghur','uk':'ukrainian','ur':'urdu','uz':'uzbek','vi':'vietnamese','wa':'walloon','cy':'welsh','fy':'frisian','yi':'yiddish','yo':'yoruba', 'lang':'english'}
    LANGUAGE_DICT_INV = {v: k for k, v in LANGUAGE_DICT.items() if k not in ["arz", "no", "lang"]}
