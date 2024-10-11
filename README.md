# C2-change-detector

This script is made for detecting content changes on course sites on the C2 platform of ETF UNSA.

The script is based on the Selenium WebDriver module for Python and made to run on Microsoft Edge.

Instructions:

0) Install [Python3](https://www.python.org/downloads/) and [Selenium](https://selenium-python.readthedocs.io/installation.html) module.
1) Create auth.txt file and write C2 username in first row and password in second row.
2) In the c2_sites.txt file, pase the URL's to your course pages.
3) Run the change_detector.py script once to save the baseline page contents.
4) Run the change_detector.py script every time you want to check if changes were made.

**The script currently outputs the ID's of courses where a change in content is detected.**
