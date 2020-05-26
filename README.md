# News Crawler

In this repository we create a crawler using Scrapy. With this crawler, we extract articles from the given news sites, based on their subject. From each article, we are insterested in saving its author, context, date of publication and of course the articles text body. The extracted data is being saved in a local database, otherwise it can be stored in a csv file.

## Spiders subject:
_Our crawler has 10 different spiders, one spider for each subject given bellow:_

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
    
## Used websites:
_The following 20 websites are being used to extract our articles:_

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
    - newsit.gr
    - tovima.gr
    - kathimerini.gr
    - naftemporiki.gr
    - lifo.gr
    - newsit.gr
    - topontiki.gr
    - insomnia.gr
    - popaganda.gr

## Structure of the extracted data
_From each article we collect data concerning:_

    - topic
    - subtopic
    - extracted website
    - title
    - date
    - author
    - article text
    - url of the specific article

## Commands to run this project:
_In order to run our spider and save it's extracted data in a csv file do the following:_

```bash
  1. $ pip install -r requirements.txt
  2. $ git clone https://github.com/elenisproject/NewsCrawler 
  3. $ cd NewsCrawler
  4. $ scrapy crawl "spidername" -o out.csv -t csv
```

    - where spidername belongs in {world, environment, economics, politics, greece, sport, style, tech, culture, food}

*In case you want to run the spider without the outpout printed in the terminal run for eachspider the command:*

```bash
  - $ scrapy crawl world -o out.csv -t csv --nolog
```

## Project structure:
_Code File description:_

    - reguirements.txt: Contains Pyhton libraries used for this project.
    - items.py: Spiders fields extracted from each article.
    - middlewares.py : Concerns spiders behavior. In our project, we use this to set custom domain depth per site.
    - pipelines.py: Database credentials and connector.
    - settings.py: Custom settings for controlling our spiders.
    - utilities.py: Functions needed in our project.
    
   
    
