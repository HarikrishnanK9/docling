import json
from io import BytesIO
from pathlib import Path
from typing import Union, List

from docling_core.types.doc import DoclingDocument
from typing_extensions import override

from docling.backend.abstract_backend import DeclarativeDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument


class DoclingJSONLBackend(DeclarativeDocumentBackend):
    @override
    def __init__(
        self, in_doc: InputDocument, path_or_stream: Union[BytesIO, Path]
    ) -> None:
        super().__init__(in_doc, path_or_stream)

        # Parse JSONL and store success/error state
        self._doc_or_err = self._get_doc_or_err()

    @override
    def is_valid(self) -> bool:
        return isinstance(self._doc_or_err, DoclingDocument)

    @classmethod
    @override
    def supports_pagination(cls) -> bool:
        return False

    @classmethod
    @override
    def supported_formats(cls) -> set[InputFormat]:
        return {InputFormat.JSONL_DOCLING}

    def _get_doc_or_err(self) -> Union[DoclingDocument, Exception]:
        """
        Parses JSONL (Newline Delimited JSON) into a DoclingDocument.
        """
        try:
            json_lines: List[dict] = []
            if isinstance(self.path_or_stream, Path):
                with open(self.path_or_stream, encoding="utf-8") as f:
                    json_lines = [json.loads(line) for line in f if line.strip()]
            elif isinstance(self.path_or_stream, BytesIO):
                json_lines = [json.loads(line) for line in self.path_or_stream.getvalue().decode().splitlines() if line.strip()]
            else:
                raise RuntimeError(f"Unexpected: {type(self.path_or_stream)=}")

            # Convert list of JSON objects into a structured DoclingDocument
            return DoclingDocument.model_validate_json(json_data=json.dumps(json_lines))

        except Exception as e:
            return e

    @override
    def convert(self) -> DoclingDocument:
        if isinstance(self._doc_or_err, DoclingDocument):
            return self._doc_or_err
        else:
            raise self._doc_or_err
