# encoding: utf-8

from server import vecnod_client


async def get_network():
    """
    Get some global vecno network information
    """
    resp = await vecnod_client.request("getBlockDagInfoRequest")
    return resp["getBlockDagInfoResponse"]
