# Uds Grade Scraper
A Selenium Webdriver based scraper that gives you the latest exam of the provided lectures / seminars from the LSF website of the Saarland University. It's important, that you use the exact name from LSF, check your "info on exams" ("Info über angemeldete Prüfungen") page to see the exact name.

## How to use it
### Prerequisites
you need Python 3, the Chrome browser and the following packages:
* selenium
* BeatifulSoup 4

use this command to install it with pip:
```
pip install selenium beautifulsoup4
```
### Running it
you can either run it with:
```
python seleniumScraper.py
```
to enter the interactive mode, or use
```
python seleniumScraper.py -flag1 val1 -flag2 val2 ...
```
Which allows you to call it with a script or other program.
When writing your "desired grades" you need to separate it with "," and write the exact name.

### Arguments
| Argument name |Type               | required|
|---------------|-------------------|---------|
| username     	| string            | YES     |
| password 		| string            | YES     |
| desiredgrades | string[]			| YES     |
| rate   		| int (minutes)		| NO      |