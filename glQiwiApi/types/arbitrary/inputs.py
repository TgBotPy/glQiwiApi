from __future__ import annotations

import abc
import io
import os
import pathlib
from types import TracebackType
from typing import Generic, BinaryIO, Type, TypeVar, Any, Optional

InputType = TypeVar("InputType")

try:
    from typing import get_args
except ImportError:
    from typing_extensions import get_args

__all__ = ('AbstractInput', 'PlainPathInput', 'PathlibPathInput', 'BinaryIOInput')


class AbstractInput(abc.ABC, Generic[InputType]):
    def __init__(self, input_: InputType) -> None:
        self._input = input_
        self._file_descriptor: Optional[BinaryIO] = None

    @abc.abstractmethod
    def get_file(self) -> BinaryIO:
        ...

    def get_path(self) -> str:
        raise TypeError(
            f"{self.__class__.__qualname__} doesn't provide a mechanism to get path to file"
        )

    def get_filename(self) -> str:
        raise TypeError(
            f"{self.__class__.__qualname__} doesn't provide a mechanism to get filename"
        )

    def close(self) -> None:
        if self._file_descriptor is None:
            return None
        self._file_descriptor.close()

    def __enter__(self) -> AbstractInput[Any]:
        self._file_descriptor = self.get_file()
        return self

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType],
    ) -> None:
        self.close()


class PlainPathInput(AbstractInput[str]):
    def get_file(self) -> BinaryIO:
        if pathlib.Path(self._input).is_file() is False:
            raise TypeError(f"Input {self._input} is not a file!")
        descriptor = open(self._input, "rb")
        self._file_descriptor = descriptor
        return descriptor

    def get_path(self) -> str:
        return self._input

    def get_filename(self) -> str:
        return os.path.split(self._input)[-1]


class PathlibPathInput(AbstractInput[pathlib.Path]):
    def get_file(self) -> BinaryIO:
        descriptor = open(self._input, "rb")
        self._file_descriptor = descriptor
        return descriptor

    def get_path(self) -> str:
        return str(self._input.resolve())

    def get_filename(self) -> str:
        return self._input.name


class BinaryIOInput(AbstractInput[BinaryIO]):
    def get_file(self) -> BinaryIO:
        return self._input

    @classmethod
    def from_bytes(cls: Type[BinaryIOInput], b: bytes) -> BinaryIOInput:
        return cls(input_=io.BytesIO(b))


def get_autodetected_input(input_: Any) -> AbstractInput[Any]:
    input_subclasses = AbstractInput.__subclasses__()
    for subclass in input_subclasses:
        if isinstance(input_, get_args(subclass.__orig_bases__[0])):  # type: ignore
            return subclass(input_)  # type: ignore

    raise
