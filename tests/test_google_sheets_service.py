import configparser
from services.google_sheets_service import GoogleSheetsService

if __name__ == "__main__":
    # todo python -m tests.test_google_sheets_service
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    api_key = config.get("apps_scripts", "api_key")
    save_character_endpoint = config.get("apps_scripts", "save_character_endpoint")
    get_characters_endpoint = config.get("apps_scripts", "get_characters_endpoint")
    google_sheets_service = GoogleSheetsService(
        api_key=api_key,
        save_character_endpoint=save_character_endpoint,
        get_characters_endpoint=get_characters_endpoint)

    google_sheets_service.sync_data()
