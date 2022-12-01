import json
import os
from errors import BaseErrorData, SuccessCode


# 确保一个路径是否存在。如果不存在就创建目录
def ensure_path(path: str) -> str:
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def fail_result(error: BaseErrorData, **kwargs) -> str:
    ret_obj = {
        "code": error.error_code,
        "result": error.error_reason,
    }

    if len(kwargs) > 0:
        ret_obj["data"] = kwargs

    return json.dumps(ret_obj, separators=(',', ':'))


def success_result(**kwargs) -> str:
    return fail_result(SuccessCode, **kwargs)
