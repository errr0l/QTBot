from utils.common import load_characters_from_json

if __name__ == '__main__':
    file_path = "data/mock_data.json"
    characters = load_characters_from_json(file_path)
    print(characters)
