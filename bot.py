import nonebot
# from nonebot.adapters.console import Adapter
from nonebot.adapters.qq import Adapter

# 初始化 NoneBot，指定控制台驱动
nonebot.init()

# 获取 ASGI 应用
# app = nonebot.get_asgi()
# 获取驱动
driver = nonebot.get_driver()
driver.register_adapter(Adapter)


if __name__ == "__main__":
    # 加载内置插件
    nonebot.load_builtin_plugins("echo")
    nonebot.load_plugins("plugins")
    nonebot.run()
