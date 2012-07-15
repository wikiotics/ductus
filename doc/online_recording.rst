Online recording system
=======================

Ductus has a basic online recording system which allows a user to directly record her voice onto the ductus server.

We currently use a flash based application `wami-recorder` (https://code.google.com/p/wami-recorder/) modified to suit our needs.
Wami-recorder provides a flash backend that accesses the client microphone and uploads the recorded wav file to a server.

We tweaked it to keep data locally until the user actively requests uploading to the server. This limits bandwidth usage.
Posting the audio file to the server is done from javascript (not flash) without accessing the local filesystem. This gives relative freedom in handling the recorded file.

The audio file is posted using an XMLHttpRequest in an HTML form compliant manner, so that the server doesn't need to know if the file was recorded online or picked from the client's hard disk.

This means that no additional server code is required to deal with online recording, nor any server-side applications (such as red5 for instance).
Also, all audio is sent to the webserver on port 80, which means online recording cannot be blocked for a user having access to the site (unlike streaming-based solutions, which would require additional ports open on the server).

