# How to install this pingid applet into your Django application

1. Put your app into a folder named mysite, if it is not already established an applet. If it is, either replaces all instances of your app name with 'mysite' or all instances of 'mysite' in the pingid applet with your application name. For simplicity, I will continue to refer to this folder as 'mysite'
2. copy the 'pingid' folder such that it sits on the same directory level as mysite
3. add the views seen in this sample mysite folder to your apps views.py.
4. same as above, but for urls.py.
5. Fill out and/or create the .env and config files located in /pingid as needed.
6. Add pingid to your installed apps in the settings.py of your main app 
7. use a wrapper or django built in method to ensure the presence of the token at each endpoint that must be secured. 
