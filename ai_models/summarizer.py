
from __future__ import annotations

from typing import Dict
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

_TOKENIZER: AutoTokenizer | None = None
_MODEL: AutoModelForSeq2SeqLM | None = None


def _get_model_and_tokenizer() -> tuple[AutoTokenizer, AutoModelForSeq2SeqLM]:
    """
    Lazily load and cache the tokenizer/model pair.

    We intentionally avoid `transformers.pipeline(...)` because your installed
    Transformers build does not expose the classic tasks like
    'summarization' / 'text2text-generation'. Direct model usage is stable.
    """
    global _TOKENIZER, _MODEL

    if _TOKENIZER is None or _MODEL is None:
        model_name = "facebook/bart-large-cnn"
        _TOKENIZER = AutoTokenizer.from_pretrained(model_name)
        _MODEL = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        _MODEL.eval()

    return _TOKENIZER, _MODEL


def _generate_summary(text: str, max_new_tokens: int, min_new_tokens: int) -> str:
    """
    Generate a single free-form summary string using BART.
    """
    tokenizer, model = _get_model_and_tokenizer()

    # BART-large-cnn is typically trained with <=1024 tokens input.
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=1024,
    )

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            do_sample=False,
            max_new_tokens=max_new_tokens,
            min_new_tokens=min_new_tokens,
            num_beams=4,
        )

    return tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()


def summarize_text(
    text: str,
    max_length: int = 256,
    min_length: int = 64
) -> Dict[str, str]:
    """
    Generate a structured research paper summary.

    The model generates a general summary which is then divided into:
    - Problem
    - Methodology
    - Results
    - Conclusion
    """

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text for summarization must be a non-empty string.")

    try:
        summary_text = _generate_summary(
            text=text[:3000],
            max_new_tokens=max_length,
            min_new_tokens=min_length,
        )

    except Exception as exc:
        raise RuntimeError(
            "Failed to generate summary with the transformer model."
        ) from exc

    if not summary_text:
        raise RuntimeError("Model did not return a summary.")

    # Split summary into sentences
    sentences = [
        s.strip() for s in summary_text.replace("\n", " ").split(".") if s.strip()
    ]

    # Ensure minimum number of segments
    while len(sentences) < 4:
        sentences.append("")

    quarter = max(1, len(sentences) // 4)

    problem_sentences = sentences[0:quarter]
    methodology_sentences = sentences[quarter:2 * quarter]
    results_sentences = sentences[2 * quarter:3 * quarter]
    conclusion_sentences = sentences[3 * quarter:]

    structured_summary: Dict[str, str] = {
        "problem": ". ".join(problem_sentences).strip(),
        "methodology": ". ".join(methodology_sentences).strip(),
        "results": ". ".join(results_sentences).strip(),
        "conclusion": ". ".join(conclusion_sentences).strip(),
    }

    # Add final punctuation
    for key, value in structured_summary.items():
        if value and not value.endswith("."):
            structured_summary[key] += "."

    return structured_summary

