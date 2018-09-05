# bme680_outputs

## pretty_BSEC.sh

This script checks a CSV of
[BSEC](https://www.bosch-sensortec.com/bst/products/all_products/bsec)
data from the
[BME680 sensor](https://www.bosch-sensortec.com/en/bst/products/all_products/bme680)
periodically for some significant change and gives feedback in form of a
sentence, which can be useful for automatic notifications.

### Example

Average air 🙂 [92 IAQ], but it's cold ❄ [19.0 °C].

![Twitter notification](https://github.com/alexh-name/bme680_outputs/raw/master/images/twitter_notification.jpg "Twitter notification")

### Dependencies

* bc for float operations
* sh that has integer indexed arrays

### CSV format

Expected CSV format:
`date,IAQ accuracy,IAQ index,temperature,humidity,pressure,gas,BSEC status`

e.g:
`2018-01-04 20:21:10,3,70.92,21.05,46.53,988.64,749721,0`

You can find an example for fitting output code for
[bsec_bme680_linux](https://github.com/alexh-name/bsec_bme680_linux)
in the header of the file.

## LED_bars_daemon.py

A python script that can be triggered by pretty_BSEC.sh to draw bars for
IAQ, temperature and humidity to a LED matrix. I used a
[Unicorn HAT HD](https://shop.pimoroni.com/products/unicorn-hat-hd).

### Example

![LED bars](https://github.com/alexh-name/bme680_outputs/raw/master/images/LED_bars.jpg "LED bars")

### Dependencies

* python
* [unicorn-hat-hd](https://github.com/pimoroni/unicorn-hat-hd)

