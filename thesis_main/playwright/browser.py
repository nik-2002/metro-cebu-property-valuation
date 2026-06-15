import os
import random
import time
import argparse
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from bs4 import BeautifulSoup

DELAY_RANGE = (4.0, 8.0)

# Two different blocks, handled differently:
#  - DataDome JS challenge ("window.gokuProps") auto-resolves in a real browser, so a
#    reload clears it.
#  - The interactive human-verification / CAPTCHA page does NOT auto-resolve. Reloading it
#    only resets the challenge into an infinite loop, so a human must solve it by hand in the
#    visible browser window while the scraper waits.
CAPTCHA_MARKERS = [
    "captcha-delivery",
    "geo.captcha-delivery",
    "verify you are a human",
    "verify you are human",
    "are you a human",
    "please verify you",
    "human verification",
    "i am human",
]
# How long to wait for a human to clear the verification before giving up (seconds), and how
# often to re-check the page in the meantime.
MANUAL_VERIFY_TIMEOUT = 600
MANUAL_VERIFY_POLL = 5

class LamudiBrowser:
    def __init__(self, headless=False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def __enter__(self):
        print(f"Starting Playwright Chromium (headless={self.headless})...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        
        # Desktop Chrome User Agent
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        self.context = self.browser.new_context(
            viewport={"width": 1366, "height": 768},
            locale="en-US",
            timezone_id="Asia/Manila",
            user_agent=user_agent
        )
        self.page = self.context.new_page()
        
        # Apply stealth
        try:
            stealth = Stealth()
            stealth.apply_stealth_sync(self.page)
            print("playwright-stealth applied successfully.")
        except Exception as e:
            print(f"Warning: Failed to apply playwright-stealth ({e}). Using manual fallback injection.")
            # Fallback manual injection script
            fallback_script = """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            """
            try:
                self.page.add_init_script(fallback_script)
                print("Manual fallback stealth injection applied.")
            except Exception as fe:
                print(f"Error applying fallback script: {fe}")
                
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing browser context...")
        if hasattr(self, 'page') and self.page:
            try:
                self.page.close()
            except Exception:
                pass
        if hasattr(self, 'context') and self.context:
            try:
                self.context.close()
            except Exception:
                pass
        if hasattr(self, 'browser') and self.browser:
            try:
                self.browser.close()
            except Exception:
                pass
        if hasattr(self, 'playwright') and self.playwright:
            try:
                self.playwright.stop()
            except Exception:
                pass

    def _is_captcha(self, content):
        low = content.lower()
        return any(marker in low for marker in CAPTCHA_MARKERS)

    def _await_manual_verification(self, url):
        # Interactive CAPTCHA: a human must solve it in the visible browser window.
        # Critically, do NOT reload here — reloading resets the challenge and loops forever.
        if self.headless:
            raise RuntimeError(
                f"Human verification page hit for {url} while running headless. "
                "Re-run WITHOUT --headless so the CAPTCHA can be solved manually."
            )
        print("\a")  # terminal bell to grab attention
        print("=" * 72)
        print("  >>> HUMAN VERIFICATION REQUIRED <<<")
        print(f"  URL: {url}")
        print("  Switch to the Chromium window, solve the verification, and click Continue.")
        print("  The scraper will detect it cleared and resume automatically — do not close")
        print("  the browser window.")
        print(f"  (waiting up to {MANUAL_VERIFY_TIMEOUT}s, re-checking every {MANUAL_VERIFY_POLL}s)")
        print("=" * 72)
        waited = 0
        while waited < MANUAL_VERIFY_TIMEOUT:
            self.page.wait_for_timeout(MANUAL_VERIFY_POLL * 1000)
            waited += MANUAL_VERIFY_POLL
            content = self.page.content()
            if not self._is_captcha(content) and "window.gokuProps" not in content:
                print(f"  [OK] Verification cleared after ~{waited}s. Resuming scrape.")
                return content
        raise RuntimeError(
            f"Human verification not solved within {MANUAL_VERIFY_TIMEOUT}s for {url}"
        )

    def _handle_waf(self, url, max_reload=3):
        content = self.page.content()
        reloads = 0
        while True:
            # 1) Interactive CAPTCHA — pause for a human, never reload.
            if self._is_captcha(content):
                content = self._await_manual_verification(url)
                continue
            # 2) DataDome JS challenge — auto-resolves; reload a few times.
            if "window.gokuProps" in content:
                if reloads >= max_reload:
                    raise RuntimeError(f"WAF challenge persisted for {url}")
                reloads += 1
                wait_time = random.uniform(5.0, 10.0)
                print(
                    f"[WAF] JS challenge for {url}. Reload {reloads}/{max_reload}, "
                    f"waiting {wait_time:.1f}s..."
                )
                self.page.wait_for_timeout(int(wait_time * 1000))
                self.page.reload(wait_until="domcontentloaded")
                content = self.page.content()
                continue
            # 3) Clean page.
            return content

    def warm_up(self):
        print("Warming up browser on https://www.lamudi.com.ph/...")
        self.page.goto("https://www.lamudi.com.ph/", wait_until="networkidle")
        self._handle_waf("https://www.lamudi.com.ph/")
        try:
            # Best-effort cookie consent dismissal
            self.page.click("text=/Accept|I accept|Agree|Got it/i", timeout=3000)
            print("Cookie/consent banner dismissed.")
        except Exception:
            pass

    def fetch(self, url) -> str:
        delay = random.uniform(DELAY_RANGE[0], DELAY_RANGE[1])
        print(f"Pacing: sleeping for {delay:.2f}s before navigating to {url}...")
        time.sleep(delay)
        self.page.goto(url, wait_until="domcontentloaded")
        return self._handle_waf(url)

    def screenshot(self, url, path) -> str:
        delay = random.uniform(DELAY_RANGE[0], DELAY_RANGE[1])
        print(f"Pacing: sleeping for {delay:.2f}s before navigating to {url} for screenshot...")
        time.sleep(delay)
        self.page.goto(url, wait_until="domcontentloaded")
        self._handle_waf(url)
        
        # Ensure parent directory exists
        abs_path = os.path.abspath(path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        
        self.page.screenshot(path=abs_path, full_page=True)
        print(f"Screenshot successfully saved to {abs_path}")
        return abs_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lamudi Playwright Browser tool")
    parser.add_argument("--url", required=True, help="URL to navigate to")
    parser.add_argument("--screenshot", help="Optional path to save screenshot")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    args = parser.parse_args()
    
    with LamudiBrowser(headless=args.headless) as b:
        b.warm_up()
        
        # Fetch the URL
        html = b.fetch(args.url)
        content = b.page.content()
        goku_present = "window.gokuProps" in content
        
        # Count /property/ links
        soup = BeautifulSoup(content, "html.parser")
        property_links = set()
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            if "/property/" in href or href.endswith(".html"):
                property_links.add(href)
                
        print(f"gokuProps present: {goku_present}")
        print(f"Property links count: {len(property_links)}")
        
        if args.screenshot:
            sc_path = args.screenshot
            if not os.path.isabs(sc_path) and not sc_path.startswith("screenshots/"):
                sc_path = os.path.join("screenshots", sc_path)
            # Take screenshot using the current page state to avoid navigating again
            abs_path = os.path.abspath(sc_path)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            b.page.screenshot(path=abs_path, full_page=True)
            print(f"Screenshot saved to {abs_path}")
