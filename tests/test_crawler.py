from services.qt_wiki_crawler import QTWikiCrawler, parse_character_page, parse_goodness_page
from bs4 import BeautifulSoup, element
from services.character_service import CharacterService

# def test_parse_list_page():
#     r = crawler.parse_list_page("/Goddess_List")
#     print(r)


if __name__ == "__main__":
    crawler = QTWikiCrawler()
    # crawler.run()
    entry = {
        "name": "xxx",
        "url": "",
        "avatar": "",
        "awakened_avatar": ""
    }

    with open("Athana.html", "r", encoding="utf-8") as _f:
        html = _f.read()
        entry['html'] = html
        character = parse_goodness_page(entry)
        # print(character.skins)
        soup = BeautifulSoup(html, 'lxml')
        # character_entry['soup'] = soup
        description_tag = soup.find('meta', attrs={'name': 'description'})
        print(description_tag)
        if description_tag:
            description = description_tag.get('content', '')
            print(description)
            # if description and 'Goddesses' in description:
            #     # character_entry['type'] = 2
            #     print(2)
        # print("--")
        # print(character.talent_tree.descriptions)
        # print(character.bonds)

    # with open("/Users/errol/personalplace/QTBot/Vanadis.html", "r", encoding="utf-8") as _f:
    #     html = _f.read()
    #     entry['html'] = html
    #     character = parse_goodness_page(entry)
    #     print(character)
    # with open(file_path, "r", encoding="utf-8") as f:
    #     data = json.load(f)
    # entries = crawler.parse_character_page(entry)
