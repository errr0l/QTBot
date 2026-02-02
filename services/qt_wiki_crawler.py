import random
import time
from typing import List

from bo.wiki_scrape_instructions import SuperInstructions
from entities.character import Character
import requests
from bs4 import BeautifulSoup, element
from requests.exceptions import RequestException

from services.character_service import CharacterService
from nonebot import logger
from utils.common import convert_single_dict_attributes_to_json


def build_character_entry(entry: element.Tag) -> dict:
    """包含角色名称、角色头像、角色页面链接"""
    character = {}
    name_a = entry.select_one(".name a")
    character['name'] = name_a.get_text(strip=True)
    character['url'] = name_a.get("href", "")
    default_img = entry.select_one(".default a img")
    default_avatar = default_img.get("src", "")
    character['avatar'] = default_avatar
    awakened = entry.select_one(".on-hover a img")
    character['awakened_avatar'] = awakened.get("src", "")
    return character


def build_character_entry_v2(name: str) -> dict:
    character = {
        "name": name,
        "url": f"/wiki/{name}",  # 一般是这个,
        "avatar": "",
        "awakened_avatar": "",
        "type": 1
    }

    return character


def append_urls(img_list: List[element.Tag], containers: List):
    if img_list and len(img_list) > 0:
        for item in img_list:
            containers.append(item.get("src"))


def set_background(nodes: List[element.Tag], dict_character: dict):
    texts = []

    for node in nodes[::-1]:
        text = node.get_text().strip()
        if text != '':
            texts.append(text)
    dict_character['background'] = "\n\n".join(texts)


def set_skill_desc(nodes: List[element.Tag]):
    skill_descriptions = []
    # 倒序，从1星开始添加
    for item in nodes:
        # 加strip参数，反而使得显示不正常
        texts = []
        for p in item.find_all("p"):
            text = p.get_text().strip()
            if text != '':
                texts.append(text)
        desc = "\n\n".join(texts)
        skill_descriptions.append(desc)
    return skill_descriptions


def get_skin_node_ids(node: element.Tag):
    panel_top = node.find("ul", id="mw-panel-toc-list")
    li_list = panel_top.find_all("li", recursive=False)
    skin_node_ids = []
    for item in li_list:
        if "skin" in item.get("id").lower():
            skin_node_ids.append(item.find("a").get("href"))
    return skin_node_ids


