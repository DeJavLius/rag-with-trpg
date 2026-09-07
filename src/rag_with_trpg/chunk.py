# chunk_fixed
# ┌──────────────┬────────────────────────────────────────────────┐
# │     계약      │                       내용                      │
# ├──────────────┼────────────────────────────────────────────────┤
# │ 커버리지       │ overlap=0 일 때 "".join(chunks) == text         │
# ├──────────────┼────────────────────────────────────────────────┤
# │ 최대 길이      │ 모든 청크가 len(c) <= size                        │
# ├──────────────┼────────────────────────────────────────────────┤
# │ 겹침          │ chunks[i][-overlap:] == chunks[i+1][:overlap]  │
# ├──────────────┼────────────────────────────────────────────────┤
# │ 빈 청크 없음    │ all(len(c) > 0 for c in chunks) — 빈 입력 포함   │
# ├──────────────┼────────────────────────────────────────────────┤
# │ 입력 가드      │ overlap >= size 면 ValueError                   │
# └──────────────┴────────────────────────────────────────────────┘
def chunk_fixed(text: str, size: int, overlap: int = 0) -> list[str]:
    if overlap >= size:
        raise ValueError("Overlap must be less than size")

    chunk_size: int = size - overlap
    text_length: int = len(text)
    result: list[str] = []
    times: int = text_length // chunk_size + 1
    i, j, c = 0, 0, 0

    while j < times:
        c = min(i + size, text_length)
        sentence = text[i:c]

        if len(sentence) > 0:
            result.append(sentence)

        i = i + chunk_size
        j += 1

    return result
