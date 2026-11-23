# django-npm-finder

Want to use npm modules in your django project without vendoring them?
`django-npm-finder` serves as a wrapper around the npm/yarn/pnpm cli and provides a staticfiles
finder that provides integration of your installed node_modules during development and hooks to
selectively provide `collectstatic` functionality to export static files for production without
exposing the entire node_modules hierarchy.

`django-npm-finder` is a fork of kevin1024's [django-npm](https://github.com/kevin1024/django-npm) module with the
following changes:

- modern `pyproject.toml` packaging (uv)
- caching of searches to provide better performance
- much of the core refactored to be more robust and predictable
- added support for alternative node managers, such as yarn and pnpm.
- autoconfigure default match patterns from `package.json` dependencies
- added an extensive list of default ignore patterns
- unit tests were added (pytest)

These changes make the module easier to use, more reliable and as autoconfiguring as possible.

## Installation

- Install into your django project

```
  $ pip install django-npm-finder
```

```
  $ uv add django-npm-finder
```

```
  $ uv pip install django-npm-finder
```

- Requires Python 3.13 or later and Django 5.2.17 or later.


- Install npm, yarn or pnpm.
  If you use a private registry, make sure your `.npmrc` or equivalent is set up to connect to it.


- Have a `package.json` at the root of your project (can be configured), listing your dependencies.


- Add `django_npm.finders.NpmFinder` to `STATICFILES_FINDERS`


- Configure your `settings.py` as detailed in the following section [Configuration](#configuration)


- Run `$ ./manage.py npm_install` from the command line, or with your own Python code
(see npm install section below).
Or install your npm modules using `[p]npm|yarn install` from the command line.


- `$ ./manage.py collectstatic` will copy all selected node_modules files into your `STATIC_ROOT`.
   This is only required at deployment, and if using Django runserver for development, will not be required.

## Configuration

In the following section, reference to `npm` also includes `yarn` or `pnpm`.

* `NPM_ROOT_PATH`: path to the npm "root" directory, where your package manager will look
  for `package.json`, `node_modules`, `.npmrc` etc.
  Set this if it differs from the root of your Django project
  (usually `settings.BASE_DIR` in most Django projects).


* `NPM_EXECUTABLE_PATH`: (optional, default `npm`) the package manager to run, as an executable name
  or a full path. The manager is recognised by the executable name, which must end in `npm`,
  `yarn` or `pnpm`; this selects the command line options used by `npm_install`.


* `NPM_STATIC_FILES_PREFIX`: (optional) Your npm files will be located under this path inside the
  static URL.
  As an example, if set to 'vendor' the collected files will be located in
  `/static/vendor/bootstrap/dist/bootstrap.min.js`, and if not set, it will be located in
  `/static/bootstrap/dist/bootstrap.min.js`.


* `NPM_FILE_PATTERNS`: (optional) By default, django-npm-finder will expose all modules listed under `dependencies`
  in `package.json` (not `devDependencies`) to Django as staticfiles, excluding files using the default
  or specified ignore patterns.
  You may want to restrict what is exposed.
  You can pick specific files by adding some additional configuration shown in the following code block.
  Keys are the names of the npm modules, and values are lists containing strings. The strings are glob
  patterns, matched against paths relative to that module's directory.
  Use double asterisk wildcard '**' to include all subdirectories.
  > **NOTE**: If unset, the module will autoconfigure modules based on the
  > dependencies specified in `package.json`.
```python
NPM_FILE_PATTERNS = {
    'bootstrap': ['dist/*'],
    'htmx.org': ['dist/*']
}
```

* `NPM_IGNORE_PATTERNS`: (optional) This is a python list of patterns to exclude.
  There is an extensive list of default patterns that are excluded, but you can override this.
  An empty list disables all ignore patterns; leave the setting unset to use the defaults.


* `NPM_FINDER_USE_CACHE`: (default True) A boolean that enables cache in the finder.
  If enabled, the file list will be computed only once when the server is started.


## npm install

To use `./manage.py npm_install`, `"django_npm"` must be added to Django's `INSTALLED_APPS` setting. Otherwise it doesn't need to be added there.

Even if the module is not added in `INSTALLED_APPS` you can run `npm install` programmatically
from python by creating a script as follows:

```python
from django_npm.finders import npm_install

npm_install()
```

The advantage of using `npm_install` is that it will run the package manager configured in
your Django settings. `manage.py npm_install` exits with an error if the package manager fails.

The package manager is run with a restricted environment: `PATH`, `HOME` (or the Windows
equivalents), proxy and certificate settings, and `npm_config_*`, `PNPM_*`, `YARN_*`, `NODE_*`
and `COREPACK_*` variables are passed through. Other variables, such as your Django secrets,
are not, because package install scripts are third-party code.
