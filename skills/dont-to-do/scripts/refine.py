#!/usr/bin/env python3
"""
dont-to-do  --  Prompt Constraint Compiler
===========================================
Three-phase pipeline (inspired by VCC compiler architecture):

  Phase 1  SCAN      Locate all constraint spans (negative + vague) via regex
  Phase 2  TRANSFORM LLM generates a precise positive directive for each span
  Phase 3  BACKFILL  Substitute transformed spans at exact offsets; preserve all other characters

Usage
-----
  python refine.py "your prompt here"          # default: --scan-json
  echo "your prompt" | python refine.py        # default: --scan-json
  python refine.py --scan-only "your prompt"   # human-readable scan output
  python refine.py --scan-json "your prompt"   # JSON scan output (default)
  python refine.py --list                      # list all patterns
  echo '{"text":"...","replacements":[...]}' | python refine.py --backfill
"""

from __future__ import annotations
import re, sys, json, argparse
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Negation intensity detection
# ---------------------------------------------------------------------------

_STRENGTH_HARD = re.compile(
    r"^(?:never\b|禁止|绝不|绝对不(?:要|能|得)?)",
    re.IGNORECASE | re.UNICODE,
)
_STRENGTH_SOFT = re.compile(
    r"^(?:try\s+(?:not\s+)?to\s+avoid|try\s+not\s+to|prefer\s+not\s+to"
    r"|avoid\s+if\s+(?:you\s+)?(?:can|possible)|if\s+possible[,\s]+avoid"
    r"|refrain\s+from|尽量不要|如[果可]能(?:的话)?不要)",
    re.IGNORECASE | re.UNICODE,
)

def _detect_strength(matched_text: str) -> str:
    """Return MUST_NOT for 'never/禁止', PREFER_NOT for 'try not to/尽量不要', else SHOULD_NOT."""
    if _STRENGTH_HARD.match(matched_text):
        return "MUST_NOT"
    if _STRENGTH_SOFT.match(matched_text):
        return "PREFER_NOT"
    return "SHOULD_NOT"


@dataclass
class Span:
    start: int; end: int; text: str
    span_type: str; category: str; description: str
    strength: str = "SHOULD_NOT"


