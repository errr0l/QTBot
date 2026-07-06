import nonebot
# from nonebot.adapters.console import Adapter
from nonebot.adapters.qq import Adapter

# 初始化 NoneBot，指定控制台驱动
nonebot.init()

# 获取驱动
driver = nonebot.get_driver()


@driver.on_startup
async def _():
    from containers.app_container import container
    container.init()


driver.register_adapter(Adapter)


if __name__ == "__main__":
    # 加载内置插件
    nonebot.load_builtin_plugins("echo")
    nonebot.load_plugins("plugins")
    nonebot.run()
