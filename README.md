# django-npm-finder

Want to use npm modules in your django project without vendoring them?
`django-npm-finder` serves as a wrapper around the npm/yarn/pnpm cli and provides a staticfiles
finder that provides integration of your installed node_modules during development and hooks to
selectively provide `collectstatic` functionality to export static files for production without
exposing the entire node_modules hierarchy.

`django-npm-finder` is a fork of kevin1024's [django-npm](https://github.com/keven1024/django-npm) module with the
following changes:

- modern `pyproject.toml` packaging (poetry)
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
  $ poetry add django-npm-finder
```

```
  $ uv pip install django-npm-finder
```

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


* `NPM_EXECUTABLE_PATH`: (optional, default manager) sets `npm` as modules manager and optionally
  overrides its location.
  Supported NPM managers are: npm, yarn and pnpm.


* `NPM_STATIC_FILES_PREFIX`: (optional) Your npm files will be located under this path inside the
  static URL.
  As an example, if set to 'vendor' the collected files will be located in
  `/static/vendor/dist/bootstrap.min.js`, and if not set, it will be located in
  `/static/dist/bootstrap.min.js`.


* `NPM_FILE_PATTERNS`: (optional) By default, django-npm will expose all modules defined as dependencies
  in `package.json` to Django as staticfiles, excluding files using the default or specified ignore patterns.
  You may want to restrict what is exposed.
  You can pick specific files by adding some additional configuration shown in the following code block.
  Keys are the names of the npm modules, and values are lists containing strings. The strings match against glob patterns.
  Use double asterisk wildcard '**' to include all subdirectories.
  > **NOTE**: If unset, the module will autoconfigure modules based on the
  > dependencies specified in `package.json`.
```python
NPM_FILE_PATTERNS = {
    'bootstrap': ['dist/*'],
    'htmx.org': ['htmx.org/dist/*']
}
```

* `NPM_IGNORE_PATTERNS`: (optional) This is a python list of patterns to exclude.
  There is an extensive list of default patterns that are excluded, but you can override this.


* `NPM_FINDER_USE_CACHE`: (default True) A boolean that enables cache in the finder.
  If enabled, the file list will be computed only once when the server is started.


## npm install

To add the `./manage.py npm_install` "django_npm" must be added to Django's `INSTALLED_APPS` setting, otherwise it doesn't need to be added there.

Even if the module is not added in `INSTALLED_APPS` you can run `npm install` programmatically
from python by creating a script as follows:

```python
from django_npm.finders import npm_install

npm_install()
```

The advantage of using `npm_install` is that it will run the package manager configured in
your Django settings.
