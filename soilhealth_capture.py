from playwright.sync_api import sync_playwright

URL = "https://soilhealth.dac.gov.in/school"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    def handle_request(request):
        print(f"[REQUEST] {request.method} {request.url}")

    def handle_response(response):
        if response.status >= 400:
            print(f"[ERROR] {response.status} {response.url}")

    page.on("request", handle_request)
    page.on("response", handle_response)

    print("Opening Soil Health portal...")
    page.goto(URL, wait_until="domcontentloaded", timeout=120000)

    print("\n========================================")
    print("BROWSER READY")
    print("Navigate/click normally in the browser.")
    print("Every network request will be printed here.")
    print("Press ENTER when finished.")
    print("========================================\n")

    input()

    browser.close()