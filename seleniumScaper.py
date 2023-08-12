from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import sys
import time
import math
import datetime

# ---------------------------------------------------------------#
#                   Function definitions                        #
# ---------------------------------------------------------------#


def getInputs_interactive():
    username = input("username:\t\t\t\t\t\t\t")
    password = input("password:\t\t\t\t\t\t\t")
    desiredGrades = input(
        "enter the grades you like to watch as a list (spaces are kept):\t")
    desiredGrades = desiredGrades.split(",")
    pollingRate = input("pollingrate (in minutes):\t\t\t\t\t")
    viewAll = input("should all exams be shown (t/f):\t\t\t\t")

    return {
        "username": username,
        "password": password,
        "desiredgrades": desiredGrades,
        "pollingrate": pollingRate,
        "viewall":viewAll
    }


def getInputs_flags():
    # define the input variable
    inputs = {}

    # check the arguments
    acceptedFlags = ["--username", "--password",
                     "--desiredgrades", "--rate", "--viewall"]
    arguments = sys.argv

    for i in range(len(arguments)):
        arg = arguments[i].lower()

        if acceptedFlags.__contains__(arg.lower()):
            # remove '--'
            arg = arg.replace(arg[0], "", 2)

            # save it
            if (arg == "rate"):
                inputs["pollingrate"] = arguments[i+1]
            elif (arg == "viewall"):
                # transform input to bool
                inputs["viewall"] = arguments[i+1].lower() in ['true', '1', 't', 'y', 'yes']
            else:
                # loop until a new arg is found
                subArgs = ""

                for j in range(i+1, len(arguments)):
                    if arguments[j].__contains__("--"):
                        break
                    subArgs += arguments[j]+" "

                # remove the last space
                inputs[arg] = subArgs[:-1]

            i += 1
    return inputs


def gatherGrades(username, password, desiredGrades, viewAll):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.lsf.uni-saarland.de/qisserver/rds?state=user&type=0")

    # login
    driver.find_element(By.ID, "Benutzerkennung").send_keys(username)
    driver.find_element(By.ID, "pass").send_keys(password)
    driver.find_element(By.ID, "pass").send_keys(Keys.ENTER)

    # navigate to overview page
    driver.find_element(By.LINK_TEXT, 'Prüfungsverwaltung').click()
    driver.find_element(By.LINK_TEXT, 'Notenspiegel').click()

    # select the correct course of study (i.e. the top entry)
    elements = driver.find_elements(By.CLASS_NAME, 'treelist')
    elements[0].find_element(By.TAG_NAME, "a").click()
    driver.find_element(By.XPATH, "//a[contains(@title,'Leistungen')]").click()

    # parse the page
    soup = BeautifulSoup(driver.page_source, 'lxml')
    table = soup.findAll('table')[1]
    rows = table.findAll(lambda tag: tag.name == 'tr')

    entries = {}
    importantEntries = {}

    # select the desired rows
    for row in rows:
        cols = row.findAll(lambda tag: tag.name == 'td')
        if (len(cols) != 8):
            # only actual exams/grades have this lenght, everything else can be pruned
            continue
        if len(cols[7].text.strip()) == 0:
            # no date means, that the row is a (sub-)header row
            continue

        # create an entry from the row
        date = (datetime.datetime.strptime(cols[7].text.strip(), '%d.%m.%Y'))
        name = cols[1].text.strip()
        grade = cols[3].text.strip()

        entry = {"name": name, "date": date, "grade": grade}
        
        # check if any name of the desired grades is found in the row
        if (desiredGrades.__contains__(cols[1].text.strip())):
            if name in importantEntries:
                importantEntries[name].append(entry)
            else:
                importantEntries[name] = [entry] 
        elif(viewAll): 
            if name in entries:
                entries[name].append(entry)
            else:
                entries[name] = [entry] 

    # select the latest entry for the found rows/exams
    def selectLatestEntry(entryList):
        selected = {}
        for propName in entryList:
            for exam_1 in entryList[propName]:
                for exam_2 in entryList[propName]:
                    # get the entry with later date out of the two
                    entry = exam_1 if exam_1["date"] > exam_2["date"] else exam_2

                    if propName not in selected:
                        # check if these are the first
                        selected[propName] = entry
                    else:
                        # not the first -> check if the entry is later than the current one
                        d = selected[propName]
                        selected[propName] = d if d["date"] > entry["date"] else entry
        return selected

    selectedEntries = selectLatestEntry(entries)
    selectedImportantEntries= selectLatestEntry(importantEntries)

    def createTableRow(widths, data):
        numTab = 0
        # first part
        numTab = math.floor((widths[0]-len(data[0])) / 8)
        p1 = data[0] + ("\t" * numTab)

        # second part
        numTab = math.floor((widths[1]-len(data[1])) / 8)+1
        p2 = data[1] + ("\t" * numTab)

        # third part
        numTab = math.floor((widths[2]-len(data[2])) / 8)+1
        p3 = data[2] + ("\t" * numTab)

        print(p1+" "+p2+" "+p3)

    # print table
    screenWidth = 200
    widthName = math.floor((screenWidth-2) * 0.7)
    widthGrade = math.floor((screenWidth-2) * 0.15)
    widthDate = math.floor((screenWidth-2) * 0.15)
    widths = [widthName, widthGrade, widthDate]

    ##  create the spacers
    entrySpacer = ("-"*screenWidth)
    sectionSpacer = ("="*screenWidth)

    ## >print header
    print(sectionSpacer)
    createTableRow(widths, ["Name", "Grade", "Date"])
    print(sectionSpacer)

    ## > important entries on top
    if len(selectedImportantEntries.keys()) >= 1:
        for entryName in selectedImportantEntries:
            createTableRow(widths, [entryName, selectedImportantEntries[entryName]["grade"], selectedImportantEntries[entryName]["date"].strftime('%d.%m.%Y')])
            
            if not(entryName == list(selectedImportantEntries)[-1]):
                print(entrySpacer)

    else:
        print("No exams were found.")
    print(sectionSpacer)

    ## > other entries
    if len(selectedEntries.keys()) >= 1:
        for entryName in selectedEntries:
            createTableRow(widths, [entryName, selectedEntries[entryName]["grade"], selectedEntries[entryName]["date"].strftime('%d.%m.%Y')])
            
            if not(entryName == list(selectedEntries)[-1]):
                print(entrySpacer)

    print(sectionSpacer)

    # shut down
    driver.close()


