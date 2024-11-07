from dotenv import load_dotenv
import os
import secrets
import sys

dotenvPath = "./data_updater/.env"
env_set = True
try:
    env_set = load_dotenv(dotenvPath)
except Exception as exp:
    print(f"ERROR: {exp}")
    sys.exit("Error in loading .env file")


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

print(f"env_settings: {env_settings}")
if os.path.isdir("./data_updater"):
    for k in env_settings.keys():
        if env_settings[k] == '':
            env_settings[k] = secrets.token_hex(64) if k != 'FLASK_DEBUG' else 1
    with open(dotenvPath, 'w', encoding='utf-8')as fout:
        for k in env_settings.keys():
            fout.write(f"{k}={env_settings[k]}\n")
    print(f"Environment varibales set successfully, Please check the .env file in both the narratives-ui and narratives-backend repositories.")
else:
    print(f"Environment varibales needed to be initialized before running the app.")
    sys.exit(-1)