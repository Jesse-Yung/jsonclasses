"""module for map modifier."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING, Callable
from .modifier import Modifier
if TYPE_CHECKING:
    from ..ctx import Ctx

class MapModifier(Modifier):
    """Map modifier maps number value."""

    def __init__(self, callback: Callable) -> None:
        if not callable(callback):
            raise ValueError('map callback is not callable')
        self.callback = callback


    def transform(self, ctx: Ctx) -> Any:
        if type(ctx.val) is list:
            return list(map(self.callback, ctx.val))
        if type(ctx.val) is tuple:
            return tuple(map(self.callback, ctx.val))
        else:
            return ctx.val