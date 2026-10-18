# Online Movie Ticket Booking System — PRT582

**Software Group Project | Sydney 1**

This repository contains the Sydney 1 group's work for the PRT582 Software Group Project. The project uses an **Online Movie Ticket Booking System** as the application under test, with supporting materials for requirements, functional testing, performance testing, and security assessment.

## Project scope

The application supports a customer journey involving movie search, viewing movie details and showtimes, selecting seats, registering or signing in, simulated ticket payment, and viewing booking history. The test activities evaluate whether these workflows meet the user stories and acceptance criteria recorded in the project documentation.

**Technology:** Django (Python), MySQL, Docker Compose for local deployment, Robot Framework/SeleniumLibrary for browser-based functional tests, Locust for load testing, and OWASP ZAP for security analysis.

> **Important:** Payment is simulated in the supplied application; it is not a real card-payment gateway. All testing should be carried out on a local or otherwise authorised test instance.

## Repository structure

The following folders and files are visible in the repository. Contents may evolve as the group adds evidence.

```text
.
├── Functional Testing/
│   ├── functional.robot
│   ├── README.ME
│   └── results/
│       ├── report.html
│       ├── log.html
│       ├── output.xml
│       └── selenium-screenshot-*.png
├── Performance Testing/
│   ├── locustfile.py
│   ├── check_login.py
│   ├── run_all_tests.py
│   ├── security_checks.py
│   ├── summarize_results.py
│   ├── README
│   └── results/
├── README.md
└── [application source/archive and other project materials]
```

Check the repository folders for the latest test files and output. The application source may be provided as a separate archive; do not assume it is executable from the repository root.

## Local application setup

If you have the Django application source containing `docker-compose.yml`, use the following workflow from **that application's directory**:

```powershell
docker compose up --build -d
docker compose ps
```

Open **http://localhost:8000/** in your browser after the containers are healthy. To stop the environment:

```powershell
docker compose down
```

The configuration used in the group's local work relies on Docker and a MySQL service. Consult the application's own `README.md`, `docker-compose.yml`, and environment configuration for prerequisites, ports, database setup, and test accounts. Do not commit actual credentials or production secrets.

## Functional testing — Robot Framework

Browser-based acceptance tests cover customer-facing activities such as movie searching, showtime discovery, registration, seat booking, and booking history. Some negative tests are intended to reveal known issues rather than pass.

Install the dependencies:

```powershell
python -m pip install robotframework robotframework-seleniumlibrary
```

From the **repository root**, run the checked-in Robot Framework suite:

```powershell
python -m robot --outputdir "Functional Testing/results" "Functional Testing/functional.robot"
```

Review `Functional Testing/results/report.html` and `log.html` for results, step details, and screenshots. Confirm browser-driver compatibility and any test-account variables required by the suite before execution. **Do not report skipped tests as passed.**

### Form C acceptance scenarios

The team's Form C cases cover: valid and invalid movie search (TC01–TC02), showtime availability (TC03–TC04), seat selection and duplicate-seat prevention (TC05–TC06), registration and validation (TC07–TC09), simulated payment and multi-seat bookings (TC10–TC12), and authenticated/unauthenticated booking history (TC13–TC14). Not all cases are necessarily automated in the checked-in `functional.robot`; see the test file and its generated report for exact coverage.

## Performance testing — Locust

The `Performance Testing` folder includes a Locust script and supporting helper scripts. The goal is to compare response times, throughput, and failure rates under different simulated workloads.

Install Locust:

```powershell
python -m pip install locust
```

To run the checked-in script against a **running local instance**:

```powershell
python -m locust -f "Performance Testing/locustfile.py" --host http://localhost:8000
```

Open **http://localhost:8089/** to set the user count and ramp-up rate. For a reproducible headless baseline with saved evidence:

```powershell
python -m locust -f "Performance Testing/locustfile.py" --headless -u 1 -r 1 -t 1m --host http://localhost:8000 --html "Performance Testing/results/baseline.html" --csv "Performance Testing/results/baseline"
```

Make sure `Performance Testing/results/` exists before saving new files. Workloads previously explored in the group's testing included 1, 10, 25, 50, and 100 simulated users. Exact results depend on the test script, duration, machine, and configuration; consult the saved reports rather than assuming a fixed performance outcome. Higher loads can degrade or disrupt a local Django development server.

## Security testing

Security evaluation includes manually checked behaviour and web-response inspection with **OWASP ZAP**. Areas investigated include registration/password validation, access to booking history while logged out, HTTP security headers, cookie configuration, and outdated client-side libraries.

To repeat passive inspection safely:

1. Start the authorised local application at `http://localhost:8000/`.
2. Open OWASP ZAP and choose **Quick Start → Manual Explore**.
3. Launch a browser configured through ZAP and navigate the application.
4. Review the **Alerts** panel and inspect evidence for the **local application host**.
5. Export an HTML report and save the relevant evidence in the project results folder.

An alert is a potential issue, not proof of exploitation. If ZAP also captures unrelated browser-service traffic, filter the report to the local target before counting application findings. Avoid active scanning systems you do not own or have permission to test.

## Interpreting test evidence

Keep test scripts and outcomes together. For each run, record the test date, environment, scenario, prerequisites, expected result, actual result, and status (`PASS`, `FAIL`, `SKIP`, or `NOT APPLICABLE`). Screenshots and HTML/CSV reports support the written results but do not replace them.

Observed issues during project testing included weak-password acceptance and inappropriate unauthenticated booking-history handling. These should be documented as findings and verified again after any code change. A passing automated script only confirms the assertions present in that script.

## Group members

| Member | Student ID |
|---|---|
| Jordan Then Ryan | S405349 |
| Saugat Shrestha | S403036 |
| Suleman Uddin Farhad Syed | S403360 |
| Ujjwol Neupane | S403295 |

## Academic use

Prepared for the **PRT582 Software Group Project — Sydney 1**. This repository is intended for coursework, demonstration, and authorised testing. It is not a production-ready movie ticketing service.
