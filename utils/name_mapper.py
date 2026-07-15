from typing import Optional, List
from services.character_service import CharacterService


class NameMapper:
    def __init__(self, character_service: CharacterService):
        self.character_service = character_service
        self._build_index()

    def _build_index(self):
        """构建名称索引，提高查询效率；需要依赖character_service"""
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

    # def add_mapping(self, canonical_name: str, aliases: List[str]):
    #     """添加新的名称映射"""
    #     # 检查是否已存在
    #     existing_item = None
    #     for item in self.data:
    #         if item["name"] == canonical_name:
    #             existing_item = item
    #             break
    #
    #     if existing_item:
    #         # 更新现有项
    #         existing_aliases = set(existing_item["aliases"])
    #         new_aliases = set(aliases)
    #         all_aliases = list(existing_aliases.union(new_aliases))
    #         existing_item["aliases"] = all_aliases
    #     else:
    #         # 添加新项
    #         self.data.append({
    #             "name": canonical_name,
    #             "aliases": aliases
    #         })
    #
    #     # 重建索引
    #     self._build_index()

    def get_canonical_name(self, query: str) -> Optional[str]:
        """根据查询词获取标准名称"""
        return self.name_index.get(query.lower())

    def get_all_aliases(self, canonical_name: str) -> List[str]:
        """获取某个角色的所有别名"""
        for item in self.data:
            if item["name"] == canonical_name:
                return item.get("aliases", [])
        return []

    # def get_all_mappings(self) -> List[Dict]:
    #     """获取所有映射"""
    #     return self.data.copy()

    def refresh_index(self):
        """刷新索引"""
        self._build_index()

    @staticmethod
    def _calc_fuzzy_score(query_lower: str, target_lower: str) -> float:
        """计算字符顺序匹配度：query 字符按顺序在 target 中出现的匹配分数"""
        qi = 0
        score = 0.0
        prev_pos = -2

        for ti, tc in enumerate(target_lower):
            if qi < len(query_lower) and tc == query_lower[qi]:
                if ti == prev_pos + 1:
                    score += 2  # 连续匹配加分
                else:
                    score += 1
                score += max(0.0, 1.0 - ti / len(target_lower)) * 3  # 位置靠前加分
                prev_pos = ti
                qi += 1

        if qi < len(query_lower):
            return 0.0  # 有字符未匹配到
        return score

    def fuzzy_search(self, query: str, max_results: int = 5) -> List[str]:
        """
        优先匹配标准名，匹配不上再逐个试别名，
        只要有一个命中就采用该角色的标准名，
        按匹配分降序排列，取前 N 个
        """
        query_lower = query.lower()
        scored = []

        for item in self.data:
            # 先试标准名
            score = self._calc_fuzzy_score(query_lower, item["name"].lower())
            if score > 0:
                scored.append((score, item["name"]))
                continue
            # 标准名不匹配，试别名，有一个匹配即可
            for alias in item.get("aliases", []):
                score = self._calc_fuzzy_score(query_lower, alias.lower())
                if score > 0:
                    scored.append((score, alias))
                    break

        scored.sort(key=lambda x: -x[0])
        return [name for _, name in scored[:max_results]]

    def get_alia4characters(self):
        """统计数据；只包含三年级角色与女神"""
        result = {
            "女神": [],
            "角色": []
        }
        for char_data in self.data:
            year = char_data['year']

            if year == "3":
                container = result['角色']
            elif year is None or year == "":
                container = result['女神']
            else:
                continue
            aliases = char_data.get("aliases")
            if aliases:
                # 一般第一个别名是最常用的
                container.append(aliases[0])
            else:
                container.append(char_data.get("name"))
        return result
    def get_alia4goddesses(self):
        result = self.get_alia4characters()
        del result['角色']
        return result
    # def show_all(self):
    #     for key in self.name_index.keys():
    #         print(key, self.name_index.get(key))


__all__ = ['NameMapper']


# if __name__ == '__main__':
#     # 全局实例
#     name_mapper = NameMapper("/data/character_aliases.json")
#     print(name_mapper.get_all_mappings())
#     name_mapper.show_all()
