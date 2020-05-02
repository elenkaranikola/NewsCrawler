# News Crawler
In this repository we create a crawler using scrapy.
Our crawler has 10 different spiders, one spider for every subject given bellow:
```
  1. Greece
  2. World
  3. Economics
  4. Culture
  5. Politics
  6. Sport
  7. Technology
  8. Environment
  9. Style
  10. Food
```
We use our spiders to extract articles from 20 different greek website. So far we have extracted articles from here:
```
  - cnn.gr
  - reader.gr
  - thetoc.gr
  - protagon.gr
  - periodista.gr
  - in.gr
  - newpost.gr
  - gazzetta.gr
  - sport24.gr
  - tanea.gr
  - iefimerida.gr
  - thepressproject.gr
  - tovima.gr
  - kathimerini.gr
```
From each article we collect data concerning:
```
  - subtopic
  - extracted website
  - title
  - date
  - author
  - text
  - url of the specific article
```
In order to run our spider and save it's extracted data in a csv file do the following:
```
1.Install it's requirements from requirements.txt
2.Run -- scrapy startproject news2
3.Clone this project localy
4.Run -- scrapy crawl spidername -o out.csv -t csv
```

