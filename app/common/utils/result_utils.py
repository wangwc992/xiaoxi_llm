import http


class ResultUtils:
    @staticmethod
    def success(data=None, message=None):
        return {
            "code": http.HTTPStatus.OK,
            "data": data,
            "message": message
        }

    @staticmethod
    def error(message=None):
        return {
            "status": http.HTTPStatus.INTERNAL_SERVER_ERROR,
            "message": message
        }