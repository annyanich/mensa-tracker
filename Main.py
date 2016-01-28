# I'm going to just doodle around in here and see what I can get working.
from bs4 import BeautifulSoup

testFilename = "test menu pages/uhlhornsweg-ausgabe-a.php"
testFile = open(testFilename)
soup = BeautifulSoup(testFile, 'html.parser', from_encoding="utf-8")

print(soup.prettify())