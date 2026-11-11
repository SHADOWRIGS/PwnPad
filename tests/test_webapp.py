#!/usr/bin/env python3
"""Integration tests for the PwnPad webapp using Playwright."""

import subprocess
import time
import sys


def run_tests():
    server = subprocess.Popen(
        ["python3", "-m", "http.server", "-b", "127.0.0.1", "12531"],
        cwd="tools/webapp",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
            page = browser.new_page()
            page.goto("http://127.0.0.1:12531/index.html")

            title = page.title()
            assert title == "PwnPad", f"FAIL: title is '{title}', expected 'PwnPad'"
            print("PASS: page title is correct")

            options = page.locator("#challenge option").all()
            assert len(options) == 15, f"FAIL: expected 15 challenges, got {len(options)}"
            print("PASS: all 15 challenges in dropdown")

            expected_names = [
                "Serial Snitch", "Echo Chamber", "Bus Whisperer",
                "Invisible Wires", "Code Heist", "Hard Leak",
                "Power Trip", "Glitch Storm", "Clock Spy",
                "Tempo Leak", "Chaos Chain - Glitchgate",
                "Chaos Chain - Timebomb", "Pizza Order",
                "Ladybirds", "Ladybird I Am Your Father",
            ]
            for i, opt in enumerate(options):
                text = opt.text_content()
                assert text == expected_names[i], \
                    f"FAIL: option {i} is '{text}', expected '{expected_names[i]}'"
            print("PASS: all challenge names correct")

            expected_values = [f"chal{i}" for i in range(1, 16)]
            for i, opt in enumerate(options):
                val = opt.get_attribute("value")
                assert val == expected_values[i], \
                    f"FAIL: option {i} value is '{val}', expected '{expected_values[i]}'"
            print("PASS: all challenge values correct")

            flag_input = page.locator("#flag")
            assert flag_input.is_visible(), "FAIL: flag input not visible"
            print("PASS: flag input is visible")

            submit_btn = page.locator("button")
            assert submit_btn.is_visible(), "FAIL: submit button not visible"
            assert "Submit" in submit_btn.text_content(), "FAIL: submit button text wrong"
            print("PASS: submit button is visible with correct text")

            result_div = page.locator("#result")
            assert result_div.text_content() == "", "FAIL: result div should be empty initially"
            print("PASS: result div empty on load")

            has_crypto = page.evaluate("typeof CryptoJS !== 'undefined'")
            if has_crypto:
                page.select_option("#challenge", "chal1")
                page.fill("#flag", "TS{U@rt_15_@w3s0m3}")
                page.click("button")
                page.wait_for_timeout(500)
                result = page.locator("#result").text_content()
                assert "Correct" in result, f"FAIL: expected correct, got '{result}'"
                print("PASS: correct flag accepted for chal1")

                page.select_option("#challenge", "chal2")
                page.fill("#flag", "WRONG_FLAG")
                page.click("button")
                page.wait_for_timeout(500)
                result = page.locator("#result").text_content()
                assert "Wrong" in result, f"FAIL: expected wrong, got '{result}'"
                print("PASS: wrong flag rejected for chal2")
            else:
                print("SKIP: CryptoJS not loaded (CDN unavailable), flag submission tests skipped")

            page.select_option("#challenge", "chal2")
            assert page.locator("#result").text_content() == "", "FAIL: result not reset on challenge switch"
            print("PASS: result resets on challenge switch")

            browser.close()
            print("\nAll webapp tests passed")
            return True

    except Exception as e:
        print(f"FAIL: {e}")
        return False
    finally:
        server.terminate()
        server.wait()


if __name__ == "__main__":
    sys.exit(0 if run_tests() else 1)
