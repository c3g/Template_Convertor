# Convertor Installation and Update Guide


## Installation
___
open an ssh tunnel to the dev or qc or prod server (note: IT has to grant you access to do this)

(dev)
`ssh cousteau.genome.mcgill.ca -L 2222:f5kvm-biobank-dev:22 `

(qc)
`ssh cousteau.genome.mcgill.ca -L 2223:f5kvm-biobank-qc:22`

(prod)
`ssh cousteau.genome.mcgill.ca -L 2224:biobank.genome.mcgill.ca:22`

In a separate terminal, ssh into the server (use 2222, 2223 or 2224 depending which server you are connecting to)

`ssh -p 2222 <your_user_name>@localhost`

switch to the django user (sudo su - django)

`sudo su - django`

cd to the django user home folder if not already there (cd ~)

`cd ~`

Build Python 3.9

`mkdir python-new cd python-new cp /opt/Python-3.9.0.tgz .`

`tar -xzvf Python-3.9.0.tgz `

`cd Python-3.9.0./configure --prefix=$HOME/opt/Python-3.9.0 --with-ssl-default-suites=openssl`

`make -j4 `

`make install`

`export PATH=$HOME/opt/Python-3.9.0/bin:$PATH` 

`pip3.9 install streamlit` 

Streamlit has a dependency on pyarrow that will not run on the dev and qc vm’s - the vm’s do not support the instruction set required by the binary build of pyarrow. To fix that, we have to build our own version of pyarrow on the vm itself. *This is not necessary on prod*.

`pip3.9 uninstall pyarrow `

`pip3.9 install /opt/pyarrow-9.0.0.dev333+g984b59a-cp39-cp39-linux_x86_64.whl` 

Next, git clone the Template_Convertor project into the /data folder (*use https://*)

`cd /data`

`git clone https://github.com/c3g/Template_Convertor.git`

`cd Template_Convertor`

Create a python virtual environment USING PYTHON 3.9 and activate it

`python3.9 -m venv env3.9`

`source env3.9/bin/activate`

pip install the dependencies for the project

`pip install -r requirements.txt`

Override the pyarrow dependency (*not needed on prod*)

`pip uninstall pyarrow`

`pip3.9 install /opt/pyarrow-9.0.0.dev333+g984b59a-cp39-cp39-linux_x86_64.whl` 

The project should now be ready to go. Start the application:

`streamlit run app_streamlit.py`

Verify that it is running by opening a browser and going to one of the addresses:

`DEV: https://f5kvm-biobank-dev.genome.mcgill.ca/convertor/`

`QC: https://f5kvm-biobank-qc.genome.mcgill.ca/convertor/`

`PROD: https://biobank.genome.mcgill.ca/convertor/`
 
If everything is running properly, shutdown streamlit and then  use gnu screen to launch the app, so that ending your ssh session doesn’t shutdown the app.

### Running Convertor in Dev and QC
___

*In Dev and QC we start and stop the Convertor app manually. We use gnu screen so that we can log out of the terminal and Convertor will continue running.*

Shutdown streamlit

`ctrl-C`

Start a new screen named ‘convertor’

`screen -R convertor`

Make sure the working directory is still `/data/Template_Converter` then launch the app

`streamlit run app_streamlit.py`

Exit the screen - this will leave the app running after you logout from ssh.

`ctrl-a, d`

To come back to the screen later to check that the app is still running use:

`sudo su - django`

`screen -r convertor`

### Running Convertor in Prod
___
*Nginx is configured to run the Convertor application in Prod.*

The following commands are used to manage the application. You can ssh into the prod server and then run these commands (without having to sudo as the django user).
```
sudo /usr/bin/systemctl start convertor
sudo /usr/bin/systemctl status convertor
sudo /usr/bin/systemctl stop convertor
sudo /usr/bin/systemctl restart convertor
```

The Convertor log can be viewed with this command:

```
sudo /usr/bin/journalctl -u convertor
```

---
## Update
___

Open an ssh tunnel as described above, then:

sudo to the django user

`sudo su - django`

Restart the 'convertor' screen

`screen -r convertor`

Shut down streamlit, if it's still running

`ctrl-c`

Make sure you are in the Template_Convertor directory

`cd /data/Template_Convertor`

Run git status to make sure git is working and then pull

`git status`

`git pull`

Relaunch the app

`streamlit run app_streamlit.py`

Exit the screen

`ctrl-a d`





