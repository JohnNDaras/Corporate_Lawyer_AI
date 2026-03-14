import glob
import os
from src.core.rag import RAGConfig, FAISSRetriever
from src.core.types import Passage
from src.core.text import normalize_text


def main():
    cfg = RAGConfig()
    retriever = FAISSRetriever(cfg)

    passages = []

    for path in glob.glob("data/corpus_raw/*.txt"):
        filename = os.path.basename(path).replace(".txt", "")
        parts = filename.split("__")
        if len(parts) < 3:
            continue

        clause_type, title, source_id = parts[0], parts[1], parts[2]

        with open(path, "r", encoding="utf-8") as f:
            text = normalize_text(f.read())

        passages.append(
            Passage(
                source_id=source_id,
                title=title,
                clause_type=clause_type,
                text=text,
            )
        )

    retriever.build_index(passages)


if __name__ == "__main__":
    main()
