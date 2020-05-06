# News Crawler

In this repository we create a crawler using scrapy.
Our crawler has 10 different spiders, one spider for every subject given bellow:

``` bash

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

``` bash

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
  - naftemporiki.gr
  - lifo.gr
```

From each article we collect data concerning:

``` bash

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
  1. $ pip install scrapy
  2. $ scrapy startproject news2
  3. $ cd news2
  4. $ rm -r news2
  5. $ git clone https://github.com/elenisproject/NewsCrawler news2
  6. $ scrapy crawl "spidername" -o out.csv -t csv
    - where spidername belongs in {world, environment, economics, politics, greece, sport, style, tech, culture, food}
```

*In case you want to run the spider without the outpout printed in the terminal run for eachspider the command:* __
$ scrapy crawl world -o out.csv -t csv --nolog
