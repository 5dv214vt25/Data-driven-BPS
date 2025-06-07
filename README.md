# Data-driven Business Process Simulation
This project is a web application that allows users to create business process models from event logs. The models can then be manipulated, simulated and analysed. The model creation and simulation is done with either [Simod](https://github.com/AutomatedProcessImprovement/Simod) or [AgentSimulator](https://github.com/lukaskirchdorfer/agentsimulator).

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed
- [Git](https://git-scm.com/downloads) 

## Run Locally
To run locally, follow these steps:

1. Clone the repo
   ```sh
   git clone https://github.com/5dv214vt25/Data-driven-BPS.git
   ```
2. Add password files for database in the project root directory with passwords.

	**macOS & Linux (bash shell)**

	``` bash
	printf "password" >> pg_password.txt
	printf "super_password" >> pg_super_password.txt
	```
	**Windows PowerShell**

	``` powershell
	Add-Content -NoNewline -Path pg_password.txt -Value "password"
	Add-Content -NoNewline -Path pg_super_password.txt -Value "super_password"
	```

	**Windows Command Prompt**
	``` cmd
	<nul set /p=password>>pg_password.txt
	<nul set /p=super_password>>pg_super_password.txt
	```
3. Run docker compose to build and run the containers.

	``` bash
	docker compose up --build -d
	```
4. The web-app can now be accessed on [http://localhost:80/](http://localhost:80/)

## Stop and remove containers

To stop the containers, run:

``` bash
docker compose down --volumes --remove-orphans
```

To Remove all unused images, run: 
``` bash
docker image prune -a
```

## Editing configuration settings

In the files nginx.conf and compose.yaml there are certain settings that can be changed depending on use case.

### [nginx.conf](https://github.com/algotgraner/pvt-test/blob/main/nginx.conf)
`client_max_body_size 100M;` limits the size of files that can be uploaded (XES files will be converted to CSV files and thus reduced in size).

```
proxy_connect_timeout 3600s;
proxy_send_timeout 3600s;
proxy_read_timeout 3600s;
send_timeout 3600s;
```
These values change how long Nginx will wait for responses.

### [compose.yaml](https://github.com/algotgraner/pvt-test/blob/main/compose.yaml)

`command: gunicorn -w 2 --timeout=3600 -b 0.0.0.0:8888 api:app`
The amount of concurrent gunicord workers is set with the `-w` flag and `--timeout` flag sets the lifetime (seconds) of those workers.

## Event log samples

In the zip file `event_log_samples.zip` there are three files that work with both Simod and AgentSimulator that you can use to try out the project. Please mind that `BPIC17.xes` (one of the event logs in the zip file) can can take a prolonged time to do the discovery on depending on your PC specifications. During testing it has taken as long as 50 minutes for Simod to run its discovery on that event log with AgentSimulator being a bit quicker.

## Deploying to Production

To deploy this project in a production environment, it is recommended to use NGINX as a reverse proxy with HTTPS enabled. The provided Docker Compose setup includes an NGINX container, using the configuration defined in `nginx.conf`.

By default, the NGINX configuration is set up for local development and listens on port 80 without SSL certificates. For production, you should update the configuration to enable HTTPS on port 443 using valid SSL certificates.

For guidance on configuring HTTPS in NGINX, refer to the official documentation: [NGINX: Configuring HTTPS Servers](https://nginx.org/en/docs/http/configuring_https_servers.html)


## Known issues

This section lists some common known issues.

### Docker Issues on Windows

**Description:** Sometimes containers fail to start on Windows if WSL2 is not properly configured. 

**Workaround:** Ensure WSL2 is installed and set as the default backend for Docker Desktop. Follow [Docker's WSL2 guide](https://docs.docker.com/desktop/windows/wsl/) for setup instructions.

### PostgreSQL Password File Permissions

**Description:** On some systems (especially Linux), the `pg_password.txt` and `pg_super_password.txt` files may be ignored due to restrictive permissions.  

**Workaround:** Ensure the files are readable by Docker:

```bash
chmod 644 pg_password.txt pg_super_password.txt
```

### PostgreSQL Login Fails Due to Newlines in Password Files

**Description:** If the password files `pg_password.txt` or `pg_super_password.txt` contain a trailing newline, the database service may reject the credentials, causing login failures. This is a common issue when the files are created using editors that append newlines automatically.

**Workaround:** Ensure the password files are created without any trailing newline characters. Use the commands below to write the passwords without adding a newline:

**macOS & Linux (bash shell)**
``` bash
printf "password" >> pg_password.txt
printf "super_password" >> pg_super_password.txt
```
**Windows PowerShell**

``` powershell
Add-Content -NoNewline -Path pg_password.txt -Value "password"
Add-Content -NoNewline -Path pg_super_password.txt -Value "super_password"
```

**Windows Command Prompt**
``` cmd
<nul set /p=password>>pg_password.txt
<nul set /p=super_password>>pg_super_password.txt
```
## Contributors

This project was developed as part of a course at Umeå University by a group of 35 students.

See the full list of [Contributors](./CONTRIBUTORS.md).

## Contributing
This project was developed as part of a university course project and is no longer maintained.

We are not accepting any issues, pull requests, or other contributions. If you would like to build upon or extend the project, feel free to fork the repository and continue development independently.

## License
This project is licensed under the terms of the [Apache License 2.0](./LICENSE).

