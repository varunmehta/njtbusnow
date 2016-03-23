#NJ Transit MyBusNow.

Simple python script that parses the mybusnow HTML page, and captures the info to elasticsearch. 
The idea is to identify which is the best bus to catch in the morning when you are getting late for work. Will try plotting this data for 3-6 months and see if I can draw a pattern and generate any useful info from it. 
  
Thinking to add more reference points, where I can add PABT bus alerts or traffic alerts for the route I'm checking. 
  
As of now the code is very specific to my bus and my bus's route, if you are interested, then you can fork and modify for your buses. 
  
The code is run on RaspberryPi (Model B - 512MB), as part of a cron job.   

## Installation

Since we want things to be fast, we use lxml as the html parser

``` 
 $ pip install beautifulsoup4
 $ pip install lxml
 $ pip install elasticsearch
```

You have to install Elasticsearch on your local n/w and persist data to that.


## TODO 

Convert this script to AWS Kinesis & DynamoDB. 