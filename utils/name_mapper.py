# import json
# from pathlib import Path
from typing import Optional, Dict, List
from services.character_service import CharacterService


class NameMapper:
    def __init__(self, character_service: CharacterService):
        # self.config_path = Path(config_path)
        # self.data = self.load_config()
        self.character_service = character_service
        self._build_index()

    # def load_config(self) -> List[Dict]:
    #     """加载配置文件"""
    #     if self.config_path.exists():
    #         with open(self.config_path, 'r', encoding='utf-8') as f:
    #             return json.load(f)
    #     return []

    def _build_index(self):
        """构建名称索引，提高查询效率"""
        self.name_index = {}
        self.data = self.character_service.build_character_alias()
        # 遍历配置列表
        for item in self.data:
            canonical_name = item["name"]
            aliases = item.get("aliases", [])

            # 添加标准名称
            self.name_index[canonical_name.lower()] = canonical_name

            # 添加所有别名
            for alias in aliases:
                if alias:
                    self.name_index[alias.lower()] = canonical_name

    def add_mapping(self, canonical_name: str, aliases: List[str]):
        """添加新的名称映射"""
        # 检查是否已存在
        existing_item = None
        for item in self.data:
            if item["name"] == canonical_name:
                existing_item = item
                break

        if existing_item:
            # 更新现有项
            existing_aliases = set(existing_item["aliases"])
            new_aliases = set(aliases)
            all_aliases = list(existing_aliases.union(new_aliases))
            existing_item["aliases"] = all_aliases
        else:
            # 添加新项
            self.data.append({
                "name": canonical_name,
                "aliases": aliases
            })

        # 重建索引
        self._build_index()
        # self.save_config()

    # def remove_mapping(self, canonical_name: str):
    #     """删除映射"""
    #     self.data = [item for item in self.data if item["name"] != canonical_name]
    #     self._build_index()
    #     self.save_config()

    # def add_alias(self, canonical_name: str, alias: str):
    #     """为已有角色添加别名"""
    #     for item in self.data:
    #         if item["name"] == canonical_name:
    #             if alias not in item["aliases"]:
    #                 item["aliases"].append(alias)
    #                 self._build_index()
    #                 self.save_config()
    #             break

    def get_canonical_name(self, query: str) -> Optional[str]:
        """根据查询词获取标准名称"""
        return self.name_index.get(query.lower())

    def get_all_aliases(self, canonical_name: str) -> List[str]:
        """获取某个角色的所有别名"""
        for item in self.data:
            if item["name"] == canonical_name:
                return item.get("aliases", [])
        return []

    def get_all_mappings(self) -> List[Dict]:
        """获取所有映射"""
        return self.data.copy()

    # def save_config(self):
    #     """保存配置到文件"""
    #     self.config_path.parent.mkdir(parents=True, exist_ok=True)
    #     with open(self.config_path, 'w', encoding='utf-8') as f:
    #         json.dump(self.data, f, ensure_ascii=False, indent=2)

    def refresh_index(self):
        """刷新索引"""
        self._build_index()

    def show_all(self):
        for key in self.name_index.keys():
            print(key, self.name_index.get(key))


__all__ = ['NameMapper']


# if __name__ == '__main__':
#     # 全局实例
#     name_mapper = NameMapper("/data/character_aliases.json")
#     print(name_mapper.get_all_mappings())
#     name_mapper.show_all()