# ---------------------------------------------------------------------------
# Pattern library  (regex, span_type, category, description)
# span_type: N=negative  V=vague
# strength:  MUST_NOT (never/禁止)  SHOULD_NOT (default)  PREFER_NOT (try not to/尽量不要)
# category:  A=length B=privacy C=tone D=format E=focus F=output-meta G=depth H=code
#            I=image/video/audio J=agent K=faithfulness L=ethics/bias
# ---------------------------------------------------------------------------
_RAW = [

    # A: Length
    (r"don'?t (?:(?:make|be) (?:it |this |the \w+ )?)?too (?:brief|short)",
     "N","A","don't be too brief -> word-count floor"),
    (r"don'?t (?:make it |be )?too long",
     "N","A","don't be too long -> word-count ceiling"),
    (r"don'?t (?:pad|ramble|repeat yourself)",
     "N","A","don't pad -> information-density rule"),
    (r"don'?t (?:add|use|include) (?:any )?filler|no filler",
     "N","A","no filler -> information-density rule"),
    (r"不要?太短|别太短|不能太短",
     "N","A","不要太短 -> word-count floor"),
    (r"不要?太长|别太长|不能太长",
     "N","A","不要太长 -> word-count ceiling"),
    (r"不要?废话|别废话",
     "N","A","不要废话 -> information-density rule"),
    (r"不要?太?(?:啰嗦|冗长)|别太?(?:啰嗦|冗长)",
     "N","A","不要啰嗦 -> conciseness rule"),
    (r"(?:keep it |be |stay )(?:relatively |fairly )?concise",
     "V","A","be concise -> target length band"),
    (r"(?:appropriate|reasonable|suitable) (?:length|length of)",
     "V","A","appropriate length -> concrete length range"),
    (r"尽量简洁|适当简洁",
     "V","A","尽量简洁 -> target length band"),
    (r"适当长度|合适的长度",
     "V","A","适当长度 -> concrete length range"),

    # B: Privacy
    (r"don'?t (?:leak|expose|log|print|show) (?:any )?(?:credentials?|secrets?|passwords?|tokens?|api[_ ]?keys?)",
     "N","B","don't leak credentials -> redaction rule"),
    (r"don'?t (?:include|store|log|expose) (?:any )?(?:personal|private|sensitive|pii)(?: (?:data|info(?:rmation)?))?",
     "N","B","don't include PII -> anonymisation rule"),
    (r"don'?t (?:leak|expose|reveal|show) (?:any )?(?:user )?data",
     "N","B","don't leak user data -> data-masking rule"),
    (r"不要?泄[露漏]用户数据|别泄[露漏]用户数据",
     "N","B","不要泄露用户数据 -> data-masking rule"),
    (r"不要?泄[露漏](?:个人)?隐私|别泄[露漏](?:个人)?隐私",
     "N","B","不要泄露隐私 -> PII-masking rule"),
    (r"不要?暴露敏感信息|别暴露敏感信息",
     "N","B","不要暴露敏感信息 -> credential-redaction rule"),
    (r"不要?(?:显示|输出|打印)(?:密码|口令|secret|token)",
     "N","B","不要显示密码 -> masking rule"),
    (r"(?:properly|appropriately|reasonably) (?:protect|handle|treat) (?:user |sensitive )?data",
     "V","B","properly protect data -> explicit masking rule"),
    (r"适当保护(?:用户)?数据|合理保护(?:用户)?数据",
     "V","B","适当保护数据 -> explicit masking rule"),

    # C: Tone
    (r"don'?t (?:be |sound |feel )?too formal",
     "N","C","don't be too formal -> casual-style directive"),
    (r"don'?t (?:be |sound |feel )?too casual|don'?t (?:be |sound |feel )?too informal",
     "N","C","don't be too casual -> formal-style directive"),
    (r"don'?t (?:be |sound )?(?:too )?(?:robotic|mechanical|stiff|like a robot)",
     "N","C","don't sound robotic -> natural-voice directive"),
    (r"don'?t (?:be |sound )?too (?:academic|scholarly|jargon[- ]?(?:heavy|laden))",
     "N","C","don't be too academic -> plain-language directive"),
    (r"avoid sounding too academic",
     "N","C","avoid sounding academic -> plain-language directive"),
    (r"不要?太(?:学术化?|学术性)|别太(?:学术化?|学术性)",
     "N","C","不要太学术化 -> plain-language directive"),
    (r"不要?太(?:技术性|technical)|别太(?:技术性|technical)",
     "N","C","不要太技术性 -> plain-language directive"),
    (r"不要?太正式|别太正式|不(?:能|要)太书面",
     "N","C","不要太正式 -> casual-style directive"),
    (r"不要?太随意|别太随意|不(?:能|要)太口语",
     "N","C","不要太随意 -> formal-style directive"),
    (r"不要?(?:有)?机翻感|别(?:有)?机翻感|不(?:能|要)(?:有)?翻译腔",
     "N","C","不要机翻感 -> natural-translation directive"),
    (r"(?:a )?(?:bit|little|slightly|somewhat) more formal",
     "V","C","a bit more formal -> formal delta directive"),
    (r"(?:a )?(?:bit|little|slightly|somewhat) more casual",
     "V","C","a bit more casual -> casual delta directive"),
    (r"稍微正式(?:一点|些)?|适当正式",
     "V","C","稍微正式一点 -> formal delta directive"),
    (r"稍微(?:随意|轻松)(?:一点|些)?|适当轻松",
     "V","C","稍微随意一点 -> casual delta directive"),

    # C: Tone — multilingual benchmarks
    (r"don'?t (?:mix|switch|blend|code[- ]?switch)(?: between)? languages?",
     "N","C","don't mix languages -> language-consistency rule"),
    (r"不要?(?:中英混用|混用语言|语言混杂)|不要?(?:切换|混合)语言",
     "N","C","不要混用语言 -> language-consistency rule"),
    (r"不要?(?:包含|有|出现|使用|写)(?:任何)?中文(?:字符|内容|文字|汉字)?",
     "N","C","不要包含中文 -> english-only rule"),
    (r"不要?(?:包含|有|出现|使用|写)(?:任何)?英文(?:字符|内容|单词)?",
     "N","C","不要包含英文 -> chinese-only rule"),
    (r"don'?t (?:include|use|add|contain|write|output)(?: any)? (?:Chinese|Mandarin)(?: characters?| text| script| language)?",
     "N","C","don't include Chinese -> english-only rule"),
    (r"don'?t (?:include|use|add|contain|write|output)(?: any)? (?:Japanese|Korean|Arabic|Cyrillic|Hebrew|Thai|Devanagari)(?: characters?| text| script| language)?",
     "N","C","don't include [script] -> script-exclusion rule"),

    # D: Format
    (r"don'?t use (?:bullet points?|lists?|numbered lists?)",
     "N","D","don't use bullet points -> prose directive"),
    (r"don'?t (?:add |use |include )?(?:too many )?headers?|avoid (?:too many )?headers?",
     "N","D","don't use too many headers -> header-count limit"),
    (r"don'?t use [Mm]arkdown",
     "N","D","don't use Markdown -> plain-text directive"),
    (r"don'?t use (?:fenced |triple-?backtick )?code blocks?",
     "N","D","don't use code blocks -> inline-code directive"),
    (r"not too many headers(?: please)?",
     "N","D","not too many headers -> header-count limit"),
    (r"不要?(?:用|加)(?:太多)?[Bb]ullet\s*[Pp]oints?|不要?(?:用|加)(?:太多)?列表|别用列表",
     "N","D","不要用列表 -> prose directive"),
    (r"不要?(?:加|用)(?:太多)?标题|别(?:加|用)(?:太多)?标题",
     "N","D","不要太多标题 -> header-count limit"),
    (r"不要?(?:换行|分行)太多|别(?:换行|分行)太多",
     "N","D","不要换行太多 -> paragraph-density directive"),
    (r"不要?用[Mm]arkdown|别用[Mm]arkdown",
     "N","D","不要用Markdown -> plain-text directive"),
    (r"don'?t use (?:any )?tables?|no tables?",
     "N","D","don't use tables -> list/prose alternative"),
    (r"don'?t (?:use|add|include) (?:any )?emojis?|no emojis?",
     "N","D","don't use emojis -> plain-text rule"),
    (r"don'?t (?:use|add) (?:any )?bold|no bold(?:ing)?|don'?t bold",
     "N","D","don't use bold -> plain-emphasis rule"),
    (r"don'?t (?:number|add numbers? to|use numbered) (?:the )?(?:items?|points?|steps?|sections?)",
     "N","D","don't number items -> unnumbered-list rule"),
    (r"don'?t (?:(?:write|make|format)(?: it)? )?like (?:a )?(?:slides?|presentation|deck|powerpoint|ppt)",
     "N","D","don't write like slides -> prose directive"),
    (r"不要?用表格|别用表格",
     "N","D","不要用表格 -> list/prose alternative"),
    (r"不要?(?:加|用|带)emoji|别(?:加|用)emoji|不要?用表情符号",
     "N","D","不要加emoji -> plain-text rule"),
    (r"不要?加粗|别加粗|不要?用粗体",
     "N","D","不要加粗 -> plain-emphasis rule"),
    (r"不要?加序号|别加序号|不要?用编号",
     "N","D","不要加序号 -> unnumbered rule"),
    (r"不要?(?:写(?:得)?)?像PPT|别(?:写(?:得)?)?像PPT|不要?像幻灯片",
     "N","D","不要像PPT -> prose directive"),
    (r"(?:proper|appropriate|reasonable|clean) (?:format(?:ting)?|layout|structure)",
     "V","D","appropriate formatting -> explicit format spec"),
    (r"适当排版|合理排版|格式(?:清晰|整洁)(?:一点)?",
     "V","D","适当排版 -> explicit format spec"),
    (r"不要?用代码块|别用代码块|不要?用三个反引号",
     "N","D","不要用代码块 -> inline-code directive"),
    (r"不要?(?:加|用)(?:数字)?编号|别(?:加|用)编号|不要?给(?:条目|步骤|要点)编号",
     "N","D","不要编号 -> unnumbered-list rule"),

    # E: Focus + disclaimers
    (r"don'?t (?:go |wander )?off[- ]?topic|avoid (?:going )?off[- ]?topic",
     "N","E","don't go off-topic -> focus-boundary directive"),
    (r"(?:stay on[- ]?topic|keep it (?:on[- ]?topic|focused|relevant))",
     "V","E","stay on topic -> focus-boundary directive"),
    (r"don'?t repeat(?: yourself)?|avoid (?:any )?repetition",
     "N","E","don't repeat -> deduplication directive"),
    (r"don'?t (?:add|include|inject) (?:your )?(?:own )?(?:opinion|bias|perspective)",
     "N","E","don't add opinion -> objectivity directive"),
    (r"don'?t (?:guess|speculate|(?:assume|make assumptions)(?!\s+(?:I'?m|I\s+am)\b))",
     "N","E","don't guess -> certainty-boundary directive"),
    (r"不要?跑题|别跑题",
     "N","E","不要跑题 -> focus-boundary directive"),
    (r"不要?重复(?:我的|我说的)?问题|别重复问题",
     "N","F","不要重复问题 -> direct-answer rule"),
    (r"不要?重复|别重复",
     "N","E","不要重复 -> deduplication directive"),
    (r"不要?(?:加|有|带)自己的观点|不要?主观",
     "N","E","不要加观点 -> objectivity directive"),
    (r"不要?猜测|别猜测",
     "N","E","不要猜测 -> certainty-boundary directive"),
    (r"(?:only )?(?:cover|focus on|address) (?:the )?(?:main|key|core|essential) (?:points?|aspects?|topics?)",
     "V","E","focus on main points -> scope directive"),
    (r"尽量客观|适当客观",
     "V","E","尽量客观 -> objectivity directive"),
    (r"don'?t (?:add|include|use|write) (?:any )?disclaimers?",
     "N","E","don't add disclaimers -> direct-statement rule"),
    (r"don'?t (?:hedge|over-?hedge|add (?:unnecessary |too many )?caveats?)",
     "N","E","don't hedge -> direct-statement rule"),
    (r"don'?t (?:add|say|use) (?:phrases? like )?(?:in my opinion|i think|i believe|i feel)",
     "N","E","don't say 'in my opinion' -> fact-statement rule"),
    (r"不要?加免责声明|别加免责声明",
     "N","E","不要加免责声明 -> direct-statement rule"),
    (r"不要?过度(?:谨慎|保守)|别太保守",
     "N","E","不要过度谨慎 -> direct-statement rule"),
    (r"不要?说仅供参考|不要?加仅供参考",
     "N","E","不要说仅供参考 -> direct-statement rule"),
    (r"不要?说(?:我(?:个人)?(?:觉得|认为|感觉)|依我看|在我看来)",
     "N","E","不要说我觉得 -> fact-statement rule"),
    (r"(?:只|仅)(?:关注|讨论|回答)(?:核心|关键|主要|重要)(?:内容|问题|要点|方面)",
     "V","E","只关注核心要点 -> scope directive"),

    # F: Output meta-structure
    (r"don'?t (?:start|begin|open) with (?:sure|of course|certainly|absolutely|great question|good question)[!.]?",
     "N","F","don't start with Sure! -> direct-open rule"),
    (r"don'?t (?:end|close|finish) with (?:hope (?:this |that )?helps?|let me know if (?:you have )?(?:any )?(?:more )?questions?|feel free to ask)[!.]?",
     "N","F","don't end with Hope this helps -> direct-close rule"),
    (r"don'?t (?:be |sound )?sycophant(?:ic)?|don'?t (?:flatter|compliment) me|(?:no|don'?t add) (?:empty )?(?:praise|flattery|compliments?)",
     "N","F","don't be sycophantic -> neutral-tone rule"),
    (r"don'?t (?:explain|show|walk(?: me)? through) your (?:reasoning|thought process|thinking)",
     "N","F","don't explain reasoning -> conclusion-only rule"),
    (r"don'?t (?:add|include|write) (?:a |an )?(?:preamble|intro(?:duction)?|opening paragraph)",
     "N","F","don't add preamble -> direct-start rule"),
    (r"don'?t (?:add|include|write|repeat) (?:a )?(?:summary|conclusion|closing|wrap-?up)(?: section)?",
     "N","F","don't add summary -> no-recap rule"),
    (r"don'?t (?:restate|repeat|rewrite|rephrase) (?:my |the )?(?:question|prompt|request)",
     "N","F","don't restate the question -> direct-answer rule"),
    (r"不要?开头说(?:当然|好的|没问题|当然可以)|别开头说(?:当然|好的|没问题)",
     "N","F","不要开头说当然好的 -> direct-open rule"),
    (r"不要?结尾说(?:希望这对你有帮助|如有问题欢迎继续提问|希望能帮到你)|别说希望这对你有帮助",
     "N","F","不要结尾说希望对你有帮助 -> direct-close rule"),
    (r"不要?拍马屁|别拍马屁|不要?夸我|别夸我",
     "N","F","不要拍马屁 -> neutral-tone rule"),
    (r"不要?解释你?的思路|别解释(?:你的)?思路|不要?展示推理过程",
     "N","F","不要解释思路 -> conclusion-only rule"),
    (r"不要?加前言|别加前言|不要?铺垫",
     "N","F","不要加前言 -> direct-start rule"),
    (r"不要?加总结|别加总结|不要?写总结",
     "N","F","不要加总结 -> no-recap rule"),

    # G: Depth / audience assumptions
    (r"don'?t (?:give|use|include|add) too many examples?",
     "N","G","don't give too many examples -> example-count limit"),
    (r"don'?t (?:over-?explain|explain (?:the )?obvious|state (?:the )?obvious)",
     "N","G","don't over-explain -> assumed-knowledge rule"),
    (r"don'?t (?:assume|treat me as|act (?:like|as if) I(?:'m| am)) (?:I'?m )?(?:a )?beginner|I(?:'m| am) not a beginner",
     "N","G","don't assume I'm a beginner -> expert-audience rule"),
    (r"don'?t (?:assume|act (?:like|as if) I(?:'m| am)) (?:I'?m )?(?:an? )?(?:expert|senior|advanced)",
     "N","G","don't assume I'm an expert -> beginner-audience rule"),
    (r"不要?举太多例子|别举太多例子",
     "N","G","不要举太多例子 -> example-count limit"),
    (r"不要?过度解释|别过度解释|不要?解释显而易见的",
     "N","G","不要过度解释 -> assumed-knowledge rule"),
    (r"不要?假设我不懂(?:基础)?|别把我当新手|我不是新手",
     "N","G","不要假设我不懂基础 -> expert-audience rule"),
    (r"不要?假设我(?:是|都)?懂|别假设我是专家|不要?假设我是专家",
     "N","G","不要假设我是专家 -> beginner-audience rule"),
    (r"(?:keep it |stay |be )(?:simple|easy to understand|accessible)",
     "V","G","keep it simple -> readability directive"),
    (r"尽量(?:简单|易懂|通俗)|适当(?:通俗|简单)",
     "V","G","尽量简单 -> readability directive"),

    # G: Depth — reasoning benchmarks (GSM8K / MATH / AIME)
    (r"don'?t (?:skip|omit|hide|abbreviate|leave out) (?:any )?(?:steps?|reasoning|work|derivations?|intermediate (?:steps?|results?))",
     "N","G","don't skip steps -> full-derivation rule"),
    (r"(?:don'?t|avoid) (?:round(?:ing)?|approximat(?:e|ing)) (?:intermediate|mid[- ]?step) (?:results?|values?|calculations?)",
     "N","G","don't round intermediate results -> exact-precision rule"),
    (r"don'?t (?:guess|estimate)(?: (?:the )?(?:answer|result|solution|value))?(?: when| if) (?:an )?exact (?:calculation|derivation|answer) (?:is )?(?:possible|required)",
     "N","G","don't guess when exact is possible -> exact-answer rule"),
    (r"不要?(?:跳过|省略|简化)(?:推理|计算|求解|推导)?步骤|不要?省略(?:中间|推导)过程",
     "N","G","不要跳过步骤 -> full-derivation rule"),
    (r"不要?(?:四舍五入|近似)(?:中间|推导)?(?:结果|数值|计算值)",
     "N","G","不要近似中间结果 -> exact-precision rule"),
    (r"(?:能(?:精确|准确)(?:计算|求解|推导)时)?不要?(?:猜|估算|估计)(?:答案|结果|数值)|不要?(?:猜|估算).*(?:精确|准确)(?:计算|求解)",
     "N","G","不要猜测可精确计算的答案 -> exact-answer rule"),

    # H: Code-specific
    (r"don'?t (?:over-?engineer|over-?design|add unnecessary (?:abstraction|complexity))",
     "N","H","don't over-engineer -> minimal-implementation rule"),
    (r"don'?t (?:add|write|include) (?:any )?(?:inline )?comments?",
     "N","H","don't add comments -> comment-free rule"),
    (r"don'?t (?:add|include|write) (?:any )?(?:error[- ]?handling|exception[- ]?handling|try[/-]?catch(?:[/-]?finally)?)",
     "N","H","don't add error handling -> happy-path-only rule"),
    (r"don'?t (?:add|include|use) (?:any )?type[- ]?(?:hints?|annotations?|signatures?)",
     "N","H","don't add type hints -> annotation-free rule"),
    (r"don'?t (?:change|modify|alter|touch) (?:the )?(?:function|method|class|API) (?:signature|interface|contract)",
     "N","H","don't change the signature -> interface-preservation rule"),
    (r"don'?t (?:change|modify|edit|touch) (?:any )?other files?|only (?:change|edit|modify) this file",
     "N","H","don't touch other files -> single-file-scope rule"),
    (r"don'?t (?:add|include|write) (?:any )?(?:doc(?:string)?s?|jsdoc|javadoc)",
     "N","H","don't add docstrings -> doc-free rule"),
    (r"don'?t (?:refactor|restructure|reorganize|rewrite) (?:the )?(?:existing|surrounding|other) code",
     "N","H","don't refactor surrounding code -> minimal-diff rule"),
    (r"不要?过度设计|别过度设计|不要?过度封装",
     "N","H","不要过度设计 -> minimal-implementation rule"),
    (r"不要?加注释|别加注释|不要?写注释",
     "N","H","不要加注释 -> comment-free rule"),
    (r"不要?加错误处理|别加错误处理|不要?加异常处理|不要?加try[/-]?catch",
     "N","H","不要加错误处理 -> happy-path-only rule"),
    (r"不要?加类型注解|别加类型注解|不要?加类型标注",
     "N","H","不要加类型注解 -> annotation-free rule"),
    (r"不要?改(?:函数|方法|类|接口)?签名|别改签名|不要?改接口",
     "N","H","不要改签名 -> interface-preservation rule"),
    (r"不要?改(?:其他|别的)文件|只改这(?:个|一个)文件|别动其他文件",
     "N","H","不要改其他文件 -> single-file-scope rule"),
    (r"不要?加docstring|不要?加文档注释|别加docstring",
     "N","H","不要加docstring -> doc-free rule"),
    (r"不要?重构(?:其他|周边|现有)?代码|别重构|不要?改(?:其他|现有)代码结构",
     "N","H","不要重构现有代码 -> minimal-diff rule"),

    # H: Code — benchmark-specific (HumanEval / MBPP)
    (r"don'?t (?:use|import|include|add|depend on) (?:any )?(?:external|third[- ]?party|non[- ]?standard)(?: libraries?| packages?| modules?| dependencies?)?",
     "N","H","don't use external libraries -> stdlib-only rule"),
    (r"don'?t (?:add|include|write) (?:any )?(?:test cases?|unit tests?|example usage|usage examples?|if __name__|__main__ block)",
     "N","H","don't add test cases -> implementation-only rule"),
    (r"不要?(?:使用|导入|引入|依赖)(?:任何)?(?:第三方|外部|非标准)(?:库|包|模块|依赖)",
     "N","H","不要使用第三方库 -> stdlib-only rule"),
    (r"不要?(?:添加|写|加)(?:测试用例|单元测试|示例用法|使用示例|main函数|__main__代码块)",
     "N","H","不要添加测试用例 -> implementation-only rule"),
    (r"don'?t (?:add|include|write|use|leave) (?:any )?(?:logging|debug|print|console\.log)(?: (?:statements?|calls?|output|messages?|lines?))?",
     "N","H","don't add logging -> logging-free rule"),
    (r"don'?t (?:hardcode|hard-?code)\b",
     "N","H","don't hardcode values -> named-constant rule"),
    (r"不要?(?:加|添加|写|输出)(?:日志|调试|debug|log|print)(?:语句|代码|输出|调用)?",
     "N","H","不要加日志 -> logging-free rule"),
    (r"不要?(?:硬编码|魔法数字|魔术数字|写死(?:数值|字符串)?)",
     "N","H","不要硬编码值 -> named-constant rule"),

    # I: Image / Video generation
    (r"don'?t (?:make it |be )?(?:too )?photo-?realistic|(?:no|avoid) photo-?realism",
     "N","I","don't be photorealistic -> stylized-render directive"),
    (r"don'?t (?:make it |be )?(?:too )?(?:dark|dim|underexposed)",
     "N","I","don't be too dark -> brightness floor"),
    (r"don'?t (?:make it |be )?(?:too )?(?:bright|overexposed)",
     "N","I","don't be too bright -> brightness ceiling"),
    (r"don'?t (?:make it |be )?(?:too )?(?:blurry|out[- ]of[- ]focus)",
     "N","I","don't be blurry -> sharpness directive"),
    (r"don'?t (?:add|include|use) (?:any )?(?:text|watermarks?|logos?|overlays?|captions?)",
     "N","I","don't add watermarks/text -> clean-output directive"),
    (r"don'?t (?:generate|show|include|depict) (?:any )?(?:human )?(?:faces?|portraits?)",
     "N","I","don't generate faces -> face-exclusion directive"),
    (r"don'?t (?:make it |be )?(?:too )?(?:cartoon(?:ish|y)?|anime|cel[- ]shaded)",
     "N","I","don't be too cartoony -> realistic-render directive"),
    (r"don'?t (?:use|include|add) (?:any )?(?:nsfw|explicit|adult|sexual|violent|gore) (?:content|elements?|imagery)?",
     "N","I","don't use NSFW content -> SFW-only directive"),
    (r"don'?t (?:crop|cut off) (?:the )?(?:subject|figure|character|person|head|body)",
     "N","I","don't crop the subject -> full-frame directive"),
    (r"don'?t (?:change|alter|modify) (?:the )?(?:style|aesthetic|look and feel)",
     "N","I","don't change the style -> style-lock directive"),
    (r"不要?太写实|别太写实|不要?写实风格",
     "N","I","不要太写实 -> stylized-render directive"),
    (r"不要?太暗|别太暗|不要?太昏暗",
     "N","I","不要太暗 -> brightness floor"),
    (r"不要?太亮|别太亮|不要?曝光过度",
     "N","I","不要太亮 -> brightness ceiling"),
    (r"不要?模糊|别模糊|不要?失焦",
     "N","I","不要模糊 -> sharpness directive"),
    (r"不要?(?:加|有|带)水印|不要?(?:加|有|带)文字|别加水印",
     "N","I","不要加水印 -> clean-output directive"),
    (r"不要?(?:生成|出现|展示)(?:人脸|面部|脸部)|不要?人脸",
     "N","I","不要生成人脸 -> face-exclusion directive"),
    (r"不要?太卡通|别太卡通|不要?卡通风格",
     "N","I","不要太卡通 -> realistic-render directive"),
    (r"不要?(?:出现|包含|生成)(?:色情|裸露|暴力|血腥|NSFW)(?:内容|元素|画面)?",
     "N","I","不要出现NSFW内容 -> SFW-only directive"),
    (r"不要?裁剪(?:主体|人物|角色|头部)|不要?切掉(?:头|脚|手)",
     "N","I","不要裁剪主体 -> full-frame directive"),
    (r"不要?(?:改变|更改)(?:风格|画风|美术风格)|保持(?:原有)?风格",
     "N","I","不要改变风格 -> style-lock directive"),
    (r"(?:consistent|maintain|preserve|keep) (?:the )?(?:style|aesthetic|visual language)",
     "V","I","maintain style consistency -> style-lock directive"),
    (r"(?:don'?t|avoid|no) (?:(?:add(?:ing)?|include|including|embed(?:ding)?|put(?:ting)?|show(?:ing)?) (?:any )?)?watermarks?",
     "N","I","avoid watermarks -> watermark-free directive"),
    (r"(?:don'?t|avoid|no) (?:show(?:ing)?|render(?:ing)?|include|add(?:ing)?) (?:any )?(?:human )?faces?|(?:no|without) (?:visible )?faces?",
     "N","I","no faces -> face-free composition directive"),
    (r"(?:don'?t|avoid|no) (?:NSFW|explicit|adult|sexual|violent|gore|graphic) (?:content|imagery|material)?",
     "N","I","no NSFW content -> safe-content directive"),
    (r"(?:don'?t|avoid) (?:creat(?:e|ing)|generat(?:e|ing)|render(?:ing)) (?:realistic|photorealistic|hyperrealistic) (?:people|faces?|humans?|persons?)",
     "N","I","no realistic people -> stylized-figure directive"),
    (r"适当(?:明亮|亮度)|合适的(?:亮度|光线)",
     "V","I","适当亮度 -> brightness range"),
    (r"(?:背景)?不要?(?:有|出现)?太多(?:的)?人(?:物|群)?|不要?(?:太拥挤|太多人流)|背景不要?太多人",
     "N","I","不要太多人 -> crowd-density directive"),
    (r"don'?t (?:add|include|put|show) too many people(?: in (?:the )?(?:background|scene|frame))?",
     "N","I","don't add too many people -> crowd-density directive"),
    (r"(?:keep (?:the )?(?:background|scene) (?:sparse|empty|uncrowded|minimal))|(?:no crowds?|(?:not too many|few) people in (?:the )?(?:background|scene))",
     "N","I","keep background sparse -> crowd-density directive"),
    (r"不要?太暴露|不要?穿(?:太少|得太少)|别太暴露",
     "N","I","不要太暴露 -> SFW-clothing directive"),
    (r"不要?(?:有)?(?:手指|手部)(?:崩坏|变形|畸形|错误|扭曲)(?:的问题)?|手指(?:崩坏|变形|畸形)(?:的问题)?",
     "N","I","不要手指崩坏 -> hand-anatomy directive"),
    (r"不要?(?:斗鸡眼|对眼|眼神涣散|眼珠偏移)|眼睛不要?(?:斜视|对视)",
     "N","I","不要斗鸡眼 -> eye-alignment directive"),
    (r"don'?t (?:make (?:the )?)?(?:fingers?|hands?) (?:deformed|distorted|malformed|broken|messed up)",
     "N","I","don't deform fingers -> hand-anatomy directive"),
    (r"(?:no|don'?t) (?:cross[- ]?eyed|wall[- ]?eyed|lazy eye|strabismus|misaligned eyes?)",
     "N","I","no cross-eyed -> eye-alignment directive"),
    (r"(?:避免|不要?(?:有|带|嵌入|添加))水印|(?:去掉|移除)水印",
     "N","I","避免水印 -> watermark-free directive"),
    (r"(?:不要?|别)(?:出现|展示|渲染|包含)(?:任何)?(?:人)?(?:面部|脸(?:部)?)|(?:画面中)?(?:不要?|别)(?:有|出现)脸",
     "N","I","不要出现脸 -> face-free composition directive"),
    (r"(?:不要?|别)(?:出现|包含|生成)(?:色情|裸露|暴力|血腥|不雅|敏感)(?:内容|画面|素材)?",
     "N","I","不要敏感内容 -> safe-content directive"),
    (r"(?:不要?|别)(?:生成|创建|渲染)(?:写实|逼真|超写实)(?:的)?(?:人物|人脸|人像|角色)",
     "N","I","不要写实人物 -> stylized-figure directive"),

    # I: Audio / Music generation
    (r"don'?t (?:make it |be )?(?:too )?(?:loud|ear-?splitting|piercing|harsh|noisy)",
     "N","I","don't be too loud -> loudness ceiling"),
    (r"don'?t (?:make it |be )?(?:too )?(?:quiet|silent|inaudible)",
     "N","I","don't be too quiet -> loudness floor"),
    (r"don'?t (?:make it |be )?(?:too )?(?:generic|mainstream|pop(?:py)?|commercial|cliché|cliche)",
     "N","I","don't be too generic -> originality directive"),
    (r"don'?t (?:add|use|include) (?:any )?(?:vocals?|singing|voice|lyrics?)",
     "N","I","don't add vocals -> instrumental-only directive"),
    (r"don'?t (?:change|alter|break|vary) (?:the )?(?:tempo|bpm|time signature|rhythm)",
     "N","I","don't change tempo -> tempo-lock directive"),
    (r"不要?太(?:吵|嘈杂|刺耳)|别太响|不要?太响",
     "N","I","不要太吵 -> loudness ceiling"),
    (r"不要?太(?:安静|轻|小声)|别太安静",
     "N","I","不要太安静 -> loudness floor"),
    (r"不要?太(?:流行|商业化|俗气)|不要?太[Pp]op",
     "N","I","不要太流行 -> originality directive"),
    (r"不要?(?:加|有|使用)人声|不要?(?:唱歌|歌词|演唱)",
     "N","I","不要加人声 -> instrumental-only directive"),
    (r"不要?(?:改变|改动)(?:节拍|[Bb][Pp][Mm]|速度|节奏|拍号)",
     "N","I","不要改变节拍 -> tempo-lock directive"),

    # J: Agent / Tool-use
    (r"(?:don'?t|avoid|no) (?:auto[- ]?execut(?:e|ion|ing)?|automatically (?:execut|run|apply)|execut(?:e|ing) (?:it |this |that |the changes? )?automatically)"
     r"|(?:ask|confirm|pause) (?:me )?before (?:executing|running|applying|doing)",
     "N","J","don't execute automatically -> confirm-before-act rule"),
    (r"(?:don'?t|avoid) (?:call(?:ing)?|use|using|invoke|invoking) (?:too many |excessive )?tools?(?: too many times?)?"
     r"|(?:minimize|reduce) tool (?:calls?|use)",
     "N","J","don't call too many tools -> tool-call budget"),
    (r"(?:don'?t|avoid|no) (?:touch(?:ing)?|modify(?:ing)?|access(?:ing)?|chang(?:e|ing)|deploy(?:ing)? to) (?:the )?(?:prod(?:uction)?|live|staging)(?: (?:environment|server|databases?|system|db))?",
     "N","J","don't touch production -> environment-guard rule"),
    (r"(?:don'?t|avoid|no) (?:delete|deleting|drop(?:ping)?|truncat(?:e|ing)|wip(?:e|ing)|destroy(?:ing)?|remov(?:e|ing)) (?:any )?(?:data|records?|rows?|tables?|files?|buckets?)",
     "N","J","don't delete data -> soft-delete-only rule"),
    (r"(?:don'?t|avoid|no) (?:access(?:ing)?|use|using|call(?:ing)?|fetch(?:ing)? from) (?:the )?(?:internet|web|external (?:API|service|URL))|(?:offline|no internet)",
     "N","J","don't access the internet -> offline-only rule"),
    (r"(?:don'?t|avoid) (?:make|send|fire|mak(?:e|ing)|send(?:ing)|fir(?:e|ing)) (?:any )?(?:external|outbound|network|HTTP|API)(?: API)? (?:requests?|calls?)(?: without (?:explicit )?(?:confirmation|approval))?",
     "N","J","don't make external calls -> network-isolated rule"),
    (r"(?:don'?t|avoid) (?:loop(?:ing)?|retr(?:y|ying)) (?:more than \d+ times?|indefinitely|forever|endlessly|too (?:many times?|much|often)|more than (?:necessary|needed))"
     r"|(?:don'?t|avoid) (?:excessive|unnecessary|too many) retries?",
     "N","J","don't retry excessively -> retry-budget rule"),
    (r"(?:don'?t|avoid) (?:store|save|persist|cache|write) (?:any )?(?:data|state|results?|output)(?: (?:to disk|locally|to file|to database))?",
     "N","J","don't persist data -> memory-only rule"),
    (r"不要?自动执行|别自动执行|不要?直接执行|先(?:确认|问我)",
     "N","J","不要自动执行 -> confirm-before-act rule"),
    (r"不要?(?:频繁|过多|太多)(?:调用|使用)?工具|减少工具调用",
     "N","J","不要频繁调用工具 -> tool-call budget"),
    (r"不要?(?:碰|改|访问|部署到)(?:生产|线上|prod)(?:环境|数据库|服务器)?",
     "N","J","不要碰生产环境 -> environment-guard rule"),
    (r"不要?(?:删除|清空|截断|销毁)(?:任何)?(?:数据|记录|文件|表)",
     "N","J","不要删除数据 -> soft-delete-only rule"),
    (r"不要?(?:联网|访问外网|调用外部API)|离线(?:运行|操作)",
     "N","J","不要联网 -> offline-only rule"),
    (r"不要?(?:无限|死)循环|不要?(?:无限|死)重试",
     "N","J","不要死循环 -> retry-budget rule"),

    # J: Agent — Web browsing scope (WebArena / Mind2Web)
    (r"(?:don'?t|avoid) (?:navigat(?:e|ing)|go(?:ing)?|leav(?:e|ing)|redirect(?:ing)?) (?:away from|outside|beyond|off) (?:the )?(?:current |this )?(?:domain|site|page|origin)",
     "N","J","don't navigate outside domain -> domain-lock rule"),
    (r"(?:don'?t|avoid|never) (?:submit|checkout|purchase|place (?:an )?order|confirm (?:the )?(?:order|purchase|payment)|click (?:buy|checkout|pay))",
     "N","J","don't submit/purchase -> submit-guard rule"),
    (r"(?:don'?t|avoid) (?:log(?:ging)? (?:in|out)|sign(?:ing)? (?:in|out)|switch(?:ing)? accounts?|authenticat(?:e|ing))",
     "N","J","don't log in/out -> auth-state-lock rule"),
    (r"不要?(?:离开|跳出|跳转到)(?:当前)?(?:域名|网站|页面)|不要?(?:跨域|导航到其他网站)",
     "N","J","不要离开当前域名 -> domain-lock rule"),
    (r"不要?(?:提交|结算|购买|下单|确认订单|支付|点击购买)",
     "N","J","不要提交/购买 -> submit-guard rule"),
    (r"不要?(?:登录|退出登录|登出|切换账号)|不要?改变(?:登录|认证)状态",
     "N","J","不要登录退出 -> auth-state-lock rule"),

    # J: Agent — OS / Computer use (OSWorld)
    (r"(?:don'?t|avoid|never) (?:use|run|execute|invoke) (?:as |with )?(?:root|sudo|administrator|admin|elevated)(?: privileges?)?",
     "N","J","don't use sudo/root -> privilege-guard rule"),
    (r"(?:don'?t|avoid) (?:modify|edit|change|write to|overwrite|touch) (?:any )?(?:system files?|/etc|/sys|/proc|/boot|/usr|windows registry|registry keys?)",
     "N","J","don't modify system files -> system-file-guard rule"),
    (r"(?:don'?t|avoid) (?:install|uninstall|upgrade|downgrade|remove) (?:any )?(?:software|packages?|dependencies|libraries|modules?|extensions?)",
     "N","J","don't install software -> install-guard rule"),
    (r"(?:don'?t|avoid) (?:modify|edit|change|overwrite|touch) (?:any )?(?:config(?:uration)?|\.env|environment|settings?) files?",
     "N","J","don't modify config files -> config-guard rule"),
    (r"(?:don'?t|avoid) (?:escalat(?:e|ing) privileges?|request(?:ing)? elevated permissions?|gain(?:ing)? (?:higher|more) (?:access|permissions?))",
     "N","J","don't escalate privileges -> privilege-escalation-guard rule"),
    (r"不要?(?:使用|运行|执行)\s*(?:sudo|root)(?:\s*权限)?|不要?以\s*(?:root|管理员)(?:\s*身份|\s*权限)?(?:运行|执行)|不要?使用\s*管理员权限",
     "N","J","不要使用sudo/root -> privilege-guard rule"),
    (r"不要?(?:修改|编辑|写入)(?:系统文件|/etc|/sys|/boot|系统目录|注册表)",
     "N","J","不要修改系统文件 -> system-file-guard rule"),
    (r"不要?(?:安装|卸载|升级|降级)(?:任何)?(?:软件|包|依赖|库|模块|插件)",
     "N","J","不要安装软件 -> install-guard rule"),
    (r"不要?(?:修改|编辑|覆盖)(?:配置文件|\.env|环境变量文件|settings)",
     "N","J","不要修改配置文件 -> config-guard rule"),
    (r"不要?(?:提权|请求更高权限|使用chmod\s*777|切换到root)",
     "N","J","不要提权 -> privilege-escalation-guard rule"),
    (r"不要?(?:发送?|发起|调用|请求)(?:任何)?(?:外部|外网|网络|HTTP|API)(?:请求|调用|接口|服务)|不要?(?:请求|访问)外部(?:API|接口|服务)",
     "N","J","不要发外部请求 -> network-isolated rule"),
    (r"不要?(?:保存|存储|持久化|缓存|写入)(?:任何)?(?:数据|状态|结果|输出)(?:到(?:磁盘|文件|数据库))?",
     "N","J","不要持久化数据 -> memory-only rule"),

    # J: Agent — Database safety (AgentBench)
    (r"(?:don'?t|avoid|never) (?:run|execute|use) (?:any )?(?:DROP|TRUNCATE)(?:\s+(?:or|and|/)\s+(?:DROP|TRUNCATE))*(?:\s+(?:TABLE|DATABASE|INDEX|statements?))*",
     "N","J","don't run DROP/TRUNCATE -> ddl-guard rule"),
    (r"(?:don'?t|avoid) (?:run|execute) (?:a |any )?DELETE (?:statement )?without (?:a )?WHERE(?: clause)?",
     "N","J","don't DELETE without WHERE -> safe-delete rule"),
    (r"(?:don'?t|avoid) (?:modify|alter|change|drop) (?:the )?(?:database )?schema",
     "N","J","don't modify schema -> schema-guard rule"),
    (r"不要?(?:执行|运行)(?:DROP|TRUNCATE)(?:\s+TABLE|\s+DATABASE)?语句",
     "N","J","不要执行DROP/TRUNCATE -> ddl-guard rule"),
    (r"不要?执行没有WHERE(?:子句)?的DELETE|不要?全表DELETE",
     "N","J","不要全表DELETE -> safe-delete rule"),
    (r"不要?(?:修改|变更|DROP)(?:数据库)?(?:结构|schema|表结构|字段)",
     "N","J","不要修改schema -> schema-guard rule"),

    # J: Agent — Budget / step limits (GAIA / τ-bench)
    (r"(?:don'?t|avoid) (?:exceed|go over|surpass) (?:the )?(?:\d+ )?(?:step|iteration|turn|action)(?: limit| budget| cap)?",
     "N","J","don't exceed step limit -> step-budget rule"),
    (r"(?:don'?t|avoid) (?:exceed|go over|surpass) (?:the )?(?:cost|token|API|spending)(?: limit| budget| cap)?",
     "N","J","don't exceed budget -> cost-budget rule"),
    (r"不要?(?:超过|超出)\s*(?:\d+\s*)?(?:步|轮|次|迭代)(?:限制|上限|预算)?",
     "N","J","不要超过步数限制 -> step-budget rule"),
    (r"不要?(?:超过|超出)(?:费用|token|API|预算)(?:限制|上限)?",
     "N","J","不要超出预算 -> cost-budget rule"),

    # J: Agent — system prompt confidentiality (IFEval / safety benchmarks)
    (r"don'?t (?:reveal|disclose|share|expose|repeat|output|show|print)(?: the)? (?:system prompt|system message|(?:these |the )?instructions|(?:this |the )?prompt)",
     "N","J","don't reveal system prompt -> confidentiality rule"),
    (r"不要?(?:透露|泄露|分享|输出|重复|展示)(?:系统提示词|系统prompt|system prompt|指令内容|这些指令)",
     "N","J","不要透露系统提示词 -> confidentiality rule"),

    # K: LLM output quality (hallucination, citation, faithfulness)
    # Specific patterns must come before the broad "don't hallucinate" pattern to avoid being shadowed.
    (r"don'?t (?:make up|invent|fabricate|guess) (?:any )?(?:numbers?|statistics?|dates?|names?|quotes?)",
     "N","K","don't make up numbers -> numeric-grounding rule"),
    (r"don'?t (?:cite|reference|mention) (?:sources?|papers?|articles?|URLs?) (?:you )?(?:haven't|don't) (?:read|seen|have)",
     "N","K","don't cite unseen sources -> verified-citation rule"),
    (r"don'?t (?:hallucinate|make[-\s]up|fabricate|invent|confabulate)(?: facts?| information| data| sources?)?",
     "N","K","don't hallucinate -> grounding rule"),
    (r"don'?t (?:go |be )(?:beyond|outside) (?:the )?(?:context|provided (?:text|document|data))",
     "N","K","don't go beyond context -> context-bound rule"),
    (r"don'?t (?:change|alter|paraphrase|modify) (?:the )?(?:original |source )?(?:text|quote|passage|wording)",
     "N","K","don't alter the source text -> verbatim-reproduction rule"),
    # Specific patterns must come before the broad 不要编造 pattern to avoid being shadowed.
    (r"不要?编造(?:数字|数据|统计|日期|姓名|引语)|不要?捏造数据",
     "N","K","不要编造数字 -> numeric-grounding rule"),
    (r"不要?引用(?:没有|未)?(?:读过|看过|提供的)?(?:来源|文献|链接|URL)|不要?伪造引用",
     "N","K","不要伪造引用 -> verified-citation rule"),
    (r"不要?幻觉|不要?编造|别编造|不要?捏造",
     "N","K","不要幻觉/编造 -> grounding rule"),
    (r"不要?超出(?:上下文|文档|资料)(?:范围|内容)|只基于(?:提供的|给定的)?(?:文档|资料|上下文)",
     "N","K","不要超出上下文 -> context-bound rule"),
    (r"不要?(?:改动|篡改|转述|意译)原文|保持原文(?:不变|原样)",
     "N","K","不要改动原文 -> verbatim-reproduction rule"),

    # K: LLM faithfulness — summarization / reading comprehension benchmarks
    (r"don'?t (?:add|include|inject|insert) (?:any )?(?:information|content|details?|facts?) (?:not|that (?:is|are) not|that (?:isn'?t|aren'?t)) (?:in|from|present in|found in) (?:the )?(?:source|passage|document|text|article)",
     "N","K","don't add info not in source -> source-grounded summarisation"),
    (r"don'?t (?:attempt to |try to )?answer (?:(?:the )?question )?(?:if|when) (?:(?:the )?(?:question|answer) (?:is|cannot be|can'?t be) (?:answered|found|answerable)|(?:the )?(?:question is |it is )?unanswerable|it (?:is|can'?t be) (?:answered|found) in (?:the )?(?:passage|text|context|document))",
     "N","K","don't answer unanswerable -> extractive-QA rule"),
    (r"不要?(?:添加|加入|注入)(?:原文|原文中|文章中|段落中)没有的(?:信息|内容|细节|事实)",
     "N","K","不要添加原文外信息 -> source-grounded summarisation"),
    (r"不要?(?:强行|试图)回答(?:原文|段落|文档)中(?:找不到|没有)答案的问题",
     "N","K","不要强行回答无法回答的问题 -> extractive-QA rule"),

    # L: Ethics / Bias
    (r"don'?t (?:be |show |have |demonstrate |exhibit )?(?:biased|discriminatory|prejudiced)(?: (?:against|towards?) \w+)?",
     "N","L","don't be biased -> multi-perspective directive"),
    (r"don'?t (?:discriminate|stereotype|generalize)(?: (?:against|about) \w+)?",
     "N","L","don't discriminate/stereotype -> identity-neutral directive"),
    (r"don'?t (?:add|inject|include) (?:any )?(?:political|religious|ideological)(?: bias| slant| agenda)?",
     "N","L","don't add political bias -> neutrality directive"),
    (r"(?:be |stay |remain |keep it )?(?:fair(?:ly)?|balanced|neutral|unbiased)(?: and (?:balanced|neutral|objective))?",
     "V","L","be fair/balanced -> multi-perspective directive"),
    (r"不要?(?:有|带|存在)?偏见|别有偏见|不要?偏颇|保持客观中立",
     "N","L","不要有偏见 -> multi-perspective directive"),
    (r"不要?(?:歧视|刻板印象|以偏概全)(?:某|特定|某个)?(?:群体|族裔|性别|人群)?",
     "N","L","不要歧视/刻板印象 -> identity-neutral directive"),
    (r"不要?(?:加入|带入|含有|带)?(?:政治|宗教|意识形态)(?:立场|偏见|倾向|色彩)",
     "N","L","不要带政治立场 -> neutrality directive"),
    (r"保持(?:公正|平衡|中立)|尽量(?:公正|中立|平衡)",
     "V","L","保持公正/中立 -> multi-perspective directive"),
]

