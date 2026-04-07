#!/usr/bin/env python3
"""
Automated test runner for dont-to-do refine.py
Usage: python scripts/test_refine.py
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from refine import scan, backfill, scan_unmatched

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

passed = failed = 0

def run_test(name: str, fn):
    global passed, failed
    try:
        fn()
        print(f"  PASS  {name}")
        passed += 1
    except AssertionError as e:
        print(f"  FAIL  {name}: {e}")
        failed += 1


def assert_span(text, expected_cat, expected_type, needle):
    spans = scan(text)
    matching = [s for s in spans if s.category == expected_cat and s.span_type == expected_type
                and needle.lower() in s.text.lower()]
    assert matching, f"Expected [{expected_cat}/{expected_type}] containing {needle!r}; got {[(s.category, s.span_type, s.text) for s in spans]}"


def assert_no_spans(text):
    spans = scan(text)
    assert not spans, f"Expected no spans in {text!r}; got {[(s.category, s.text) for s in spans]}"


def assert_strength(text, expected_strength):
    spans = scan(text) or scan_unmatched(text, [])
    assert spans, f"Expected spans in {text!r}; got none"
    found = [s for s in spans if s.strength == expected_strength]
    assert found, (
        f"Expected at least one span with strength {expected_strength!r} in {text!r}; "
        f"got {[(s.text, s.strength) for s in spans]}"
    )


def assert_backfill(text, replacements, expected_output):
    result = backfill(text, replacements)
    assert result == expected_output, f"Expected {expected_output!r}; got {result!r}"


# ---------------------------------------------------------------------------
# Section 1 — Category A: Length
# ---------------------------------------------------------------------------
print("\n== Section 1: Category A (Length) ==")

run_test("don't be too short → A/N",
     lambda: assert_span("don't be too short", "A", "N", "don't be too short"))

run_test("不要太短 → A/N",
     lambda: assert_span("不要太短", "A", "N", "不要太短"))

run_test("keep it concise → A/V",
     lambda: assert_span("keep it concise", "A", "V", "concise"))

run_test("尽量简洁 → A/V",
     lambda: assert_span("尽量简洁", "A", "V", "尽量简洁"))

run_test("don't ramble → A/N",
     lambda: assert_span("don't ramble", "A", "N", "ramble"))

run_test("不要废话 → A/N",
     lambda: assert_span("不要废话", "A", "N", "不要废话"))

run_test("appropriate length → A/V",
     lambda: assert_span("appropriate length", "A", "V", "appropriate length"))

run_test("适当长度 → A/V",
     lambda: assert_span("适当长度", "A", "V", "适当长度"))

run_test("don't be too long → A/N",
     lambda: assert_span("don't be too long", "A", "N", "too long"))

run_test("不要太长 → A/N",
     lambda: assert_span("不要太长", "A", "N", "不要太长"))

run_test("不要啰嗦 → A/N",
     lambda: assert_span("不要啰嗦", "A", "N", "不要啰嗦"))

# ---------------------------------------------------------------------------
# Section 2 — Category B: Privacy
# ---------------------------------------------------------------------------
print("\n== Section 2: Category B (Privacy) ==")

run_test("don't leak credentials → B/N",
     lambda: assert_span("don't leak credentials", "B", "N", "credentials"))

run_test("不要泄露用户数据 → B/N",
     lambda: assert_span("不要泄露用户数据", "B", "N", "泄露用户数据"))

run_test("don't include PII → B/N",
     lambda: assert_span("don't include PII", "B", "N", "PII"))

run_test("不要暴露敏感信息 → B/N",
     lambda: assert_span("不要暴露敏感信息", "B", "N", "敏感信息"))

run_test("properly protect user data → B/V",
     lambda: assert_span("properly protect user data", "B", "V", "protect"))

run_test("适当保护数据 → B/V",
     lambda: assert_span("适当保护数据", "B", "V", "适当保护"))

run_test("不要显示密码 → B/N",
     lambda: assert_span("不要显示密码", "B", "N", "密码"))

# ---------------------------------------------------------------------------
# Section 3 — Category C: Tone
# ---------------------------------------------------------------------------
print("\n== Section 3: Category C (Tone) ==")

run_test("don't be too formal → C/N",
     lambda: assert_span("don't be too formal", "C", "N", "formal"))

run_test("don't be too casual → C/N",
     lambda: assert_span("don't be too casual", "C", "N", "casual"))

run_test("avoid sounding too academic → C/N",
     lambda: assert_span("avoid sounding too academic", "C", "N", "academic"))

run_test("不要太学术化 → C/N",
     lambda: assert_span("不要太学术化", "C", "N", "学术"))

run_test("不要太正式 → C/N",
     lambda: assert_span("不要太正式", "C", "N", "正式"))

run_test("不要机翻感 → C/N",
     lambda: assert_span("不要机翻感", "C", "N", "机翻"))

run_test("a bit more formal → C/V",
     lambda: assert_span("a bit more formal", "C", "V", "formal"))

run_test("稍微正式一点 → C/V",
     lambda: assert_span("稍微正式一点", "C", "V", "正式"))

# ---------------------------------------------------------------------------
# Section 4 — Category D: Format
# ---------------------------------------------------------------------------
print("\n== Section 4: Category D (Format) ==")

run_test("don't use bullet points → D/N",
     lambda: assert_span("don't use bullet points", "D", "N", "bullet points"))

run_test("not too many headers → D/N",
     lambda: assert_span("not too many headers please", "D", "N", "headers"))

run_test("don't use Markdown → D/N",
     lambda: assert_span("don't use Markdown", "D", "N", "Markdown"))

run_test("不要用列表 → D/N",
     lambda: assert_span("不要用列表", "D", "N", "列表"))

run_test("不要加太多标题 → D/N",
     lambda: assert_span("不要加太多标题", "D", "N", "标题"))

run_test("不要加emoji → D/N",
     lambda: assert_span("不要加emoji", "D", "N", "emoji"))

run_test("appropriate formatting → D/V",
     lambda: assert_span("appropriate formatting", "D", "V", "formatting"))

run_test("适当排版 → D/V",
     lambda: assert_span("适当排版", "D", "V", "排版"))

# ---------------------------------------------------------------------------
# Section 5 — Category E: Focus
# ---------------------------------------------------------------------------
print("\n== Section 5: Category E (Focus) ==")

run_test("don't repeat → E/N",
     lambda: assert_span("don't repeat", "E", "N", "repeat"))

run_test("不要重复 → E/N",
     lambda: assert_span("不要重复", "E", "N", "重复"))

run_test("don't add your own opinion → E/N",
     lambda: assert_span("don't add your own opinion", "E", "N", "opinion"))

run_test("不要猜测 → E/N",
     lambda: assert_span("不要猜测", "E", "N", "猜测"))

run_test("stay on topic → E/V",
     lambda: assert_span("stay on topic", "E", "V", "topic"))

run_test("尽量客观 → E/V",
     lambda: assert_span("尽量客观", "E", "V", "客观"))

# ---------------------------------------------------------------------------
# Section 6 — Category F: Output meta-structure
# ---------------------------------------------------------------------------
print("\n== Section 6: Category F (Output meta) ==")

run_test("don't start with Sure! → F/N",
     lambda: assert_span("don't start with Sure!", "F", "N", "Sure"))

run_test("don't be sycophantic → F/N",
     lambda: assert_span("don't be sycophantic", "F", "N", "sycophantic"))

run_test("don't explain your reasoning → F/N",
     lambda: assert_span("don't explain your reasoning", "F", "N", "reasoning"))

run_test("不要开头说当然 → F/N",
     lambda: assert_span("不要开头说当然", "F", "N", "当然"))

run_test("不要拍马屁 → F/N",
     lambda: assert_span("不要拍马屁", "F", "N", "拍马屁"))

run_test("不要加总结 → F/N",
     lambda: assert_span("不要加总结", "F", "N", "总结"))

# ---------------------------------------------------------------------------
# Section 7 — Category G: Depth
# ---------------------------------------------------------------------------
print("\n== Section 7: Category G (Depth) ==")

run_test("don't give too many examples → G/N",
     lambda: assert_span("don't give too many examples", "G", "N", "examples"))

run_test("don't assume I'm a beginner → G/N",
     lambda: assert_span("don't assume I'm a beginner", "G", "N", "beginner"))

run_test("不要举太多例子 → G/N",
     lambda: assert_span("不要举太多例子", "G", "N", "例子"))

run_test("不要假设我不懂基础 → G/N",
     lambda: assert_span("不要假设我不懂基础", "G", "N", "不懂基础"))

run_test("keep it simple → G/V",
     lambda: assert_span("keep it simple", "G", "V", "simple"))

run_test("尽量简单 → G/V",
     lambda: assert_span("尽量简单", "G", "V", "简单"))

# ---------------------------------------------------------------------------
# Section 8 — Category H: Code
# ---------------------------------------------------------------------------
print("\n== Section 8: Category H (Code) ==")

run_test("don't over-engineer → H/N",
     lambda: assert_span("don't over-engineer", "H", "N", "engineer"))

run_test("don't add comments → H/N",
     lambda: assert_span("don't add comments", "H", "N", "comments"))

run_test("don't add error handling → H/N",
     lambda: assert_span("don't add error handling", "H", "N", "error handling"))

run_test("don't add type hints → H/N",
     lambda: assert_span("don't add type hints", "H", "N", "type hints"))

run_test("don't change the function signature → H/N",
     lambda: assert_span("don't change the function signature", "H", "N", "signature"))

run_test("don't touch other files → H/N",
     lambda: assert_span("don't touch other files", "H", "N", "files"))

run_test("don't add docstrings → H/N",
     lambda: assert_span("don't add docstrings", "H", "N", "docstrings"))

run_test("don't refactor the existing code → H/N",
     lambda: assert_span("don't refactor the existing code", "H", "N", "refactor"))

run_test("不要过度设计 → H/N",
     lambda: assert_span("不要过度设计", "H", "N", "过度设计"))

run_test("不要加注释 → H/N",
     lambda: assert_span("不要加注释", "H", "N", "注释"))

run_test("不要改函数签名 → H/N",
     lambda: assert_span("不要改函数签名", "H", "N", "签名"))

run_test("不要加错误处理 → H/N",
     lambda: assert_span("不要加错误处理", "H", "N", "错误处理"))

run_test("不要加类型注解 → H/N",
     lambda: assert_span("不要加类型注解", "H", "N", "类型注解"))

run_test("不要改其他文件 → H/N",
     lambda: assert_span("不要改其他文件", "H", "N", "其他文件"))

run_test("不要加docstring → H/N",
     lambda: assert_span("不要加docstring", "H", "N", "docstring"))

run_test("不要重构现有代码 → H/N",
     lambda: assert_span("不要重构现有代码", "H", "N", "重构"))

# ---------------------------------------------------------------------------
# Section 9 — Category I: Image/Video/Audio
# ---------------------------------------------------------------------------
print("\n== Section 9: Category I (Image/Video/Audio) ==")

run_test("don't be photorealistic → I/N",
     lambda: assert_span("don't be photorealistic", "I", "N", "photorealistic"))

run_test("don't make it too dark → I/N",
     lambda: assert_span("don't make it too dark", "I", "N", "dark"))

run_test("don't add watermarks → I/N",
     lambda: assert_span("don't add watermarks", "I", "N", "watermarks"))

run_test("don't generate faces → I/N",
     lambda: assert_span("don't generate faces", "I", "N", "faces"))

run_test("不要太写实 → I/N",
     lambda: assert_span("不要太写实", "I", "N", "写实"))

run_test("不要太暗 → I/N",
     lambda: assert_span("不要太暗", "I", "N", "太暗"))

run_test("不要加水印 → I/N",
     lambda: assert_span("不要加水印", "I", "N", "水印"))

run_test("不要生成人脸 → I/N",
     lambda: assert_span("不要生成人脸", "I", "N", "人脸"))

run_test("maintain style consistency → I/V",
     lambda: assert_span("maintain style consistency", "I", "V", "style"))

run_test("适当亮度 → I/V",
     lambda: assert_span("适当亮度", "I", "V", "亮度"))

run_test("don't be too loud → I/N",
     lambda: assert_span("don't be too loud", "I", "N", "loud"))

run_test("不要太吵 → I/N",
     lambda: assert_span("不要太吵", "I", "N", "太吵"))

# ---------------------------------------------------------------------------
# Section 10 — Category J: Agent
# ---------------------------------------------------------------------------
print("\n== Section 10: Category J (Agent) ==")

run_test("don't execute automatically → J/N",
     lambda: assert_span("don't execute automatically", "J", "N", "automatically"))

run_test("不要自动执行 → J/N",
     lambda: assert_span("不要自动执行", "J", "N", "自动执行"))

run_test("don't call too many tools → J/N",
     lambda: assert_span("don't call too many tools", "J", "N", "tools"))

run_test("不要频繁调用工具 → J/N",
     lambda: assert_span("不要频繁调用工具", "J", "N", "工具"))

run_test("don't touch production → J/N",
     lambda: assert_span("don't touch production", "J", "N", "production"))

run_test("不要碰生产环境 → J/N",
     lambda: assert_span("不要碰生产环境", "J", "N", "生产"))

run_test("don't delete data → J/N",
     lambda: assert_span("don't delete data", "J", "N", "data"))

run_test("don't access the internet → J/N",
     lambda: assert_span("don't access the internet", "J", "N", "internet"))

run_test("don't loop forever → J/N",
     lambda: assert_span("don't loop forever", "J", "N", "forever"))

run_test("不要死循环 → J/N",
     lambda: assert_span("不要死循环", "J", "N", "死循环"))

# ---------------------------------------------------------------------------
# Section 11 — Category K: Faithfulness
# ---------------------------------------------------------------------------
print("\n== Section 11: Category K (Faithfulness) ==")

run_test("don't hallucinate → K/N",
     lambda: assert_span("don't hallucinate", "K", "N", "hallucinate"))

run_test("不要幻觉 → K/N",
     lambda: assert_span("不要幻觉", "K", "N", "幻觉"))

run_test("don't make up facts → K/N",
     lambda: assert_span("don't make up facts", "K", "N", "facts"))

run_test("不要编造 → K/N",
     lambda: assert_span("不要编造", "K", "N", "编造"))

run_test("don't make up numbers → K/N",
     lambda: assert_span("don't make up numbers", "K", "N", "numbers"))

run_test("don't cite sources you haven't read → K/N",
     lambda: assert_span("don't cite sources you haven't read", "K", "N", "sources"))

run_test("不要伪造引用 → K/N",
     lambda: assert_span("不要伪造引用", "K", "N", "伪造引用"))

run_test("不要编造数字 → K/N",
     lambda: assert_span("不要编造数字", "K", "N", "编造数字"))

run_test("don't go beyond the context → K/N",
     lambda: assert_span("don't go beyond the context", "K", "N", "context"))

run_test("不要超出上下文范围 → K/N",
     lambda: assert_span("不要超出上下文范围", "K", "N", "上下文"))

run_test("don't change the original text → K/N",
     lambda: assert_span("don't change the original text", "K", "N", "text"))

run_test("不要改动原文 → K/N",
     lambda: assert_span("不要改动原文", "K", "N", "原文"))

# ---------------------------------------------------------------------------
# Section 12 — Category L: Ethics/Bias
# ---------------------------------------------------------------------------
print("\n== Section 12: Category L (Ethics/Bias) ==")

run_test("don't be biased → L/N",
     lambda: assert_span("don't be biased", "L", "N", "biased"))

run_test("不要有偏见 → L/N",
     lambda: assert_span("不要有偏见", "L", "N", "偏见"))

run_test("don't discriminate → L/N",
     lambda: assert_span("don't discriminate", "L", "N", "discriminate"))

run_test("不要歧视 → L/N",
     lambda: assert_span("不要歧视", "L", "N", "歧视"))

run_test("don't add political bias → L/N",
     lambda: assert_span("don't add political bias", "L", "N", "political"))

run_test("不要带政治立场 → L/N",
     lambda: assert_span("不要带政治立场", "L", "N", "政治"))

run_test("be fair and balanced → L/V",
     lambda: assert_span("be fair and balanced", "L", "V", "fair"))

run_test("保持公正 → L/V",
     lambda: assert_span("保持公正", "L", "V", "公正"))

# ---------------------------------------------------------------------------
# Section 13 — Backfill tests
# ---------------------------------------------------------------------------
print("\n== Section 13: Backfill ==")

run_test("backfill: single replacement",
     lambda: assert_backfill(
         "Write an article. don't be too short.",
         [{"start": 18, "end": 36, "directive": ">=500 words"}],
         "Write an article. >=500 words."
     ))

run_test("backfill: multiple replacements",
     lambda: assert_backfill(
         "don't be too short, don't add emojis.",
         [
             {"start": 0,  "end": 18, "directive": ">=100 words"},
             {"start": 20, "end": 36, "directive": "plain text only"},
         ],
         ">=100 words, plain text only."
     ))

run_test("backfill: no replacements returns original",
     lambda: assert_backfill(
         "Write me an article.",
         [],
         "Write me an article."
     ))

run_test("backfill: replacements with empty directive are skipped",
     lambda: assert_backfill(
         "don't be too short.",
         [{"start": 0, "end": 18, "directive": ""}],
         "don't be too short."
     ))

run_test("backfill: replacement without directive key is skipped",
     lambda: assert_backfill(
         "don't be too short.",
         [{"start": 0, "end": 18}],
         "don't be too short."
     ))

run_test("backfill: start > end is skipped (no corruption)",
     lambda: assert_backfill(
         "hello world",
         [{"start": 8, "end": 5, "directive": "test"}],
         "hello world"
     ))

run_test("backfill: negative start is skipped",
     lambda: assert_backfill(
         "hello world",
         [{"start": -1, "end": 5, "directive": "test"}],
         "hello world"
     ))

# ---------------------------------------------------------------------------
# Section 14 — Edge Cases
# ---------------------------------------------------------------------------
print("\n== Section 14: Edge Cases ==")

run_test("9.1 no constraints → no spans",
     lambda: assert_no_spans("Please summarize the document in three bullet points."))

run_test("9.2 already positive → no spans",
     lambda: assert_no_spans("Write >=500 words, use ## headers, cite all sources."))

run_test("9.3 negation in factual clause → no span",
     lambda: assert_no_spans("Explain why Python doesn't have static typing by default."))


def _overlapping_spans():
    """9.4: 'don't add inline comments or docstrings' should produce 1 span, not 2."""
    text = "don't add inline comments or docstrings"
    spans = scan(text)
    assert len(spans) == 1, (
        f"Expected 1 span for overlapping 'comments or docstrings'; got {len(spans)}: "
        f"{[(s.category, s.text) for s in spans]}"
    )

