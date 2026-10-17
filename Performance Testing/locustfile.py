"""
Locust load test - Online Movie Booking System (Django)
Form E - Performance Testing

SETUP
    pip install locust
    python manage.py runserver 8000          # app must be running first

BEFORE RUNNING - edit the TODO lines below so they match your app:
    * URL paths  (open the app, copy the real paths from the browser address bar)
    * Form field names (browser DevTools > Network > the login request > Payload)
    * A real test account (register one in the app first)

RUN (headless, writes CSV + HTML report you can paste into Form E)
    locust -f locustfile.py --host http://127.0.0.1:8000 --headless -u 1  -r 1  -t 2m --csv results/baseline --html results/baseline.html
    locust -f locustfile.py --host http://127.0.0.1:8000 --headless -u 10 -r 2  -t 3m --csv results/load10   --html results/load10.html
    locust -f locustfile.py --host http://127.0.0.1:8000 --headless -u 25 -r 5  -t 3m --csv results/load25   --html results/load25.html
    locust -f locustfile.py --host http://127.0.0.1:8000 --headless -u 50 -r 10 -t 3m --csv results/load50   --html results/load50.html
    locust -f locustfile.py --host http://127.0.0.1:8000 --headless -u 100 -r 20 -t 3m --csv results/stress100 --html results/stress100.html
    (-u = concurrent users, -r = users started per second, -t = run time)
"""
import random

from locust import HttpUser, task, between

# ---- TODO: adjust these to match your project ------------------------------
LOGIN_PATH = "/login/"            # TODO: real login URL
SEARCH_PATH = "/search/"          # TODO: real search URL (or the form action)
SEARCH_PARAM = "q"                # TODO: name of the search input field
SHOWTIMES_PATH = "/"              # TODO: page that lists movies/showtimes
MY_BOOKINGS_PATH = "/booking/"   # TODO: real "My Bookings" URL
LOGIN_FIELDS = {                  # TODO: real field names from the login form
    "email": "ujjwolneupane75@gmail.com",
    "password": "Nep@l143",
}
SEARCH_TERMS = ["Venom", "Action", "Comedy", "Drama", "Nonexistent123"]
# -----------------------------------------------------------------------------


class MovieCustomer(HttpUser):
    wait_time = between(1, 3)  # think time between actions, like a real user

    def on_start(self):
        """Log in once per simulated user (Django needs the CSRF token)."""
        self.client.get(LOGIN_PATH, name="GET login page")
        token = self.client.cookies.get("csrftoken", "")
        data = dict(LOGIN_FIELDS)
        data["csrfmiddlewaretoken"] = token
        self.client.post(
            LOGIN_PATH,
            data=data,
            headers={"Referer": self.host + LOGIN_PATH},
            name="POST login",
        )

    @task(4)
    def view_home(self):
        self.client.get(SHOWTIMES_PATH, name="GET home / movie list")

    @task(3)
    def search_movie(self):
        term = random.choice(SEARCH_TERMS)
        self.client.get(SEARCH_PATH, params={SEARCH_PARAM: term}, name="GET search")

    @task(2)
    def view_my_bookings(self):
        self.client.get(MY_BOOKINGS_PATH, name="GET my bookings")
