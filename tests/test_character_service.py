from services.character_service import CharacterService

if __name__ == '__main__':
    # todo python -m tests.test_character_service
    character_service = CharacterService(db_helper=None)
    character = {
        "skins": 'ssss',
        'arena_skill': 'aaaa'
    }
    character_service.update_character_with_fields(character=character, fields=['skins'])
