# Tips (For me xD) 

#### Set Environment Variables (Linux)
***
1. Open the current user's profile into a text editor:  
 `vim ~/.bash_profile`

2. Add the export command for *VARIABLE_JSON*, which include your account and processed password:  
`export VARIABLE_JSON='{"MKGAL_EMAIL": "*****@*.com", "MKGAL_PASSWORD": "79*****************ba"}'`

OR. Get the profile information from *variables.json* file which is saved in `~/your/project/path/variables.json`


#### Set Crontab
***
Use \*.sh file and *crontab* file to realize automated tasks.  

1. You need to use an absolute path in shell file, otherwise there will be problems with automatic run.

		 #!/bin/sh	
		. /etc/profile
		. ~/.bash_profile
		cd /home/username/sign_mkgal_automatic-master
		/usr/local/bin/pipenv run /usr/local/bin/python3 /home/username/sign_mkgal_automatic-master/begin_sign_in.py  

2. Enter a new line in your *crontab* file, and save the file.  (Use absolute path)  
`20 0-23/12 * * * . /home/username/.bash_profile; /bin/sh /home/username/autosign.sh`

Check whether it is running correctly through `cat log.txt` or *crontab* mail.
