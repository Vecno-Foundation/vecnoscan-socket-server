# encoding: utf-8
import asyncio
from queue import Queue

import grpc
from google.protobuf import json_format
from grpc._channel import _MultiThreadedRendezvous

from . import messages_pb2_grpc
from .messages_pb2 import VecnodMessage


MAX_MESSAGE_LENGTH = 1024 * 1024 * 1024  # 1GB


class VecnodCommunicationError(Exception): pass


# pipenv run python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/rpc.proto ./protos/messages.proto ./protos/p2p.proto

class VecnodThread(object):
    def __init__(self, vecno_host, vecno_port, async_thread=True):

        self.vecno_host = vecno_host
        self.vecno_port = vecno_port

        if async_thread:
            self.channel = grpc.aio.insecure_channel(f'{vecno_host}:{vecno_port}',
                                                     compression=grpc.Compression.Gzip,
                                                     options=[
                                                         ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
                                                         ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
                                                     ])
        else:
            self.channel = grpc.insecure_channel(f'{vecno_host}:{vecno_port}',
                                                 compression=grpc.Compression.Gzip,
                                                 options=[
                                                     ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
                                                     ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
                                                 ])
            self.__sync_queue = Queue()
        self.stub = messages_pb2_grpc.RPCStub(self.channel)

        self.__queue = asyncio.queues.Queue()

        self.__closing = False

    def __enter__(self, *args):
        return self

    def __exit__(self, *args):
        self.__closing = True

    async def request(self, command, params=None, wait_for_response=True, timeout=120):
        if wait_for_response:
            try:
                async for resp in self.stub.MessageStream(self.yield_cmd(command, params), timeout=120):
                    self.__queue.put_nowait("done")
                    return json_format.MessageToDict(resp)
            except grpc.aio._call.AioRpcError as e:
                raise VecnodCommunicationError(str(e))

    async def notify(self, command, params=None, callback_func=None):
        try:
            async for resp in self.stub.MessageStream(self.yield_cmd(command, params)):
                # self.__queue.put_nowait("done")
                if callback_func:
                    await callback_func(json_format.MessageToDict(resp))

            print("loop done...")

        except (grpc.aio._call.AioRpcError, _MultiThreadedRendezvous) as e:
            raise VecnodCommunicationError(str(e))

    async def yield_cmd(self, cmd, params=None):
        msg = VecnodMessage()
        msg2 = getattr(msg, cmd)
        payload = params

        if payload:
            if isinstance(payload, dict):
                json_format.ParseDict(payload, msg2)
            if isinstance(payload, str):
                json_format.Parse(payload, msg2)

        msg2.SetInParent()
        yield msg
        await self.__queue.get()

    def yield_cmd_sync(self, cmd, params=None):
        msg = VecnodMessage()
        msg2 = getattr(msg, cmd)
        payload = params

        if payload:
            if isinstance(payload, dict):
                json_format.ParseDict(payload, msg2)
            if isinstance(payload, str):
                json_format.Parse(payload, msg2)

        msg2.SetInParent()
        yield msg
        self.__sync_queue.get()
