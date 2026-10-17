import re
import requests

BASE = "http://127.0.0.1:8000"
LOGIN = "/login/"            # change if your login page address is different
USER = "loadtest@example.com"  # use the same values as in locustfile.py
PASS = "TestPass123"

s = requests.Session()
page = s.get(BASE + LOGIN)
print("Login page status:", page.status_code, "->", page.url)
print("Form field names found:", re.findall(r'name="([^"]+)"', page.text))

token = s.cookies.get("csrftoken", "")
for user_field in ("email", "username"):
    r = s.post(BASE + LOGIN,
               data={user_field: USER, "Nep@l143": PASS, "ujjwolneupane75@gmail.com": token},
               headers={"Referer": BASE + LOGIN}, allow_redirects=True)
    b = s.get(BASE + "/booking/")
    print(f"Tried field '{user_field}': login status {r.status_code}, "
          f"landed on {r.url}, My Bookings status {b.status_code}")