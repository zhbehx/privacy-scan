#!/usr/bin/env python3
"""发布前隐私自查：扫描文本里的手机号、身份证、银行卡、地址、车牌等敏感信息。

用法：
    python scripts/privacy_scan.py draft.md
    python scripts/privacy_scan.py draft.md --explain
    python scripts/privacy_scan.py draft.md --json
    python scripts/privacy_scan.py draft.md --fail-on high     # 有高危项时退出码 1

退出码：0 无高危（或未指定 --fail-on）；1 触发；2 文件错误。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# (名称, 正则, 档位, 说明, 建议)
# 档位：high=必删 / mid=建议删 / low=看情况
RULES: list[tuple[str, str, str, str, str]] = [
    # ---- 必删 ----
    ("身份证号", r"[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]",
     "high", "可直接用于实名认证与开户", "整段删掉，不要保留任何位数"),
    ("完整手机号", r"(?<!\d)1[3-9]\d{9}(?!\d)",
     "high", "可被用于骚扰、撞库、社工", "删掉或改为「私信我」；确需保留只留后四位"),
    ("银行卡号", r"(?<!\d)(?:62|4\d|5[1-5])\d{14,17}(?!\d)",
     "high", "可直接尝试支付或绑定", "整段删掉"),
    ("车牌号", r"[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-HJ-NP-Z][A-HJ-NP-Z0-9]{5,6}",
     "high", "可定位到车主与活动范围", "整块涂黑"),

    # ---- 建议删 ----
    ("邮箱", r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
     "mid", "可被用于钓鱼与撞库", "替换为「我的邮箱」或打码"),
    ("快递单号", r"(?:SF|YT|ZTO|STO|JD|EMS|YD|JT)\d{10,16}|(?<!\d)\d{12,15}(?!\d)",
     "mid", "可反查收件人手机尾号与大致地址", "整块涂黑"),
    ("详细地址", r"[\u4e00-\u9fa5]{2,6}(?:省|市)[\u4e00-\u9fa5]{0,6}(?:区|县)(?:[\u4e00-\u9fa5]{1,6}(?:路|街|道|巷))?(?:\d{1,5}号)?",
     "mid", "可定位到具体位置", "保留到区，删掉街道与门牌"),
    ("门牌/房号", r"\d{1,4}\s*(?:号楼|栋|单元|室|层|楼)\s*\d{0,4}\s*(?:室|户)?",
     "mid", "结合小区名可精确定位", "删掉房号"),

    # ---- 看情况 ----
    ("微信号", r"(?:微信|weixin|wx|wechat)\s*[:：]?\s*[A-Za-z][A-Za-z0-9_-]{5,19}",
     "low", "公开平台留微信可能违规且被爬", "改为「私信」"),
    ("QQ 号", r"(?:QQ|qq)\s*[:：]?\s*\d{5,11}",
     "low", "同上", "删掉"),
    ("内部域名/IP", r"\b(?:10|172|192)\.\d{1,3}\.\d{1,3}\.\d{1,3}\b|[\w-]+\.(?:internal|corp|local)\b",
     "low", "暴露内网结构，可能被视为安全问题", "打码或改为示例域名"),
    ("工号/学号", r"(?:工号|学号|员工编号|工牌号)\s*[:：]?\s*[A-Za-z0-9]{4,12}",
     "low", "可关联到公司内部身份", "删掉或打码"),
    ("生日（完整）", r"(?:19|20)\d{2}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日",
     "low", "与姓名组合可用于身份验证", "只保留年份或模糊化"),
]

LEVEL_LABEL = {"high": "必删", "mid": "建议删", "low": "看情况"}
LEVEL_ORDER = {"high": 0, "mid": 1, "low": 2}


def mask_value(value: str) -> str:
    """在报告里也不暴露完整值——只留可识别的少量字符。"""
    s = value.strip()
    if len(s) <= 4:
        return s[0] + "*" * (len(s) - 1) if len(s) > 1 else "*"
    return s[:2] + "*" * max(1, len(s) - 4) + s[-2:]


def scan(text: str) -> dict:
    hits = []
    seen: set[tuple[str, int]] = set()
    for name, pattern, level, why, fix in RULES:
        for m in re.finditer(pattern, text, re.I):
            key = (name, m.start())
            if key in seen:
                continue
            seen.add(key)
            line_no = text[: m.start()].count("\n") + 1
            hits.append({
                "type": name,
                "masked": mask_value(m.group(0)),
                "length": len(m.group(0)),
                "line": line_no,
                "level": level,
                "why": why,
                "fix": fix,
            })
    hits.sort(key=lambda h: (LEVEL_ORDER[h["level"]], h["line"]))

    counts = {k: sum(1 for h in hits if h["level"] == k) for k in ("high", "mid", "low")}

    if counts["high"] > 0:
        verdict = "建议不发：有必删项，改完再发"
    elif counts["mid"] > 0:
        verdict = "改完再发：有建议删项"
    elif counts["low"] > 0:
        verdict = "可以发，但看情况项建议模糊化"
    else:
        verdict = "文本层面没扫到敏感信息（截图仍需人工过一遍清单）"

    return {
        "counts": counts,
        "total": len(hits),
        "verdict": verdict,
        "hits": hits,
    }


def render(r: dict, explain: bool) -> str:
    out = []
    c = r["counts"]
    out.append(f"命中 {r['total']} 处：必删 {c['high']} · 建议删 {c['mid']} · 看情况 {c['low']}")
    out.append(f"结论：{r['verdict']}")
    if r["hits"]:
        out.append("")
        for h in r["hits"]:
            out.append(f"  [{LEVEL_LABEL[h['level']]}] {h['type']}  第 {h['line']} 行  "
                       f"{h['masked']}（{h['length']} 字符）")
            if explain:
                out.append(f"       风险：{h['why']}")
                out.append(f"       处理：{h['fix']}")
    out.append("")
    out.append("提示：脚本只能扫文本。截图里还有 10 个地方需要人工看（备注名、群名、"
               "输入框草稿、状态栏、通知横幅、订单号、背景白板、反光、EXIF）。")
    return "\n".join(out)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="发布前隐私自查")
    ap.add_argument("file", help="待发布的文本文件")
    ap.add_argument("--explain", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-on", choices=["high", "mid", "low"], default=None,
                    help="命中该档位及以上时退出码 1")
    args = ap.parse_args(argv)

    p = Path(args.file)
    if not p.is_file():
        print(f"找不到文件：{p}", file=sys.stderr)
        return 2
    text = p.read_text(encoding="utf-8-sig")
    r = scan(text)

    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(render(r, args.explain))

    if args.fail_on:
        c = r["counts"]
        triggered = (
            c["high"] > 0
            or (args.fail_on in ("mid", "low") and c["mid"] > 0)
            or (args.fail_on == "low" and c["low"] > 0)
        )
        if triggered:
            return 1
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main(sys.argv[1:]))
