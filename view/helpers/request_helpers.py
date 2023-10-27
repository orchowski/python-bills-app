from typing import TypeVar, Type, Optional, Dict, Sequence, Union

import humps
from flask import Response, make_response, jsonify
from pydantic import BaseModel, ValidationError
from pydantic.error_wrappers import ErrorWrapper

T = TypeVar('T', bound='BaseModel')


def parse_request_body(model: Type[T], request) -> Optional[T]:
    if json := request.get_json():
        return model(**humps.decamelize(json))
    raise ValidationError([ErrorWrapper(ValueError("request body is not set"), "request_body")], model)


def create_response(response_dict: Union[Dict, Sequence[Dict]], status = 200) -> Response:
    return make_response(jsonify(humps.camelize(response_dict)), status)


