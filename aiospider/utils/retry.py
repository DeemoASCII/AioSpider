#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/10 5:43 下午
import asyncio
from functools import wraps

from aiospider.utils.log import get_logger

logger = get_logger(name='Retrying')


def retry(*exceptions, retries=5, sleep=2, verbose=True):
    """Decorate an async function to execute it a few times before giving up.
    Hopes that problem is resolved by another side shortly.

    Args:
        exceptions (Tuple[Exception]) : The exceptions expected during function execution
        retries (int): Number of retries of function execution.
        sleep (int): Seconds to wait before retry.
        verbose (bool): Specifies if we should log about not successful attempts.
    """

    def wrap(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            retries_count = 0
            while True:
                try:
                    result = await func(*args, **kwargs)
                    break
                except exceptions as err:
                    retries_count += 1
                    message = f"Exception during {func} execution. {retries_count} of {retries} retries attempted"
                    if retries_count >= retries:
                        verbose and logger.exception(err)
                        raise err
                    else:
                        verbose and logger.warning(message)

                    if sleep:
                        await asyncio.sleep(sleep)
            return result

        return inner

    return wrap
