![alt text](project/sheru/static/sheru-logo.png)

# What is Sheru?

The goal of Sheru is simple - provide a experience similar to popular cloud shell environments (like Azure Cloud Shell) on a self-hosted server.

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