# django-npm-finder

Want to use npm modules in your django project without vendoring them? django-npm serves as a wrapper around the npm/yarn/pnpm cli and provides a staticfiles
finder that provides integration of your installed node_modules during development and hooks to provide selectively `collectstatic` functionality for production.

`django-npm-finder` is a fork of kevin1024's [django-npm](https://github.com/keven1024/django-npm) module with modern packaging, dding caching and options to use npm, yarn or pnpm.
Extensive tests were added with pytest support.

## Installation

1. `$ pip install django-npm-finder`

3. Install npm, yarn or pnpm.
If you use a private registry, make sure your `.npmrc` or equivalent is set up to connect to it

4. Have a `package.json` at the root of your project, listing your dependencies

5. Add `django_npm.finders.NpmFinder` to `STATICFILES_FINDERS`

6. Configure your `settings.py` as detailed in the following section [Configuration](#configuration)

7. `$ ./manage.py npm_install` from the command line, or with your own Python code (see npm install section below).

7. `$ ./manage.py collectstatic` will copy all selected node_modules files into your `STATIC_ROOT`.
This is only required at deployment, and if using Django runserver for development, will not be required.

## Configuration
In the following section, reference to `npm` also includes `yarn` or `pnpm`.

 * `NPM_ROOT_PATH`: *absolute* path to the npm  "root" directory - this is where npm will look for your `package.json`, put your `node_modules` folder and look for a `.npmrc` file

 * `NPM_EXECUTABLE_PATH`: (optional, default manager) sets `npm` as modules manager and optinoally overrides its location.
   Supported NPM managers are: npm, yarn and pnpm. If the executable is on the $PATH, the value does not need to contain a full/absolute path.

 * `NPM_STATIC_FILES_PREFIX`: (optional) Your npm files will end up under this path inside static, usually something like ` os.path.join('js', 'lib')` (so your files will be in /static/js/lib/react.js for example) but you can leave it blank and they will just end up in the root.

 * `NPM_FILE_PATTERNS`: (optional) By default, django-npm will expose all files in `node_modules` to Django as staticfiles.  You may not want *all* of them to be exposed.  You can pick specific files by adding some additional configuration:
```python
NPM_FILE_PATTERNS = {
   'bootstrap': ['dist/**'],
   'htmx.org': ['htmx.org/dist/**']
}
```
   Keys are the names of the npm modules, and values are lists containing strings.  The strings match against glob patterns.
   Use '**' to include all subdirectories.

 * `NPM_IGNORE_PATTERNS`: (optional) This is a list of patterns to exclude. By default, only files starting with a period '`.`' are excluded.

 * `NPM_FINDER_USE_CACHE`: (default True) A boolean that enables cache in the finder. If enabled, the file list will be computed only once, when the server is started.

## npm install

To add the `./manage.py npm_install` command (which runs npm, yarn or pnpm - depending on which node manager is configured in settings)
"django_npm" must be added to `INSTALLED_APPS`, otherwise it can be omitted.

If you want to run `npm install` programmatically, you can do:

```python
from django_npm.finders import npm_install
npm_install()
```