PATTERNS = [
    (re.compile(raw, re.IGNORECASE | re.UNICODE), stype, cat, desc)
    for raw, stype, cat, desc in _RAW
]

_FALLBACK_NEGATIVE = re.compile(
    r"(?:"
    # Explicit negation words (尽量不要 before 不要 so it matches as one unit)
    r"尽量不要?|不要?|别|不能|不得|禁止|避免"
    r"|don'?t|never(?!\s+mind)"
    r"|(?<! to )(?<!\w)avoid"
    r"|try\s+not\s+to|try\s+to\s+avoid|prefer\s+not\s+to|refrain\s+from"
    r"|without\s+(?:any\s+)?(?=\w)"
    # English "not too" pattern (not caught by don't)
    r"|(?<!\w)not\s+too\s+"
    r")"
    r"[^\n、，。；！？：…）,;!?:)]{1,20}",
    re.IGNORECASE | re.UNICODE,
)
# Self-contained idiomatic constraint phrases (no trailing content required)
_FALLBACK_IDIOM = re.compile(
    r"(?:"
    r"(?:tone|dial|scale|rein)\s+(?:it\s+)?(?:down|back)"
    r"|(?:cut|keep|trim|strip)\s+(?:it\s+)?(?:down|short|brief|tight|minimal|back|out)"
    r"|(?:go\s+easy|ease\s+up)(?:\s+(?:on|with))?"
    # Chinese "太+negative-adj" without explicit negation (implicit "too much")
    r"|太(?:乱|杂|长|短|多|少|慢|快|大|小|暗|亮|吵|安静|模糊|复杂|简单|正式|随意|学术|技术|抽象|啰嗦|冗长)"
    r")"
    r"[^\n、，。；！？：…）,;!?:)]{0,20}",
    re.IGNORECASE | re.UNICODE,
)
_FALLBACK_VAGUE = re.compile(
    r"(?:"
    # Original vague qualifiers
    r"尽量|适当|合适(?:的)?|稍微|大概|差不多"
    r"|somewhat|(?:a\s+)?(?:bit|little)\s+(?:more|less)"
    r"|appropriate(?:ly)?|reasonable(?:ly)?|roughly|kind\s+of"
    # Chinese "adj+一点/一些" at end of clause (implicit vagueness)
    r"|[\u4e00-\u9fff]{1,4}[一](?:点|些|点点|点儿)(?=[、，。；！？：…）,;!?:)\s]|$)"
    # Chinese "要+vague_adj" at end of clause (positive but imprecise)
    r"|要(?:协调|统一|一致|和谐|整齐|规范|美观|清晰|自然|合理|均匀|平衡|连贯|流畅)(?=[、，。；！？：…）,;!?:)\s]|$)"
    # English comparative vagueness
    r"|(?:more|less)\s+(?:formal|casual|concise|detailed|verbose|brief|readable|technical)"
    r"|(?:make|keep)\s+it\s+(?:more|less)\s+\w+"
    r")"
    r"[^\n、，。；！？：…）,;!?:)]{0,30}",
    re.IGNORECASE | re.UNICODE,
)


