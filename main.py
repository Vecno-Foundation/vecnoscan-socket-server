# encoding: utf-8
import asyncio
import os
from asyncio import Task, InvalidStateError

from fastapi_utils.tasks import repeat_every
from starlette.responses import RedirectResponse

import sockets
from server import app, vecnod_client
from sockets import blocks
from sockets.blockdag import periodical_blockdag
from sockets.bluescore import periodical_blue_score
from sockets.coinsupply import periodic_coin_supply

print(
    f"Loaded: {sockets.join_room}"
    f"{periodic_coin_supply} {periodical_blockdag} {periodical_blue_score}")

BLOCKS_TASK = None  # type: Task


@app.on_event("startup")
async def startup():
    global BLOCKS_TASK
    # find vecnod before staring webserver
    await vecnod_client.initialize_all()
    BLOCKS_TASK = asyncio.create_task(blocks.config())


@app.on_event("startup")
@repeat_every(seconds=5)
async def watchdog():
    global BLOCKS_TASK

    try:
        exception = BLOCKS_TASK.exception()
    except InvalidStateError:
        pass
    else:
        print(f"Watch found an error! {exception}\n"
              f"Reinitialize vecnods and start task again")
        await vecnod_client.initialize_all()
        BLOCKS_TASK = asyncio.create_task(blocks.config())


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url='/docs')


if __name__ == '__main__':
    if os.getenv("DEBUG"):
        import uvicorn

        uvicorn.run(app)
