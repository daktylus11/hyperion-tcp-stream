# hyperion-tcp-stream
custom hyperion effect to stream data from remote device

Add stream_server.py to the hyperion custom-effects folder and run ist like any other effect (through web interface remote)

The blue light indicates the server is waiting for a connecting
A short white signal shows a successfully connected client, when the connection ends the lights return to blue

The stream client contains a sample client that sends a visual representation of the device's audio output.
To stream custom data the get_data() method needs to be modified, it returns the data sent to the hyperion server.
It implements the API functions from https://docs.hyperion-project.org/en/effects/API.html
To make the LED at (0, 0) shine red for example the list of commands would look something like this:


[

  {'id': IMAGESOLIDFILL, 'args': [0, 0, 0]},
  
  {'id': IMAGEDRAWPOINT, 'args': [0, 0, 1, 255, 0, 0]},
  
  {'id': IMAGESHOW, 'args': []}
  
]


here the first command creates a black background
the second one draws the red point and
the thrid one tells hyperion to show the modified image
refer to the documentation for more info
