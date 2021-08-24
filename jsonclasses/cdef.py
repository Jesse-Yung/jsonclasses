"""
This module defines `Cdef`. Each JSON class has its own class
definition. The class definition object contains detailed information about how
user defines a JSON class. This is used by the framework to lookup class fields
and class field settings.
"""
from __future__ import annotations
from jsonclasses.jobject import JObject
from typing import Optional, final, TYPE_CHECKING
from dataclasses import fields as dataclass_fields
from inflection import camelize
from .jfield import JField
from .fdef import FieldStorage, DeleteRule
from .rtypes import rtypes
from .exceptions import LinkedFieldUnmatchException
if TYPE_CHECKING:
    from .jconf import JConf
    from .types import Types


@final
class Cdef:
    """Class definition represents the class definition of JSON classes. Each
    JSON class has its own class definition. The class definition object
    contains detailed information about how user defines a JSON class. This is
    used by the framework to lookup class fields and class field settings.
    """

    def __init__(self: Cdef, cls: type[JObject], jconf: JConf) -> None:
        """
        Initialize a new class definition.

        Args:
            cls (type): The JSON class for which the class definition is \
                created.
            jconf (JConf): The configuration object for the targeted class.
        """
        from .types import Types
        self._ref_resolved = False
        self._cls = cls
        jconf._cls = cls
        self._name: str = cls.__name__
        self._jconf: JConf = jconf
        self._list_fields: list[JField] = []
        self._dict_fields: dict[str, JField] = {}
        self._primary_field: Optional[JField] = None
        self._created_at_field: Optional[JField] = None
        self._updated_at_field: Optional[JField] = None
        self._deleted_at_field: Optional[JField] = None
        self._deny_fields: list[JField] = []
        self._nullify_fields: list[JField] = []
        self._cascade_fields: list[JField] = []
        self._field_names: list[str] = []
        self._camelized_field_names: list[str] = []
        self._reference_names: list[str] = []
        self._camelized_reference_names: list[str] = []
        self._assign_operator_fields: list[JField] = []
        for field in dataclass_fields(cls):
            name = field.name
            self._field_names.append(name)
            if isinstance(field.default, Types):
                types = field.default
                default = None
            elif field.default == field.default_factory:
                types = rtypes(field.type)
                default = None
            else:
                types = rtypes(field.type)
                default = field.default
            types.fdef._cdef = self
            jfield = JField(cdef=self, name=name, default=default, types=types)
            self._camelized_field_names.append(jfield.json_name)
            self._list_fields.append(jfield)
            self._dict_fields[name] = jfield
            if types.fdef._primary:
                self._primary_field = jfield
            if types.fdef._usage == 'created_at':
                self._created_at_field = jfield
            elif types.fdef._usage == 'updated_at':
                self._updated_at_field = jfield
            elif types.fdef._usage == 'deleted_at':
                self._deleted_at_field = jfield
            if types.fdef._delete_rule == DeleteRule.DENY:
                self._deny_fields.append(jfield)
            elif types.fdef._delete_rule == DeleteRule.NULLIFY:
                self._nullify_fields.append(jfield)
            elif types.fdef._delete_rule == DeleteRule.CASCADE:
                self._cascade_fields.append(jfield)
            if types.fdef._requires_operator_assign:
                self._assign_operator_fields.append(jfield)
        self._tuple_fields: tuple[JField] = tuple(self._list_fields)

    def _resolve_ref_if_needed(self: Cdef) -> None:
        if self._ref_resolved is False:
            self._resolve_ref_names()
            self._ref_resolved = True

    def _resolve_ref_names(self: Cdef) -> None:
        for jfield in self._tuple_fields:
            if jfield.types.fdef._field_storage == FieldStorage.LOCAL_KEY:
                key_transformer = self.jconf.key_transformer
                self._reference_names.append(key_transformer(jfield))
                if self.jconf.camelize_json_keys:
                    self._camelized_reference_names.append(
                        camelize(key_transformer(jfield), False))
        self._available_names: set[str] = set(self._field_names
                                              + self._camelized_field_names
                                              + self._reference_names
                                              + self._camelized_reference_names)
        self._update_names: set[str] = set(self._field_names
                                           + self._reference_names)

    @property
    def cls(self: Cdef) -> type:
        """The JSON class on which this class definition is defined.
        """
        return self._cls

    @property
    def name(self: Cdef) -> str:
        """The name of the JSON class on which this class definition is
        defined.
        """
        return self._name

    @property
    def jconf(self: Cdef) -> JConf:
        """The configuration object of the JSON class on which this class
        definition is defined.
        """
        return self._jconf

    def field_named(self: Cdef, name: str) -> JField:
        """
        Get the field which is named `name`.

        Args:
            name (str): The name of the field to return.

        Returns:
            JField: The field named `name`.

        Raises:
            ValueError: If can't find a field with name `name`.
        """
        if not self._dict_fields.get(name):
            raise ValueError(f'no field named {name} in class definition')
        return self._dict_fields[name]

    @property
    def fields(self: Cdef) -> tuple[JField]:
        """Get the fields of this class definition as a tuple. This is useful
        for looping and iterating.
        """
        return self._tuple_fields

    @property
    def created_at_field(self: Cdef) -> Optional[JField]:
        """
        The class definition's field which represents the created at field.

        This is used by the framework to locate the correct field to find the
        record's created at timestamp.
        """
        return self._created_at_field

    @property
    def updated_at_field(self: Cdef) -> Optional[JField]:
        """The class definition's field which represents the updated at field.

        This is used by the framework to locate the correct field to find the
        record's updated at timestamp.
        """
        return self._updated_at_field

    @property
    def deleted_at_field(self: Cdef) -> Optional[JField]:
        """The class definition's field which represents the deleted at field.

        This is used by the framework to locate the correct field to find the
        record's deleted at timestamp.
        """
        return self._deleted_at_field

    @property
    def deny_fields(self: Cdef) -> list[JField]:
        """Reference fields with deny delete rule.
        """
        return self._deny_fields

    @property
    def nullify_fields(self: Cdef) -> list[JField]:
        """Reference fields with nullify delete rule.
        """
        return self._nullify_fields

    @property
    def cascade_fields(self: Cdef) -> list[JField]:
        """Reference fields with cascade delete rule.
        """
        return self._cascade_fields

    @property
    def primary_field(self: Cdef) -> Optional[JField]:
        """The class definition's primary field. This can be None if it's not
        defined by user.
        """
        return self._primary_field

    @property
    def assign_operator_fields(self: Cdef) -> list[JField]:
        """The class definition's fields which require operator assigning on
        object creation.
        """
        return self._assign_operator_fields

    def rfield(
            self: Cdef, fcls: type[JObject], fname: Optional[str],
            fkey: Optional[str]) -> Optional[JField]:
        for field in self._tuple_fields:
            if field.foreign_class is fcls:
                if fname is not None:
                    if field.name == fname:
                        return field
                elif fkey is not None:
                    if field.fdef.foreign_key == fkey:
                        return field
        else:
            return None

    @property
    def available_names(self: Cdef) -> set[str]:
        self._resolve_ref_if_needed()
        return self._available_names

    @property
    def update_names(self: Cdef) -> set[str]:
        self._resolve_ref_if_needed()
        return self._update_names

        # accepted: list[tuple[FieldStorage, bool]] = []
        # if fdef.field_storage == FieldStorage.LOCAL_KEY:
        #     foreign_storage = FieldStorage.FOREIGN_KEY
        #     use_join_table = False
        #     accepted.append((foreign_storage, use_join_table))
        # elif fdef.field_storage == FieldStorage.FOREIGN_KEY:
        #     foreign_storage = FieldStorage.LOCAL_KEY
        #     use_join_table = False
        #     accepted.append((foreign_storage, use_join_table))
        #     if fdef.field_type == FieldType.LIST:
        #         foreign_storage = FieldStorage.FOREIGN_KEY
        #         use_join_table = True
        #         accepted.append((foreign_storage, use_join_table))
        #     elif fdef.field_type == FieldType.INSTANCE:
        #         pass
        # for field in foreign_cdef.fields:
        #     for (storage, use_join) in accepted:
        #         if storage == FieldStorage.LOCAL_KEY:
        #             if fdef.foreign_key == field.name:
        #                 local_matches = self._def_clsmatch(
        #                     local_field.fdef, foreign_class)
        #                 foreign_matches = self._def_class_match(
        #                     field.fdef, self.cls)
        #                 if local_matches and foreign_matches:
        #                     foreign_tuple = (foreign_cdef, field.name)
        #                     self._foreign_fields[name] = foreign_tuple
        #                     local_tuple = (self, name)
        #                     foreign_cdef._foreign_fields[field.name] = \
        #                         local_tuple
        #                     return self._foreign_fields[name]
        #                 else:
        #                     raise LinkedFieldUnmatchException(
        #                         self.cls.__name__, local_field.name,
        #                         foreign_class.__name__, field.name)
        #         elif storage == FieldStorage.FOREIGN_KEY:
        #             if local_field.name == field.fdef.foreign_key:
        #                 if use_join == field.fdef.use_join_table:
        #                     local_matches = self._def_class_match(
        #                         local_field.fdef, foreign_class)
        #                     foreign_matches = self._def_class_match(
        #                         field.fdef, self.cls)
        #                     if local_matches and foreign_matches:
        #                         foreign_tuple = \
        #                             (foreign_cdef, field.name)
        #                         self._foreign_fields[name] = foreign_tuple
        #                         local_tuple = (self, name)
        #                         foreign_cdef._foreign_fields[field.name]\
        #                             = local_tuple
        #                         return self._foreign_fields[name]
        #                     else:
        #                         raise LinkedFieldUnmatchException(
        #                             self.cls.__name__, local_field.name,
        #                             foreign_class.__name__, field.name)
        #                 else:
        #                     raise LinkedFieldUnmatchException(
        #                         self.cls.__name__, local_field.name,
        #                         foreign_class.__name__, field.name)
        # self._foreign_fields[name] = None
        # return None
