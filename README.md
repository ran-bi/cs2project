## Chicago Wanderlust: A CS122 Project

## Synopsis

The ultimate accommodation finder for leisure travellers to Chicago.

## Code Example
```
python3 manage.py runserver
```

## Motivation



## Installation

**Python packages required:**
- BeautifulSoup
- Django==1.10.5
- django-bootstrap-form==3.2.1
- googlemaps
- numpy
- pandas
- rauth
- shapely
- selenium (with Chrome webdriver)

## Code Structure

**Main funcions under search folder**
- /util/scrapers.py: Airbnb and Booking.com scrapers
- /util/routes.py: attraction and route selection algorithm
- /util/yelp_filter.py: restaurant quality algorithm
- /util/safety_filter.py: filter out locations in dangerous communities
- algorithm.py: consolidated function linked to front-end

**Crime data under Preprocessing folder**
- csv files: raw data
- crimefilter.py: code for crimerate calculation and generate geojson file
- danger_poly.json: output geojeson file for dangerous communities

## Troubleshooting

- **Date Input Error:** Date range must be within 10 days. Ensure check-in date is no later than check-outdate and not a past date.
- **Price Range Error:** Ensure price upper bound is higher than the lower bound.
- **Webdriver Error:** The program requires installation of Chrome Webdriver in PATH.
- **Googlemaps API Error:** Googlemaps API sets limit on total daily query times. We provide a list of available API keys in search/util/APIKeys.txt. Please copy and paste a new API key to search/util/routes.py file.

## Contributors

Ran Bi,
Weijie Xin,
Leping Yu,
Minjia Zhu
@Uchicago Harris, CAPP
