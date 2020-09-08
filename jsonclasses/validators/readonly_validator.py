from typing import Any
from ..field import Field, WriteRule
from ..config import Config
from ..exceptions import ValidationException
from .validator import Validator

class ReadonlyValidator(Validator):

  def define(self, field: Field):
    field.write_rule = WriteRule.NO_WRITE

  def validate(self, value: Any, key_path: str, root: Any, all_fields: bool, config: Config):
    pass
