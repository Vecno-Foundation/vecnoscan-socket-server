# encoding: utf-8

from vecnod.VecnodThread import VecnodThread


# pipenv run python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/rpc.proto ./protos/messages.proto ./protos/p2p.proto

class VecnodClient(object):
    def __init__(self, vecno_host, vecno_port):
        self.vecno_host = vecno_host
        self.vecno_port = vecno_port
        self.server_version = None
        self.is_utxo_indexed = None
        self.is_synced = None
        self.p2p_id = None

    async def ping(self):
        try:
            info = await self.request("getInfoRequest")
            self.server_version = info["getInfoResponse"]["serverVersion"]
            self.is_utxo_indexed = info["getInfoResponse"]["isUtxoIndexed"]
            self.is_synced = info["getInfoResponse"]["isSynced"]
            self.p2p_id = info["getInfoResponse"]["p2pId"]
            return info

        except Exception as exc:
            return False

    async def request(self, command, params=None, timeout=5):
        with VecnodThread(self.vecno_host, self.vecno_port) as t:
            return await t.request(command, params, wait_for_response=True, timeout=timeout)

    async def notify(self, command, params, callback):
        t = VecnodThread(self.vecno_host, self.vecno_port, async_thread=True)
        return await t.notify(command, params, callback)
