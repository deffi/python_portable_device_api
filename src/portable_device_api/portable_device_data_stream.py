import ctypes

from portable_device_api._util import ComWrapper


class PortableDeviceDataStream(ComWrapper):
    """
    Ensure that the stream is finalized before the program ends (del it if
    necessary), or the file might remain locked.
    # TODO that relies on the instance being collected immediately

    When you are aborting reading a stream, call stream.cancel()
    https://stackoverflow.com/questions/13503436/wpd-mtp-data-stream-hanging-on-release
    """
    def remote_read(self, chunk_size: int) -> bytes:
        # noinspection PyTypeChecker,PyCallingNonCallable
        buffer = (ctypes.c_ubyte * chunk_size)()
        # Patched, see portable_device_api._api.portable_device_api
        # Note that print(self.p) gives POINTER(IPortableDeviceDataStream) (or
        # POINTER(IStream) if we don't QueryInterface it), but it does seem to
        # be using ISequentialStream - if
        # _1F001332_1A57_4934_BE31_AFFC99F4EE0A_0_1_0.ISequentialStream is
        # modified, then this fails.
        # [out] POINTER(c_ubyte) pv
        # [out] POINTER(c_ulong) pcbRead
        _, length = self.p.RemoteRead(
            pv = buffer,                      # [out] POINTER(c_ubyte) pv
            cb = ctypes.c_ulong(chunk_size))  # [in] c_ulong cb

        return bytes(buffer[0:length])

    def remote_write(self, chunk: bytes) -> int:
        string_buffer = ctypes.create_string_buffer(bytes(chunk))
        # [out] POINTER(c_ulong) pcbWritten
        return self.p.RemoteWrite(
            pv = ctypes.cast(string_buffer, ctypes.POINTER(ctypes.c_ubyte)),  # [in] POINTER(c_ubyte) pv
            cb = len(chunk))                                                  # [in] c_ulong cb

    def commit(self) -> None:
        self.p.Commit(grfCommitFlags = 0)  # [in] c_ulong grfCommitFlags

    def get_object_id(self) -> str:
        return self.p.GetObjectID()  # [in, out] POINTER(WSTRING) ppszObjectID

    def cancel(self) -> None:
        self.p.Cancel()