_PREFIX_MUST_NOT = re.compile(
    r"(?:never\s+|禁止|绝不|绝对不(?:要|能|得)?)$",
    re.IGNORECASE | re.UNICODE,
)
_PREFIX_PREFER_NOT = re.compile(
    r"(?:尽量(?:不要?)?|try\s+(?:not\s+to\s+|to\s+avoid\s+)|prefer\s+not\s+to\s+)$",
    re.IGNORECASE | re.UNICODE,
)

def scan(text):
    candidates = []
    for pattern, stype, cat, desc in PATTERNS:
        for m in pattern.finditer(text):
            candidates.append((m.start(), m.end(), m.group(0), stype, cat, desc))
    candidates.sort(key=lambda c: (c[0], -(c[1] - c[0])))
    claimed, spans = [], []
    for s, e, matched_text, stype, cat, desc in candidates:
        if any(s < b and e > a for a, b in claimed):
            continue
        claimed.append((s, e))
        sp = Span(s, e, matched_text, stype, cat, desc)
        # First detect strength from the matched text itself
        sp.strength = _detect_strength(matched_text)
        # Then check for strength modifiers in the text immediately preceding the span
        # Prefix modifiers can only upgrade strength (SHOULD_NOT → MUST_NOT or PREFER_NOT)
        if sp.strength == "SHOULD_NOT":
            prefix = text[max(0, s - 20):s]
            if _PREFIX_MUST_NOT.search(prefix):
                sp.strength = "MUST_NOT"
            elif _PREFIX_PREFER_NOT.search(prefix):
                sp.strength = "PREFER_NOT"
        spans.append(sp)
    spans.sort(key=lambda sp: sp.start)
    return spans


