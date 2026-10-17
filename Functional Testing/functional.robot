*** Settings ***
Library           SeleniumLibrary
Library           DateTime
Suite Setup       Open Browser    ${BASE}    ${BROWSER}
Suite Teardown    Close All Browsers
Test Teardown     Run Keyword If Test Failed    Capture Page Screenshot

*** Variables ***
# Edit these to match your site (press F12 on the page to find the names).
${BROWSER}          edge
${BASE}             http://127.0.0.1:8000
${LOGIN_URL}        ${BASE}/login/
${REGISTER_URL}     ${BASE}/register/
${BOOKINGS_URL}     ${BASE}/bookings/
${MOVIE}            Name of a movie in your data
${USER}             testuser
${PASS}             YourTestPassword
${WEAK_PASS}        jack
${SEARCH_FIELD}     name:q
${USER_FIELD}       name:username
${PASS_FIELD}       name:password
${PASS2_FIELD}      name:password2
${LOGIN_BTN}        css:button[type=submit]
${REGISTER_BTN}     css:button[type=submit]
${LOGOUT_LINK}      link:Logout

*** Test Cases ***
F1 View Movie List
    Go To    ${BASE}
    Page Should Contain    ${MOVIE}

F2 Search For Existing Movie
    Go To    ${BASE}
    Input Text    ${SEARCH_FIELD}    ${MOVIE}
    Press Keys    ${SEARCH_FIELD}    RETURN
    Page Should Contain    ${MOVIE}

F3 Search With No Match
    Go To    ${BASE}
    Input Text    ${SEARCH_FIELD}    zzzz no such movie zzzz
    Press Keys    ${SEARCH_FIELD}    RETURN
    Page Should Not Contain    ${MOVIE}
    Page Should Not Contain    Server Error

F4 Weak Password Is Rejected
    [Documentation]    Expected to FAIL: the site accepts weak passwords (SEC-01).
    ${stamp}=    Get Current Date    result_format=%H%M%S
    Go To    ${REGISTER_URL}
    Input Text        ${USER_FIELD}     weakuser${stamp}
    Input Password    ${PASS_FIELD}     ${WEAK_PASS}
    Input Password    ${PASS2_FIELD}    ${WEAK_PASS}
    Click Button      ${REGISTER_BTN}
    Location Should Contain    register

F5 Logout Removes Access
    Go To    ${LOGIN_URL}
    Input Text        ${USER_FIELD}    ${USER}
    Input Password    ${PASS_FIELD}    ${PASS}
    Click Button      ${LOGIN_BTN}
    Click Link        ${LOGOUT_LINK}
    Go To    ${BOOKINGS_URL}
    Page Should Not Contain Link    ${LOGOUT_LINK}
