# cam-finder
find ACTi NVR3.0 cameras with default login details ( admin / 123456 )


[![asciicast](https://asciinema.org/a/ULdpcD5683dJ8KECua9B6Hwrn.svg)](https://asciinema.org/a/ULdpcD5683dJ8KECua9B6Hwrn)


The program will lookup devices using either [shodan](https://www.shodan.io) or [censys](https://search.censys.io/). It will then try the default login details for the system. Once completed, it saves a ``.csv`` file containing the following information: 

``ip, port, status code, camera count, source, city, country, country code, longitude and latitude``. 

Some of this information will be provided by either shodan or censys so it may not be 100% accurate.


```shell
# install requirements
pip install -r requirements.txt

# rename example config
mv config-example.py config.py

# configure shodan api key and / or censys api token

# run program
python main.py
```
