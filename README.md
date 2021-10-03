# Flask_restx_Shutdown
Sample of Building Flask_restx Server with test Browser and Closing From Resource

There are some edge cases where the web server needs to be shut down by the request handler in a Flask application.

This sample uses flask_restx and passes a shutdown method to selected Resource to allow it to shut down the web server. This example launches a Web Server and a web browser and will automatically close the web server and/or browser if the user presses a button or closes the web browser.

It may seem contrived but this is a good example of where some testing can be done which requires user interaction and a web browser session.

To run:
```python3 sample.py```

This code was written to run on Linux. Should work ok on MacOS and although not tested, it will likely not work on windows.
