# Fondum

The **F**lask **O**Auth **N**GINX **D**ocker **U**nicorn **M**ongoDB super-framework.

*FONDUM* is a useful tool to generate web site projects.

It uses Flask, which is a tiny simple microframework. Then a large number of libraries and presumptive and complex requirements are added. In other words, it's not tiny anymore. The dictator of the fondum project pre-emptively decides what should be added. Such arrogance!

The following are the goals:

* Make it easy to _quickly_ create a functioning web site.
* Preemptively add a lot of functions that are not usually considered until *much* later as a project expands. The important bit is that these extra functions CAN BE SAFELY IGNORED until you are ready to use them. Such as:
   * External authentication
   * Multilingual translation and localization
   * Logging and Error Handling with integrated Flash messaging
   * Scalable image storage
   * Cloud distribution
      * instances that handle multiple hosts, or
      * a single host spread across multiple instances
   * Repository storage
   * Monitization from tips, advertisements, or direct payment
   * Usage tracking and A/B testing
* Splits implementation roles between IT/Ops and Developer.
   * IT/Ops folks do things that are complicated obscurely technical. Changes are made from a command-line shell. For example, generating the project's files, maintaining the URL routes, distributing docker containers, etc.
   * Developers do things with creative eye and skill. Changes are made from the live web. For example, writing content and uploading pictures.
* Emphasize _run-time_ performance not _compile-time_ performance. It is better to waste the programmer's time once than the public's time repeatedly. To wit:
   * Have the web site create tightly generated HTML5/CSS that requires little of the end-users browser and network connection.
   * Render and test as much as possible during compilation. (But not so much as to cause problem with the Developer.)
* Refrain from adding duplicative features.
   * Fondum should _not_ appeal to all people and use cases. (But if you want to add some extra bling, feel free to fork this project. It is open source after all.)
   * The include/exclude decision of the benevelan dictator is subjective and somewhat arbitrary.
   * For example, Fondum chooses to store images on Amazon S3. There are lots of many **good** alternatives to S3. But only one is chosen.

## Preparing To Use Fondum

1. If not already installed, install Python 2.7+ and Python 3.5+. Details vary by OS. If not automatically installed with Python 3, you will also need to install pip3. (Fondum uses Python 3, Flask runs under Python 2.7)
2. If not already installed, install [GIT](https://git-scm.com/). 
3. If not already installed, install Fondum itself system-wide.

   ```
   me@machine ~ $ sudo pip3 install fondum
   ```

   Alternatively, install from the repo directly:

   ```
   me@machine ~ $ sudo pip3 install git+https://github.com/JohnAD/fondum.git#egg=fondum
   ```


4. Change to the directory where you store your web projects. (Or, make such a directory.)

   ```
   me@machine ~ $ cd WebSites
   me@machine ~/WebSites $
   ```

5. If not already installed, install [docker](https://www.docker.com/). Details vary by OS.
6. If not already installed, install [docker-compose](https://docs.docker.com/compose/). Details vary by OS.

## Starting a Project with Fondum

1. Change to the directory where you store your web projects.
2. Invoke fondum to create your project. This will create a "dummy" website that is fully functional.

   ```
   me@machine ~/WebSites $ python3 fondum/create.py test
   ```

3. Enter the directory and build the docker containers.

   ```
   me@machine ~/WebSites $ cd test
   me@machine ~/WebSites/test $ sudo docker-compose build
   ```

4. Start the docker containers.

   ```
   me@machine ~/WebSites/test $ sudo docker-compose up
   ```

5. Test the new website! Browse to `http://127.0.0.1/`
6. When done testing, press `Ctrl+C` to stop docker.
7. Edit the files in `settings` and `custom` subdirectories to make the site the way you want.
8. Re-compile the site with fondum from the project root directory.

   ```
   me@machine ~/WebSites/test $ cd ..
   me@machine ~/WebSites $ python3 fondum/compile.py test --verbose
   ```

9. Go back step 4 until you are happy with the results.
10. Deploy the docker containers on your favorite cloud hosting service.

## List of Functions Beyond Flask

* Docker: a service that efficiently stores the project in "virtual machines". Used for both testing and deployment.
* MongoDB: a NoSQL database. Accessed via the MongoEngine library.
* Google OAuth2: an open authentication method. Allows users to login and create account with their Google accounts.
* Amazon S3: an object (file) storage service. It is where we keep most of the images.
* NGINX: the web server that serves the web pages to the public.
* Unicorn: a wrapper for flask used by NGINX in production environments.
* Creole: the `python-creole` library interprets the [creole](http://www.wikicreole.org/) text format. Used for safely formatting the live web content.


TBD:

* Babel/BabelFish: a library that handles multi-lingual internationalization. Creates and uses PO/POT translation files.
* SendGrid: a outbound SMTP messages service. Integrated with Msg (see below)
* some kind of traffic tracking
* compile-time compression of HTML5/CSS.


IN-BUILT (later to be made into standalone libraries):

* Msg: a service that generically returns "responses". Used in multiple ways: generates logs, web flash messages, and python function responses.
* Page: a page description class that goes WAY beyond what Flask-WTF does. Generates forms, tables, and almost all page content.