def parse_character_page(entry: dict) -> Character:
    """解析角色页面，返回一个Character实体对象, 注：此时该Character的技能为dict，parse_goodness_page同理"""
    if entry.get("type") == 2:
        return parse_goodness_page(entry)
    avatar = entry.get("avatar")
    awakened_avatar = entry.get("awakened_avatar")
    dict_character = {
        "name": entry.get("name"),
        "avatars": [],
        "type": entry.get("type")
    }
    logger.info(dict_character)
    logger.info(f"解析[{entry.get('name')}]页面")
    if avatar:
        dict_character['avatars'].append(avatar)
    if awakened_avatar:
        dict_character['avatars'].append(awakened_avatar)

    soup = entry.get("soup")
    if not soup:
        html = entry.pop("html")
        soup = BeautifulSoup(html, 'lxml')
    char_info = soup.find("div", id="char-info")

    tables = char_info.select(".infobox-table.fill")
    # 部门、年级、元素
    table_1 = tables[0]
    spans = table_1.find_all("td", class_="right-edge")
    dict_character['club'] = spans[0].get_text(strip=True)
    dict_character['element'] = spans[1].get_text(strip=True)
    dict_character['year'] = spans[2].get_text(strip=True)

    # 身高、体重等（有可能为空）
    table_2 = tables[1]
    spans = table_2.find_all("td", class_="right-edge")
    extra = {
        'height': spans[0].get_text(strip=True).replace(" ", ""),
        'weight': spans[1].get_text(strip=True).replace(" ", ""),
        'body_size': spans[2].get_text(strip=True),
        'birthday': spans[3].get_text(strip=True)
    }
    dict_character['hobbies'] = spans[5].get_text(strip=True)
    dict_character['extra'] = extra

    # 背景
    background_h1 = soup.find("h1", id="Background")
    section_1 = background_h1.find_next("section")

    section_first_div = section_1.find("div")
    background_descriptions = section_first_div.find_previous_siblings("p")
    set_background(background_descriptions, dict_character)

    skill_divs = section_1.find_all("div", recursive=False)

    base_form_h1 = skill_divs[0].find("h1", id="Base_Form")
    base_form_div = base_form_h1.find_next("div")

    # 卡面&小人
    img_list = base_form_div.find_all("img")
    append_urls(img_list, dict_character['avatars'])

    # 技能
    arena_skill_h1 = skill_divs[0].find("h1", id="Arena_Skill")
    arena_skill_div = arena_skill_h1.find_next("div")
    table_tr_list = arena_skill_div.select(".info-table tr")
    skill_name = table_tr_list[0].find("p", class_="skill-name").get_text(strip=True)
    skill_icon = table_tr_list[0].find("img").get("src")
    skill_cooldown = int(table_tr_list[1].find("td").get_text(strip=True))
    # 倒序，从1星开始添加
    skill_descriptions = set_skill_desc(table_tr_list[2].find_all("article")[::-1])
    arena_skill = Character.CharacterSkill(
        name=skill_name, icon=skill_icon, cooldown=skill_cooldown, descriptions=skill_descriptions)
    dict_character['arena_skill'] = arena_skill
    # 觉醒卡面&小人【只有三年级角色，Emily未觉醒】
    if dict_character['year'] == "3" and len(skill_divs) > 1:
        awakened_form_h1 = skill_divs[1].find("h1", id="Awakened_Form")
        awakened_form_div = awakened_form_h1.parent.find_next("div")
        img_list = awakened_form_div.find_all("img")
        append_urls(img_list, dict_character['avatars'])

        awakening_passive_h1 = skill_divs[1].find("h1", id="Awakening_Passive")
        awakening_passive_div = awakening_passive_h1.parent.find_next("div")
        table_tr_list = awakening_passive_div.select(".info-table tr")
        awakening_passive_name = table_tr_list[0].find("p").get_text(strip=True)
        awakening_passive_icon = table_tr_list[0].find("img").get("src")
        awakening_descriptions = set_skill_desc(table_tr_list[1].find_all("article")[::-1])
        awakening_passive = Character.CharacterPassiveSkill(
            name=awakening_passive_name, icon=awakening_passive_icon, descriptions=awakening_descriptions)
        dict_character['awakening_passive'] = awakening_passive

        # 天赋
        talent_tree_h1 = soup.find("h1", id="Talent_Tree")
        talent_tree_section = talent_tree_h1.find_next("section")
        talent_tree_name_div = talent_tree_section.find("div")
        talent_tree_name = talent_tree_name_div.find("p").get_text(strip=True)
        talent_tree_icon = talent_tree_name_div.find("img").get("src")
        talent_tree_descriptions = set_skill_desc(talent_tree_section.find_all("article")[::-1])
        dd_list = talent_tree_section.find("dl").find_all("dd")
        talent_tree_attributes = ""
        for item in dd_list:
            talent_tree_attributes += item.get_text(strip=True)
        talent_tree = Character.CharacterPassiveSkill(
            name=talent_tree_name,
            icon=talent_tree_icon, descriptions=talent_tree_descriptions, extra=talent_tree_attributes)
        dict_character['talent_tree'] = talent_tree

    bonds_h1 = soup.find("h1", id="Bonds")
    bonds_section = bonds_h1.find_next("section")
    divs = bonds_section.select(".section.full")
    bonds = []
    for item in divs:
        bonds.append(item.find("div", recursive=False).get_text(strip=True))
    dict_character['bonds'] = "、".join(bonds)

    # 皮肤
    skin_node_ids = get_skin_node_ids(soup)
    skins = []
    for item in skin_node_ids:
        skin_h1 = soup.select_one(item)
        if skin_h1:
            skin = {
                "name": skin_h1.get_text(strip=True),
                "images": [],
            }
            character_info = skin_h1.find_next("section")

            if not character_info:
                continue
            sections = character_info.find_all('div', class_="section")
            if len(sections) != 2:
                continue
            images = sections[0].find_all("img")
            for image in images:
                skin['images'].append(image.get("src"))
            values = sections[1].find_all("tr")[1:]
            descriptions = []
            for val in values[::-1]:
                tds = val.find_all("td")
                descriptions.append(f"{tds[0].get_text(strip=True)}\t{tds[1].get_text(strip=True)}\t{tds[2].get_text(strip=True)}\t{tds[3].get_text(strip=True)}")
            skin['descriptions'] = descriptions
            skins.append(skin)
    return Character(nicknames="", skins=skins, **dict_character)


