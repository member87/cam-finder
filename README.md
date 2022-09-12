# cam-finder
Find [ACTi NVR3.0](https://www.acti.com/product/NVR%203%20Enterprise) IP cameras with the default login details ( admin / 123456 )



---

[![asciicast](https://asciinema.org/a/505401.svg)](https://asciinema.org/a/505401)


The program will lookup devices using either [shodan](https://www.shodan.io), [censys](https://search.censys.io/) or [netlas](https://netlas.io/). It will then try the default login details for the system. Once completed, it saves a ``.csv`` file containing the following information: 


``ip, port, status code, camera count, source, city, country, country code, longitude and latitude``. 

Some of this information will be provided by the search provider so it may not be 100% accurate.


## How to setup search providers:
You are not required to set each search provider up however, having more enabled may allow you to find more devices.
- **censys**: https://censys-python.readthedocs.io/en/stable/quick-start.html
- **shodan**:
  - create account (https://account.shodan.io/)
  - copy API Key from account overview and place in config file
- **netlas**:
  - create account (https://app.netlas.io/registration/)
  - copy API Key from [here](https://app.netlas.io/profile) and place in config file

## Installation

```shell
git clone https://github.com/member87/cam-finder/
cd cam-finder

# install requirements
pip install -r requirements.txt

# rename example config
mv config-example.py config.py

# run program
python main.py
```

## Demo
View [cam-finder-web](https://github.com/member87/cam-finder-web) for web UI

View [cam-finder.member87.uk](https://cam-finder.member87.uk) for cam-finder-web demo

## Default credentials
| Username      | Password |
| -----------   | ----------- |
| admin         | 123456       |

## Issues
If you have any problems feel free to create an issue!
