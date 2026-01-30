from dependency_injector import containers, providers
from services.character_service import CharacterService
from utils.name_mapper import NameMapper
from db.db_helper import DBHelper
from services.translation_service import TranslationService
from services.qt_wiki_crawler import QTWikiCrawler
from services.google_sheets_service import GoogleSheetsService


class AppContainer(containers.DeclarativeContainer):
    """应用依赖注入容器"""

    # 配置
    config = providers.Configuration()
    db_helper = providers.Singleton(DBHelper, db_path=config.db.db_path)
    character_service = providers.Singleton(
        CharacterService,
        db_helper=db_helper
    )
    name_mapper = providers.Singleton(
        NameMapper,
        character_service=character_service
    )
    translation_service = providers.Singleton(
        TranslationService,
        appid=config.baidu_fanyi.appid,
        app_key=config.baidu_fanyi.app_key,
        endpoint=config.baidu_fanyi.endpoint,
    )
    google_sheets_service = providers.Singleton(
        GoogleSheetsService,
        character_service=character_service,
        api_key=config.apps_scripts.api_key,
        save_characters_endpoint=config.apps_scripts.save_characters_endpoint,
        get_characters_endpoint=config.apps_scripts.get_characters_endpoint
    )
    qt_wiki_crawler = providers.Singleton(
        QTWikiCrawler,
        list_page_paths=providers.Callable(
            lambda s: [p.strip() for p in s.split(",") if p.strip()],
            config.crawler.list_page_paths
        ),
        character_service=character_service,
        google_sheets_service=google_sheets_service
    )

    # 所有服务【扫描注入目标，@inject、Provide[AppContainer.character_service]等】
    wiring_config = containers.WiringConfiguration(
        modules=[
            "plugins.wiki",
        ]
    )
