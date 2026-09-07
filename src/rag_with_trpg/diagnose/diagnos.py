import json
import statistics
from dataclasses import asdict, dataclass, field
from pathlib import Path

from transformers import AutoTokenizer, SentencePieceBackend, TokenizersBackend

from rag_with_trpg.crawl.index_mapped import PageEntry
from rag_with_trpg.diagnose.config import DiagnoseConfig


@dataclass(kw_only=True)
class DiagnoseMeta:
    title: str
    chars: int
    headings: list[int]
    tokens: int = 0
    chars_per_token: float = 0.0
    unk_tokens: dict[str, int] | None = None


@dataclass(kw_only=True)
class DiagnoseResult:
    max_sequence_length: int = 0
    count: int = 0
    average_cpt: float = 0.0
    max_cpt: float = 0.0
    min_cpt: float = 0.0
    lower_ten_percent_cpt: float = 0.0
    upper_ten_percent_cpt: float = 0.0
    safe_chars: float = 0.0
    cpt_ranking_by_worst: list[str] = field(default_factory=list)

    def print_result(self) -> None:
        print(
            f"결과 출력: 총 {self.count} 페이지\n"
            + f"페이지별 자/토큰(page size / token size) 비율 > 평균: {self.average_cpt} | 최소: {self.min_cpt} | 최대: {self.max_cpt}\n"
            + f"상위/하위 10% 비율 > 상위 10%: {self.upper_ten_percent_cpt} | 하위 10%: {self.lower_ten_percent_cpt}\n"
            + f"모델 사이즈({self.max_sequence_length})에 따른 안전 토큰: {self.safe_chars}\n"
            + f"토큰화가 불리한 페이지 순위: \n{"\n".join([f"{i + 1}. {v}" for i, v in enumerate(self.cpt_ranking_by_worst)])}"
        )


def diagnose(config: DiagnoseConfig):
    tokenizer: TokenizersBackend | SentencePieceBackend = AutoTokenizer.from_pretrained(
        config.embed_test_model
    )

    print("[1] diagnose: markdown files & index load")
    index_pages = [
        PageEntry(**j)
        for j in json.loads(config.index_file.read_text(encoding="utf-8"))
    ]
    index_pages = list(filter(lambda x: x.excluded is None, index_pages))

    print("[2] diagnose: start round-trip check")
    meta_list = meta_analyze(config, tokenizer, index_pages)
    config.meta_file.write_text(
        json.dumps([asdict(e) for e in meta_list], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("[3] diagnose: start analys meta result")
    cpt_ratios = [meta.chars_per_token for meta in meta_list]
    result = DiagnoseResult(
        max_sequence_length=config.embed_test_max_seq,
        count=len(meta_list),
        average_cpt=statistics.fmean(cpt_ratios),
        min_cpt=min(cpt_ratios),
        max_cpt=max(cpt_ratios),
        lower_ten_percent_cpt=statistics.quantiles(cpt_ratios, n=10)[0],
        upper_ten_percent_cpt=statistics.quantiles(cpt_ratios, n=10)[-1],
        safe_chars=config.embed_test_max_seq * min(cpt_ratios),
        cpt_ranking_by_worst=[
            ms.title for ms in sorted(meta_list, key=lambda m: m.chars_per_token)
        ],
    )
    config.meta_result_file.write_text(
        json.dumps(asdict(result), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("[4] diagnose: final result")
    result.print_result()


def meta_analyze(
    config: DiagnoseConfig,
    tokenizer: TokenizersBackend | SentencePieceBackend,
    index_pages: list[PageEntry],
) -> list[DiagnoseMeta]:

    meta_list: list[DiagnoseMeta] = []
    for i, index_page in enumerate(index_pages):
        meta = DiagnoseMeta(
            title=index_page.title, chars=index_page.chars, headings=index_page.headings
        )
        markdown_path = Path(config.base_path + index_page.md)
        markdown_file = markdown_path.read_text(encoding="utf-8")

        unk_text_dict: dict[str, int] = {}
        encode_token = tokenizer(
            markdown_file,
            add_special_tokens=False,
            return_offsets_mapping=True,
            verbose=False,
        )
        for index_id, (start, end) in zip(
            encode_token["input_ids"], encode_token["offset_mapping"]
        ):
            if index_id == tokenizer.unk_token_id:
                if unk_text_dict.get(markdown_file[start:end]) is None:
                    unk_text_dict[markdown_file[start:end]] = 1
                else:
                    unk_text_dict[markdown_file[start:end]] += 1

        if len(unk_text_dict.items()) == 0:
            print(f"round-check({i}): {index_page.title} - no unk tokens")
            meta.unk_tokens = None
        else:
            print(
                f"round-check({i}): {index_page.title} - 글자 {", ".join(unk_text_dict.keys())} unk 발견, 총 {sum(map(lambda v: v, unk_text_dict.values()))}개"
            )
            meta.unk_tokens = unk_text_dict

        meta.tokens = len(encode_token.tokens())
        meta.chars_per_token = meta.chars / meta.tokens

        meta_list.append(meta)

    return meta_list
