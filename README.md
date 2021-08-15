### Tips (For me xD) 

#### Set Environment Variables (Linux)
***
1. Open the current user's profile into a text editor:  
 `vim ~/.bash_profile`

2. Add the export command for *VARIABLE_JSON*, which include your account and password:  
`export VARIABLE_JSON='{"MKGAL_EMAIL": "*****@*.com", "MKGAL_PASSWORD": "79*****"}'`

OR. Get the profile information from *variables.json* file which is saved in `~/your/project/path/variables.json`  
`{"MKGAL_EMAIL": "*****@*.com", "MKGAL_PASSWORD": "79*****"}`

#### Set Crontab (Linux)
***
Use \*.sh file and *crontab* file to realize automated tasks.  

1. You need to use an absolute path in shell file, otherwise there will be problems with automatic run.

		 #!/bin/sh	
		. /etc/profile
		. ~/.bash_profile
		cd /home/username/sign_mkgal_automatic-master
		/usr/local/bin/pipenv run /usr/local/bin/python3 /home/username/sign_website-master/begin_sign_in.py  

2. Enter a new line in your *crontab* file, and save the file.  (Use absolute path)  
`20 0-23/12 * * * . /home/username/.bash_profile; /bin/sh /home/username/autosign.sh`
***
Check whether it is running correctly through `cat log.txt` or *crontab* mail.

#### Functions already available
***
1. Automatically update the sign-in website.
2. When an error occurs, it will retry up to 5 times.
3. Record check-in status in `log.txt`
4. When the main website fails to sign in, it will switch to the secondary website.

#### 可能以后会做的
***
Better way to detect sign-in status.  
Optimize the configuration file.  