# ---------------------------------------------------------------#
#                   Main function                               #
# ---------------------------------------------------------------#
# check which input method should be used
inputs = None
if len(sys.argv) > 5:
    inputs = getInputs_flags()
else:
    inputs = getInputs_interactive()

# check if all arguments are set / set the default values
if (len(inputs["username"]) < 3 or len(inputs["password"]) < 3):
    raise Exception("username or password too short")

if (len(inputs["desiredgrades"]) < 1):
    raise Exception("desired grades too short")

if isinstance(inputs["pollingrate"], int) and inputs["pollingrate"] < 60:
    inputs["pollingrate"] = 60
    print("polling rate variable was not defined / too low. It is not set to 60 minutes")
if isinstance(inputs["pollingrate"], str):
    inputs["pollingrate"] = int(inputs["pollingrate"])
    if inputs["pollingrate"] < 60:
        inputs["pollingrate"] = 60
        print(
            "polling rate variable was not defined / too low. It is not set to 60 minutes")

if not isinstance(inputs["viewall"], bool):
    inputs["viewall"] = False

# gather the grade
maxIterationsBeforeStopping = 50
iterations = 0
while iterations < maxIterationsBeforeStopping:
    try:
        timestamp = datetime.datetime.now().strftime('%H:%M - %d.%m.%y')
        print("gather grades (iteration: "+str(iterations)+", time: " +
              timestamp+")")

        gatherGrades(inputs["username"], inputs["password"],
                     inputs["desiredgrades"], inputs["viewall"])

        # notify user
        nextTime = datetime.datetime.now() + \
            datetime.timedelta(minutes=inputs["pollingrate"])
        print("gathering done.\nwaiting until: " +
              nextTime.strftime('%H:%M - %d.%m.%y'))

        # wait
        time.sleep(inputs["pollingrate"] * 60)
        iterations += 1
    except KeyboardInterrupt:
        print("Programm interrupted. Shutting down")
        sys.exit()
