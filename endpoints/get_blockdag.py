# encoding: utf-8

from server import vecnod_client


async def get_blockdag():
    """
    Get some global Vecno BlockDAG information
    """
    resp = await vecnod_client.request("getBlockDagInfoRequest")
    return resp["getBlockDagInfoResponse"]