# Matches subordinating/relative conjunctions that introduce factual clauses rather than directives.
# Used to filter out false-positive negations like "why Python doesn't have X".
_SUBORD_CLAUSE = re.compile(
    r"\b(?:why|because|that|which|who|how|since|as|when|where|whether|if)\s*$",
    re.IGNORECASE,
)

def scan_unmatched(text, claimed_intervals):
    gaps, cursor = [], 0
    for s, e in sorted(claimed_intervals):
        if cursor < s: gaps.append((cursor, s))
        cursor = e
    if cursor < len(text): gaps.append((cursor, len(text)))

    unmatched = []
    claimed_u = []  # track intervals to avoid overlapping unmatched spans
    for gs, ge in gaps:
        seg = text[gs:ge]
        for pat, stype in [(_FALLBACK_NEGATIVE,"N"), (_FALLBACK_IDIOM,"N"), (_FALLBACK_VAGUE,"V")]:
            for m in pat.finditer(seg):
                abs_s, abs_e = gs + m.start(), gs + m.end()
                # Skip if overlaps with an already-claimed unmatched span
                if any(abs_s < b and abs_e > a for a, b in claimed_u):
                    continue
                # Skip negations embedded in subordinate/relative clauses (factual, not directive)
                if pat is _FALLBACK_NEGATIVE:
                    prefix = seg[max(0, m.start() - 25):m.start()]
                    if _SUBORD_CLAUSE.search(prefix):
                        continue
                phrase = m.group(0).strip()
                claimed_u.append((abs_s, abs_e))
                sp = Span(abs_s, abs_e, phrase, stype, "?", "unmatched -- requires LLM")
                sp.strength = _detect_strength(phrase)
                unmatched.append(sp)
    return unmatched