def parse_goodness_page(entry: dict) -> Character:
    """解析角色页面，返回一个Character实体对象"""
    dict_character = {
        "name": entry.get("name"),
        "avatars": [],
        "type": entry.get("type")
    }
    soup = entry.get("soup")
    if not soup:
        html = entry.pop("html")
        soup = BeautifulSoup(html, 'lxml')
    char_info = soup.find("div", id="char-info")

    table_1 = char_info.select_one(".infobox-table.fill")
    # 部门、年级、元素
    spans = table_1.find_all("td", class_="right-edge")
    dict_character['club'] = spans[0].get_text(strip=True)
    extra = {
        'height': spans[1].get_text(strip=True).replace(" ", ""),
        'weight': spans[2].get_text(strip=True).replace(" ", ""),
        'body_size': spans[3].get_text(strip=True),
        'birthday': spans[4].get_text(strip=True)
    }
    dict_character['extra'] = extra

    # 背景
    background_h1 = soup.find("h1", id="Background")
    section_1 = background_h1.find_next("section")

    section_first_div = section_1.find("div")
    background_descriptions = section_first_div.find_previous_siblings("p")
    set_background(background_descriptions, dict_character)

    skill_divs = section_first_div.find_all("div", recursive=False)

    images_h1 = skill_divs[0].find("h1", id="Images")
    character_info_div = images_h1.find_next("div")
    # 卡面&小人
    img_list = character_info_div.find_all("img")
    append_urls(img_list, dict_character['avatars'])

    # 技能
    arena_skill_h1 = skill_divs[1].find("h1", id="Arena_Skill")
    arena_skill_div = arena_skill_h1.find_next("div")
    table_tr_list = arena_skill_div.select(".info-table tr")
    skill_name = table_tr_list[0].find("p", class_="skill-name").get_text(strip=True)
    skill_icon = None
    skill_img = table_tr_list[0].find("img")
    if skill_img:
        skill_icon = skill_img.get("src")
    skill_cooldown = int(table_tr_list[1].find("td").get_text(strip=True))
    skill_descriptions = set_skill_desc(table_tr_list[2].find_all("article")[::-1])
    arena_skill = Character.CharacterSkill(
        name=skill_name, icon=skill_icon, cooldown=skill_cooldown, descriptions=skill_descriptions)
    dict_character['arena_skill'] = arena_skill

    # 皮肤
    panel_top = soup.find("ul", id="mw-panel-toc-list")
    li_list = panel_top.find_all("li", recursive=False)
    skin_node_ids = []
    for item in li_list:
        if "skin" in item.get("id").lower():
            skin_node_ids.append(item.find("a").get("href"))

    skins = []
    for item in skin_node_ids:
        skin_h1 = soup.select_one(item)
        if skin_h1:
            skin = {
                "name": skin_h1.get_text(strip=True),
                "images": [],
            }
            character_info = skin_h1.find_next("div")
            images = character_info.find_all("img")
            for image in images:
                skin['images'].append(image.get("src"))
            skill_section = skin_h1.parent.find_next_sibling("div")
            table_tr_list = skill_section.select(".info-table tr")
            skill_name = table_tr_list[0].find("p", class_="skill-name").get_text(strip=True)
            skill_icon = table_tr_list[0].find("img").get("src")
            passive_skill = {
                "name": skill_name,
                "icon": skill_icon,
                "descriptions": set_skill_desc(table_tr_list[1].find_all("article")[::-1])
            }
            skin['passive_skill'] = passive_skill
            skins.append(skin)
    return Character(
        nicknames="",
        element="",
        year="",
        bonds="",
        hobbies="",
        skins=skins,
        **dict_character
    )


