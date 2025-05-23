from rich.pretty import pprint      # just to pretty-print
from seleniumbase import Driver

driver = Driver(uc=True, log_cdp=True)  # or uc=False if you don’t need it
try:
    driver.get('https://www.upwork.com/ab/account-security/login')
    # All performance+network log entries are now available:
    pprint(driver.get_log("network"))

    # Or, subscribe live to every CDP event:
    # from pprint import pformat
    # driver.add_cdp_listener("*", lambda evt: print(pformat(evt)))
    # driver.get("https://example.com")
finally:
    driver.quit()
