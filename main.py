import sys
import svn.local
import datetime
import subprocess
import csv

def get_commits_by_author(repo, datefrom, author=''):
    revisions = []
    client = svn.local.LocalClient(repo)
    for commit in client.log_default(timestamp_from_dt=datefrom, use_merge_history=True):
        if author in commit.author:
            revisions.append(commit.revision)
    return revisions

def writeToCsv(csvFilePath, csvRowList, defHeader):
    with open(csvFilePath, "w", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        print("Total length: %i" % len(csvRowList))
        writer.writerow(defHeader)
        for item in csvRowList:
            writer.writerow(item)

def orderBy(e):
    return e[0]

paramAuthor = sys.argv[1]
dateSplit = sys.argv[2].split('-')
paramFrom = datetime.datetime(int(dateSplit[0]), int(dateSplit[1]), int(dateSplit[2])) # year month day
paramRepo = sys.argv[3]

listOfRevisionsByAuthor = []
listOfRevisionsByAuthor = get_commits_by_author(paramRepo, paramFrom, paramAuthor)
listOfRevisionsByAuthor.sort()
mapOfFileChanged = {}

for rev in listOfRevisionsByAuthor:
    strCmd = 'svn log -v -r ' + str(rev) + ' ' + paramRepo
    print(strCmd)
    result = subprocess.run(strCmd, stderr=subprocess.DEVNULL, stdout=subprocess.PIPE, universal_newlines=True)
    isStartRead = False
    for line in str(result.stdout).splitlines():
        if isStartRead:
            if line != "" and "." in line:
                line = line.strip()
                arrOut = line.split(' ')
                key = arrOut[1]
                mapOfFileChanged[key] = rev
        if 'Changed paths:' in line:
            isStartRead = True
        if not line:
            isStartRead = False
header = ['CODE','REVISION']
defMapOfResult = []
for fileChanged in mapOfFileChanged:
    row = fileChanged , mapOfFileChanged[fileChanged]
    defMapOfResult.append(row)
defMapOfResult.sort(key=orderBy)
writeToCsv('svnCommit.csv', defMapOfResult, header)