"""This module defineds the JSON class mapping graph."""
from __future__ import annotations
from typing import Union, final, TYPE_CHECKING

from .config import Config
from .keypath_utils import reference_key
from .exceptions import (JSONClassRedefinitionException,
                         JSONClassTypedDictRedefinitionException,
                         JSONClassNotFoundException,
                         JSONClassTypedDictNotFoundException)
if TYPE_CHECKING:
    from .cdef import Cdef


@final
class CGraph:
    """JSON classes are defined on class graphs. Classes in the same graph
    share default configurations and can interoperate with each other. A class
    is guaranteed to have a unique name in it's graph. Different graphs serve
    as different naming spaces.
    """

    _graph_map: dict[str, CGraph] = {}
    """The graph map on which graph objects are stored."""

    _initialized_map: dict[str, bool] = {}
    """The map on which graphs' initialization status are recorded."""

    def __new__(cls: type[CGraph], name: str) -> CGraph:
        """The `CGraph` class returns a shared graph object by it's
        name.
        """
        if not cls._graph_map.get(name):
            cls._graph_map[name] = super(CGraph, cls).__new__(cls)
        return cls._graph_map.get(name)

    def __init__(self: CGraph, name: str) -> None:
        """Find a class graph by it's name. A new one is created if it's not
        exist.

        Args:
            name (str): The name of the graph.
        """
        if self.__class__._initialized_map.get(name):
            return
        self._name: str = name
        self._map: dict[str, Cdef] = {}
        self._dict_map: dict[str, type[dict]] = {}
        self._enum_map: dict[str, type] = {}
        self._default_config = Config(class_graph=self.name,
                                      camelize_json_keys=True,
                                      strict_input=True,
                                      key_transformer=reference_key,
                                      validate_all_fields=False,
                                      soft_delete=False,
                                      abstract=False,
                                      reset_all_fields=False,
                                      on_create=[],
                                      on_save=[],
                                      on_delete=[],
                                      can_create=[],
                                      can_update=[],
                                      can_delete=[],
                                      can_read=[])
        self.__class__._initialized_map[name] = True
        return None

    def __repr__(self) -> str:
        return f'[{self._name}]'

    @property
    def name(self: CGraph) -> str:
        """The name of this class graph."""
        return self._name

    @property
    def default_config(self: CGraph) -> Config:
        """The default configuration used on this class graph."""
        return self._default_config

    def put(self: CGraph, cdef: Cdef) -> None:
        """Put a class onto this class graph.

        Args:
            class_ (type): The JSON class which will be put onto this graph.

        Raises:
            JSONClassRedefinitionException: This exception is raised if a \
                new class with existing name is defined.
        """
        exist_definition = self._map.get(cdef.name)
        if exist_definition:
            raise JSONClassRedefinitionException(cdef.cls,
                                                 exist_definition.cls)
        self._map[cdef.name] = cdef

    def fetch(self: CGraph,
              name_or_class: Union[str, type]) -> Cdef:
        """Fetch a class by it's name from this class graph.

        Args:
            name_or_class (Union[str, type]): The name of the class to be \
                fetched or the class itself.

        Raises:
            JSONClassNotFoundException: This exception is raised if a class \
                definition with `name` is not found.
        """
        if isinstance(name_or_class, type):
            name = name_or_class.__name__
        else:
            name = name_or_class
        try:
            return self._map[name]
        except KeyError:
            raise JSONClassNotFoundException(name, self.name)

    def has(self: CGraph,
            name_or_class: Union[str, type]) -> bool:
        """Test if class with name is registered in the graph.

        Args:
            name_or_class (Union[str, type]): The name of the class to be \
                fetched or the class itself.

        Returns:
            bool: Returns True if this class is registered in the graph.
        """
        if isinstance(name_or_class, type):
            name = name_or_class.__name__
        else:
            name = name_or_class
        return self._map.get(name) is not None

    def put_dict(self: CGraph, dict_class: type[dict]) -> None:
        """Put a typed dict class onto this class graph.

        Args:
            dict_class (type): The typed dict class which will be put onto this
            graph.

        Raises:
            JSONClassRedefinitionException: This exception is raised if a \
                new typed dict class with existing name is defined.
        """
        exist_def = self._dict_map.get(dict_class.__name__)
        if exist_def:
            raise JSONClassTypedDictRedefinitionException(dict_class,
                                                          exist_def.cls)
        self._dict_map[dict_class.__name__] = dict_class

    def fetch_dict(self: CGraph,
                   dc_or_name: Union[type[dict], str]) -> type[dict]:
        """Fetch a typed dict class by it's name from this class graph.

        Args:
            dc_or_name (Union[type[dict], str]): The name of the typed dict
            class to be fetched or the class itself.

        Raises:
            JSONClassNotFoundException: This exception is raised if a class \
                definition with `name` is not found.
        """
        if isinstance(dc_or_name, type):
            name = dc_or_name.__name__
        else:
            name = dc_or_name
        try:
            return self._dict_map[name]
        except KeyError:
            raise JSONClassTypedDictNotFoundException(name, self.name)

    def has_dict(self: CGraph,
                 dc_or_name: Union[type[dict], str]) -> bool:
        """Test if a typed dict class with name is registered in the graph.

        Args:
            dc_or_name (Union[type[dict], str]): The name of the typed dict
            class to be fetched or the class itself.

        Returns:
            bool: Returns True if this typed dict class is registered in the
            graph.
        """
        if isinstance(dc_or_name, type):
            name = dc_or_name.__name__
        else:
            name = dc_or_name
        return self._dict_map.get(name) is not None

    def put_enum(self: CGraph, enum_class: type) -> None:
        """Put a enum class onto this class graph.

        Args:
            enum_class (type): The enum class which will be put onto this
            graph.

        Raises:
            JSONClassRedefinitionException: This exception is raised if a \
                new enum class with existing name is defined.
        """
        exist_def = self._enum_map.get(enum_class.__name__)
        if exist_def:
            raise JSONClassTypedDictRedefinitionException(enum_class,
                                                          exist_def.cls)
        self._enum_map[enum_class.__name__] = enum_class

    def fetch_enum(self: CGraph,
                   ec_or_name: Union[type[dict], str]) -> type[dict]:
        """Fetch a enum class by it's name from this class graph.

        Args:
            ec_or_name (Union[type[dict], str]): The name of the enum class to
            be fetched or the class itself.

        Raises:
            JSONClassNotFoundException: This exception is raised if a class \
                definition with `name` is not found.
        """
        if isinstance(ec_or_name, type):
            name = ec_or_name.__name__
        else:
            name = ec_or_name
        try:
            return self._enum_map[name]
        except KeyError:
            raise JSONClassTypedDictNotFoundException(name, self.name)

    def has_enum(self: CGraph,
                 ec_or_name: Union[type[dict], str]) -> bool:
        """Test if a enum class with name is registered in the graph.

        Args:
            ec_or_name (Union[type[dict], str]): The name of the enum class to
            be fetched or the class itself.

        Returns:
            bool: Returns True if this enum class is registered in the graph.
        """
        if isinstance(ec_or_name, type):
            name = ec_or_name.__name__
        else:
            name = ec_or_name
        return self._enum_map.get(name) is not None