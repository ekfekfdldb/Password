# app/generator.py
import secrets
import string
from dataclasses import dataclass

AMBIG = set("O0oIl1|")

@dataclass
class GenOptions:
    length: int = 16
    lower: bool = True
    upper: bool = True
    digits: bool = True
    symbols: bool = True
    avoid_ambiguous: bool = True

def generate(opts: GenOptions) -> str:
    pools = []
    if opts.lower:   pools.append(string.ascii_lowercase)
    if opts.upper:   pools.append(string.ascii_uppercase)
    if opts.digits:  pools.append(string.digits)
    if opts.symbols: pools.append("!@#$%^&*()-_=+[]{};:,.?/")

    chars = "".join(pools)
    if not chars:
        raise ValueError("문자군을 하나 이상 선택하세요.")

    if opts.avoid_ambiguous:
        chars = "".join(ch for ch in chars if ch not in AMBIG)

    # 필수군 충족 보장: 각 풀에서 1자씩
    req = []
    for p in pools:
        cands = [c for c in p if (c not in AMBIG) or (not opts.avoid_ambiguous)]
        if cands:
            req.append(secrets.choice(cands))

    # 나머지
    remain = [secrets.choice(chars) for _ in range(max(0, opts.length - len(req)))]
    pw_list = req + remain
    secrets.SystemRandom().shuffle(pw_list)
    return "".join(pw_list)
