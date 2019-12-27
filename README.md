![alt text](project/sheru/static/sheru-logo.png)

# What is Sheru?

The goal of Sheru is simple - provide a experience similar to popular cloud shell environments (like Azure Cloud Shell) on a self-hosted server. The primary use-case is to act as a bastion container to communicate with services on your network, like SSH'ing to servers, running scripts to create VMs, etc.

Essentially, Sheru spins up a new container for every user who connects, and deletes the container when they leave. Optionally, a directory can be mounted on every container to provide access to useful files, like scripts.

### THIS PROJECT IS STILL IN ALPHA

What does this mean?

* There are bugs. Probably lots of them.
  * My day job is Systems / Network administration, not development. I know the code looks gross
* Security flaws are probably guarenteed.
* Feature incomplete
  * I have the most basic functionality I was looking for in my head, but more will likely come.
* This project is not geared towards less tech-savvy users - knowledge of docker will be useful when troubleshooting.

## Getting Started

Want to test it out? Be my guest! A sample _baseline_ [docker-compose.yml](https://raw.githubusercontent.com/SoarinFerret/sheru/master/docker-compose.yml) is provided in the root directory. Please note that by default it is not using SSL, and I HIGHLY recommend using HTTPS.

Besides the docker-compose file, you will also need a file called `.env`. At a bare-minimum, you will need something like this:

```env
SECRET_KEY=RANDOM_KEY_GOES_HERE
POSTGRES_PASSWORD=password
POSTGRES_USER=postgres
POSTGRES_DB=django
```

Here are the basic install steps:

```bash
# Clone Repo
git clone https://github.com/SoarinFerret/sheru.git
cd sheru

# Create .env file
vim .env

# Start services
docker-compose up -d

# Create first user
docker exec -it sheru_sheru_1 python manage.py createsuperuser
```

## Settings

All settings can be provided as environment variables:

* `SECRET_KEY`: This should be a user generated key for Django
* `DB_OVERRIDE`: If this option is set to anything, Django will use sqlite instead of postgres
* `POSTGRES_DB`: The postgres DB to connect to
* `POSTGRES_USER`: The postgres DB username
* `POSTGRES_PASSWORD`: The postgres DB password
* `HEADER_AUTH`: If set to 'True', the application will accept `REMOTE_USER` header from an upstream proxy server
* `DEBUG`: If set to 'True', the application will produce debug output

## Credits

* [xterm.js](https://xtermjs.org/): Used for front-end terminal emulator
* [This article](https://ynotes.cn/blog/article_detail/180): Used as my basis for my [django-channels](https://channels.readthedocs.io/en/latest/index.html) implementation
* [Font Awesome](https://fontawesome.com/): Used for icons in the project
* [LogoMakr](https://logomakr.com): Created my free logo at LogoMakr.com
