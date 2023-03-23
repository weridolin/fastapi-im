from json import JSONDecoder,JSONEncoder
from typing import Any
from datetime import datetime

class JsonEncoderWithTime(JSONEncoder):

    def default(self, o: Any) -> Any:
        if isinstance(o,datetime):
            return datetime.strftime(o,'%Y-%m-%D, %H:%M:%S')
        return super().default(o)