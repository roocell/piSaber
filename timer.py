import asyncio

################ TIMER CLASS ################
class Timer:
    def __init__(self, timeout, callback, repeat):
        self._timeout = timeout
        self._callback = callback
        self._repeat = repeat
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback(self._repeat, self._timeout)

    def cancel(self):
        self._task.cancel()