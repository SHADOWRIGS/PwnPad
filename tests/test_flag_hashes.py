#!/usr/bin/env python3
"""Verify that MD5 hashes in the webapp match the actual flags from firmware."""

import hashlib
import re
import sys

KNOWN_FLAGS = {
    "chal1": "TS{U@rt_15_@w3s0m3}",
    "chal2": "TS{N0w_Y0u_@r3_@n_el173_H@(k3r}",
    "chal5": "TS{F1rmw@re_S3cret}",
    "chal7": "TS{Gl1th3s_@r3_Awe50m3_!}",
    "chal8": "TS{0h_n0_y0u_foun6_my_7r1gg3r}",
    "chal9": "TS{Y0u_3nter36_th3_v@ul7}",
    "chal10": "TS{D@mn_y0u_@r3_g006}",
    "chal11": "TS{L0gin_Succ355fu1_!}",
    "chal12": "TS{D0n7_M355_w17h_t1m3}",
    "chal13": "TS{5P@_ar3_H4rd_Bu7_r3w0rd1n9}",
    "chal14": "TS{5WD_15_P0werFu11_Use}",
    "chal15": "TS{JT@G_5@YS_SWD_1m_Y0ur_F@7h3r}",
}

EEPROM_VALUES = [84, 83, 123, 51, 51, 80, 82, 48, 77, 95, 105, 53, 95, 102, 117, 110, 95, 33, 125]
KNOWN_FLAGS["chal6"] = "".join(chr(v) for v in EEPROM_VALUES)


def load_webapp_hashes(path):
    with open(path, "r") as f:
        content = f.read()
    hashes = {}
    for m in re.finditer(r'"(chal\d+)":\s*"([a-f0-9]{32})"', content):
        hashes[m.group(1)] = m.group(2)
    return hashes


def test_flag_hashes():
    webapp_hashes = load_webapp_hashes("tools/webapp/index.html")
    passed = 0
    failed = 0

    for chal_id, flag in sorted(KNOWN_FLAGS.items()):
        expected_hash = hashlib.md5(flag.encode()).hexdigest()
        webapp_hash = webapp_hashes.get(chal_id)

        if webapp_hash is None:
            print(f"SKIP {chal_id}: not found in webapp")
            continue

        if expected_hash == webapp_hash:
            print(f"PASS {chal_id}: hash matches")
            passed += 1
        else:
            print(f"FAIL {chal_id}: expected {expected_hash}, got {webapp_hash}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    return failed == 0


def test_all_challenges_have_hashes():
    webapp_hashes = load_webapp_hashes("tools/webapp/index.html")
    expected = {f"chal{i}" for i in range(1, 16)}
    actual = set(webapp_hashes.keys())
    missing = expected - actual
    if missing:
        print(f"FAIL: webapp missing hashes for: {sorted(missing)}")
        return False
    print(f"PASS: all 15 challenge hashes present in webapp")
    return True


def test_eeprom_flag():
    flag = "".join(chr(v) for v in EEPROM_VALUES)
    if not flag.startswith("TS{") or not flag.endswith("}"):
        print(f"FAIL: EEPROM flag format invalid: {flag}")
        return False
    print(f"PASS: EEPROM flag format valid: {flag}")
    return True


def test_challenge_selector_coverage():
    with open("firmware/src/main/PwnPad/PwnPad.ino", "r") as f:
        content = f.read()
    cases = set(int(m.group(1)) for m in re.finditer(r"case\s+(\d+):", content))
    expected_cases = {1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 16, 17, 18, 19, 20}
    missing = expected_cases - cases
    extra = cases - expected_cases
    ok = True
    if missing:
        print(f"FAIL: missing switch cases: {sorted(missing)}")
        ok = False
    if extra:
        print(f"WARN: unexpected switch cases: {sorted(extra)}")
    if ok:
        print(f"PASS: all expected switch cases present")
    return ok


if __name__ == "__main__":
    results = []
    results.append(test_flag_hashes())
    results.append(test_all_challenges_have_hashes())
    results.append(test_eeprom_flag())
    results.append(test_challenge_selector_coverage())
    sys.exit(0 if all(results) else 1)