def handle_character_entries(entries: List[dict]) -> List[Character]:
    characters = []
    for item in entries:
        if item.get("html") is None:
            continue
        if item.get("type") == 1:
            character = parse_character_page(item)
        else:
            character = parse_goodness_page(item)
        characters.append(character)
    return characters


class QTWikiCrawler:
    """QT wiki页面爬虫服务"""

    def __init__(
            self,
            list_page_paths: List[str],
            character_service: CharacterService):
        self.wiki_base_url = "https://projectqt.miraheze.org"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        # 角色与女神
        self.list_page_paths = list_page_paths
        self.character_service = character_service

    def parse_list_page(self, list_page_path: str) -> List[dict]:
        character_entries = []
        response = requests.get(list_page_path, headers=self.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        entries = soup.find_all("div", class_="char-list-entry")
        if 'Goddess' in list_page_path:
            char_type = 2
        else:
            char_type = 1
        for item in entries:
            character_entry = build_character_entry(item)
            character_entry['url'] = self.wiki_base_url + character_entry['url']
            character_entry['type'] = char_type
            character_entries.append(character_entry)
        return character_entries

    def scrape_character_and_save(self, name):
        character = self.scrape_character(name)
        self.character_service.save_character(character)
        return character

    def scrape_character_and_update_fields(self, name, fields: List[str]):
        character = self.scrape_character(name=name)
        dict_char = character.to_dict()
        dict_char = convert_single_dict_attributes_to_json(dict_char)
        r = self.character_service.update_character_with_fields(character=dict_char, fields=fields)
        if r:
            return character.name

    def scrape_character(self, name: str):
        character_entry = build_character_entry_v2(name)
        character_entry['url'] = self.wiki_base_url + character_entry['url']
        try:
            response = requests.get(character_entry['url'], headers=self.headers)
            soup = BeautifulSoup(response.text, 'lxml')
            character_entry['soup'] = soup
            description_tag = soup.find('meta', attrs={'name': 'description'})
            if description_tag:
                description = description_tag.get('content', '')
                if description and 'Goddesses' in description:
                    character_entry['type'] = 2
            return parse_character_page(entry=character_entry)
        except RequestException as e:
            logger.info(e)
            logger.info("抓取失败")

    def run(self, force: bool = False, super_instructions: SuperInstructions = None) -> dict:
        logger.info("开始抓取列表页数据...")
        character_map = {}
        # 如果已经存在于数据库。则跳过
        if not force:
            character_map = self.character_service.build_character_map()
        skip_names = []
        all_entries = []
        if super_instructions and super_instructions.type > 0:
            index = super_instructions.type - 1
            list_page_paths = [self.list_page_paths[index]]
        else:
            list_page_paths = self.list_page_paths
        for path in list_page_paths:
            url = self.wiki_base_url + path
            logger.info(f"抓取{url}页面...")
            entries = self.parse_list_page(url)
            all_entries = all_entries + entries
            time.sleep(6)
        if super_instructions and 0 < super_instructions.count < len(all_entries):
            logger.info(f"随机抓取{super_instructions.count}条...")
            all_entries = random.sample(all_entries, super_instructions.count)
        filtered = []
        for entry in all_entries:
            if not force and entry.get("name") in character_map:
                logger.info(f"skip: {entry}")
                skip_names.append(entry.get("name"))
                continue
            filtered.append(entry)
        logger.info("开始抓取角色页面数据, 这个过程要花费一些时间...")
        for entry in filtered:
            url = entry.get("url")
            logger.info(f"抓取{url}页面...")
            try:
                response = requests.get(url, headers=self.headers)
                entry['html'] = response.text
                time.sleep(6)
            except RequestException as e:
                logger.info(e)
                logger.info("停止抓取")
                break
        logger.info("开始解析...")
        names = []
        characters = handle_character_entries(filtered)
        size = len(characters)
        if size > 0:
            for char in characters:
                names.append(char.name)
            self.character_service.save_characters(characters)
            logger.info(f"共{size}个数据，已保存至数据库")
        else:
            logger.info(f"无数据")
        return {
            "names": names,
            "skip_names": skip_names,
            "characters": characters
        }