run_test("9.4 overlapping spans: longest match wins (1 span, not 2)", _overlapping_spans)


def _mixed_language():
    text = "帮我写代码，don't add comments, 不要改函数签名, keep it concise"
    spans = scan(text)
    assert len(spans) >= 3, f"Expected >=3 spans, got {len(spans)}: {[(s.category, s.text) for s in spans]}"
    cats = [s.category for s in spans]
    assert "H" in cats, f"Expected H category spans; got {cats}"

run_test("9.5 mixed EN/ZH in single prompt: >=3 spans", _mixed_language)

# ---------------------------------------------------------------------------
# Section 15 — Negation strength
# ---------------------------------------------------------------------------
print("\n== Section 15: Negation Strength ==")

run_test("MUST_NOT for 'never add comments'",
     lambda: assert_strength("never add comments", "MUST_NOT"))

run_test("MUST_NOT for '禁止访问生产环境'",
     lambda: assert_strength("禁止访问生产环境", "MUST_NOT"))

run_test("SHOULD_NOT for 'don't add comments'",
     lambda: assert_strength("don't add comments", "SHOULD_NOT"))

run_test("SHOULD_NOT for '不要加注释'",
     lambda: assert_strength("不要加注释", "SHOULD_NOT"))

run_test("PREFER_NOT for 'try not to add comments'",
     lambda: assert_strength("try not to add comments", "PREFER_NOT"))

run_test("PREFER_NOT for '尽量不要使用框架' (fallback pattern)",
     lambda: assert_strength("尽量不要使用框架", "PREFER_NOT"))

run_test("PREFER_NOT for '尽量不要太长' (prefix + pattern-library match)",
     lambda: assert_strength("尽量不要太长", "PREFER_NOT"))

run_test("MUST_NOT for 'never be too formal' (prefix + pattern-library match)",
     lambda: assert_strength("never be too formal", "MUST_NOT"))

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print(f"\n{'='*50}")
print(f"Results: {passed} passed, {failed} failed  ({passed + failed} total)")
if failed:
    sys.exit(1)
