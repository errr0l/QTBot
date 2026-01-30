from services.translation_service import TranslationService
import configparser


if __name__ == "__main__":
    # todo python -m tests.test_translation_service
    query = "Hello, world."
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')  # 推荐指定 encoding
    print(config['baidu_fanyi'].get("endpoint"))
    service = TranslationService(
        appid=config['baidu_fanyi'].get("appid"),
        app_key=config['baidu_fanyi'].get("app_key"),
        endpoint=config['baidu_fanyi'].get("endpoint"),
    )
    result = service.translate(query)
    print(result)
