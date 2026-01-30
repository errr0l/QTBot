from typing import Optional
from containers.app_container import AppContainer

_container: Optional[AppContainer] = None


def set_container(container: AppContainer) -> None:
    global _container
    _container = container


def get_container() -> AppContainer:
    if _container is None:
        raise RuntimeError("容器未初始化")
    return _container
