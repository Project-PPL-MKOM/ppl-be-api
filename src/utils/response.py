from typing import Any, Union

from flask import jsonify


class ResponseBuilder:
    def __init__(self, success: bool, data: Union[Any, None], error: Union[str, None]) -> None:
        self.__success = success
        self.__data = data
        self.__error = error

    @classmethod
    def success(cls, data: Union[Any, None]):
        return cls(True, data, None)

    @classmethod
    def failed(cls, error: Union[str, None]):
        return cls(False, None, error)

    @property
    def json(self):
        res = {'success': self.__success}
        if self.__data is not None:
            res['data'] = self.__data
        if self.__error is not None:
            res['error'] = self.__error
        return jsonify(res)
