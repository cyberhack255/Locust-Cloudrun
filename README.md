# Locust-Cloudrun

## Must perform the following from the GCP Cloudshell console
- Download Zip file or git clone https://github.com/cyberhack255/Locust-Cloudrun.git
  
### Change the GCP project id in build.sh
<img width="638" height="120" alt="image" src="https://github.com/user-attachments/assets/5826f743-3bca-4b22-a319-6e1c868b1e4e" />

### Set the credentials for web portal login in locustfile.py
- LOCUST_USERNAME = Anything (eg. admin, hacker etc)
- LOCUST_PASSWORD = anything
- LOCUST_SECRET_KEY = anything (eg. Fyurpgjsdflfdgyrt)
<img width="882" height="469" alt="image" src="https://github.com/user-attachments/assets/1d88ca42-37dc-4652-94bf-f172d818d6a0" />

### Building docker image in Artifact Registry
-  Go to Locust-Cloudrun directory
-  Run `./build.sh` should see the following screenshot
<img width="1121" height="468" alt="image" src="https://github.com/user-attachments/assets/f3dbde2a-4ecf-49af-9bec-73dc46003e10" />

- When the build is completed should see "Successfully build" message
<img width="869" height="159" alt="image" src="https://github.com/user-attachments/assets/cd95d332-629f-47ae-b6fc-54ad50c96af2" />

- Verify Docker image in Artifect Registry

<img width="1050" height="441" alt="image" src="https://github.com/user-attachments/assets/0f7afdcd-ac22-4368-b67d-1fca232a270c" />

### Deploy docker image in Cloud Run

- Go to Locust-Cloudrun directory
- Run `./deploy-locust.sh deploy <number>` - The number represent how many cloudrun service you want to run
- The following screenshot shows only 1 service deployed

<img width="1045" height="212" alt="image" src="https://github.com/user-attachments/assets/6b3560cf-71d9-4b4a-b7ea-93a8f52d70c7" />

 In the browser go to the address as shown in the `service url` which will ask for authentication (use the username and password that was setup earlier in locustfile.py)
 
<img width="647" height="551" alt="image" src="https://github.com/user-attachments/assets/474cb580-25d1-4282-8308-1465ad248479" />

- Once login, the following screen will appear.
  
<img width="889" height="594" alt="image" src="https://github.com/user-attachments/assets/f1a6eaa0-b1cb-49d4-8679-ca9d62ec87d2" />

- 1000 = number of virtual users
- 100 =  ramp up started per second
- Advanced options is where you define the duration time in minute

### Destroy Cloud Run service

- Run `./deploy-locust.sh delete <number>` You should see the following message.
<img width="820" height="110" alt="image" src="https://github.com/user-attachments/assets/feff97a0-bca8-42b5-be36-f13be25a39f6" />