def backfill(text, replacements):
    """Splice directives into text at the given offsets.

    replacements: list of dicts with keys {start, end, directive}
    Only entries with a non-empty 'directive' are applied.
    Invalid entries (start > end, negative offsets) are silently skipped.
    Overlapping replacements are skipped (first-come by start position wins).
    """
    applicable = sorted(
        [r for r in replacements
         if r.get('directive') and r.get('start', -1) >= 0 and r.get('end', -1) >= r.get('start', -1)],
        key=lambda r: r['start'],
    )
    parts, cursor = [], 0
    for rep in applicable:
        if rep['start'] < cursor:
            continue  # skip overlapping replacement
        parts.append(text[cursor:rep['start']])
        parts.append(rep['directive'])
        cursor = rep['end']
    parts.append(text[cursor:])
    return "".join(parts)


SEP = "-" * 70

def print_scan_only(text):
    spans = scan(text)
    all_spans = sorted(spans + scan_unmatched(text, [(s.start,s.end) for s in spans]), key=lambda s: s.start)
    print("SCAN RESULTS\n" + SEP)
    if not all_spans:
        print("  (no constraint spans detected)")
    else:
        print(f"  {'#':<3}  {'Type':<5}  {'Cat':<4}  {'Offset':<10}  Span text")
        print(f"  {'---':<3}  {'----':<5}  {'---':<4}  {'------':<10}  ---------")
        for i, sp in enumerate(all_spans, 1):
            print(f"  {i:<3}  {sp.span_type:<5}  {sp.category:<4}  {sp.start}-{sp.end:<6}  {sp.text!r}")
    print(SEP + f"\nTotal: {len(all_spans)} constraint span(s) detected")


def print_list_patterns():
    print(f"{'#':<4}  {'Type':<5}  {'Cat':<4}  Description")
    print("-" * 70)
    for i, (_, stype, cat, desc) in enumerate(PATTERNS, 1):
        print(f"{i:<4}  {stype:<5}  {cat:<4}  {desc}")


def main():
    parser = argparse.ArgumentParser(description="dont-to-do: SCAN and BACKFILL phases of the prompt constraint compiler.")
    parser.add_argument("query", nargs="?")
    parser.add_argument("--scan-only", action="store_true", help="Human-readable scan output")
    parser.add_argument("--scan-json", action="store_true", help="JSON scan output (default mode)")
    parser.add_argument("--backfill",  action="store_true", help="Read JSON from stdin and splice directives")
    parser.add_argument("--list",      action="store_true", help="List all patterns in the library")
    args = parser.parse_args()

    if args.list:
        print_list_patterns()
        return

    # --backfill: read JSON from stdin, write refined text to stdout
    if args.backfill:
        raw = sys.stdin.read()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON input for --backfill: {e}", file=sys.stderr)
            sys.exit(1)
        if "text" not in data:
            print("Error: --backfill JSON must contain a 'text' key", file=sys.stderr)
            sys.exit(1)
        text = data["text"]
        replacements = data.get("replacements", [])
        print(backfill(text, replacements), end="")
        return

    # Read input text
    text = args.query if args.query else (sys.stdin.read().strip() if not sys.stdin.isatty() else None)
    if text is None:
        parser.print_help()
        sys.exit(1)

    if args.scan_only:
        print_scan_only(text)
        return

    # Default mode (--scan-json or no flag): output JSON scan result
    spans = scan(text)
    claimed = [(sp.start, sp.end) for sp in spans]
    unmatched_spans = scan_unmatched(text, claimed)

    result = {
        "text": text,
        "spans": [
            {
                "start": sp.start,
                "end": sp.end,
                "text": sp.text,
                "type": sp.span_type,
                "category": sp.category,
                "strength": sp.strength,
                "description": sp.description,
            }
            for sp in spans
        ],
        "unmatched": [
            {
                "start": sp.start,
                "end": sp.end,
                "text": sp.text,
                "type": sp.span_type,
                "strength": sp.strength,
            }
            for sp in unmatched_spans
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
