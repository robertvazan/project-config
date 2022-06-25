import contextlib
import textwrap
import re
import io
import pathlib
import datetime
import urllib.request
import urllib.parse

# resources and constants
resource_directory = lambda: config_directory()/'res'
lang_directory = lambda: None
apache_license_text = lambda: (resource_directory()/'license.txt').read_text('utf-8')
gitignore_text = lambda: (lang_directory()/'gitignore.txt').read_text('utf-8')
current_year = lambda: datetime.date.today().year

# checkout
workflows_directory = lambda: project_directory()/'.github'/'workflows'

# repository
repository_name = lambda: project_directory().name
github_repository_url = lambda: f'https://github.com/robertvazan/{repository_name()}' if is_opensource() else None
bitbucket_repository_url = lambda: f'https://bitbucket.org/robertvazan/{repository_name()}'
repository_url = lambda: github_repository_url() if is_opensource() else bitbucket_repository_url()
repository_file_url = lambda path: f'{repository_url()}/blob/master/{path}'
repository_dir_url = lambda path: f'{repository_url()}/tree/master/{path}'

# general info
pretty_name = lambda: repository_name()
is_opensource = lambda: True
project_version = lambda: (project_directory()/'scripts'/'version.txt').read_text('utf-8').strip()

# license
inception_year = lambda: current_year()
license_id = lambda: 'Apache-2.0' if is_opensource() else None
license_name = lambda: 'Apache License 2.0' if is_opensource() else None
license_url = lambda: repository_file_url('LICENSE') if is_opensource() else None
license_text = lambda: apache_license_text() if is_opensource() else None

# website
has_website = lambda: is_opensource()
subdomain = lambda: repository_name()
website = lambda: f'https://{subdomain()}.machinezoo.com/'
homepage = lambda: website()

# readme
standard_badges = lambda: []
badges = lambda: standard_badges()
stable_status = lambda: 'Stable and maintained.'
experimental_status = lambda: 'Experimental.'
obsolete_status = lambda: 'Obsolete. No longer maintained.'
unpublished_status = lambda: 'Experimental. Unpublished.'
project_status = lambda: stable_status() if is_opensource() else unpublished_status()
def common_documentation_links():
    if has_website():
        yield 'Homepage', homepage()
standard_documentation_links = lambda: common_documentation_links()
documentation_links = lambda: standard_documentation_links()
md_description_fallback = lambda: None
md_description = lambda: homepage_lead() + f'\n\nMore on [homepage]({homepage()}).' if has_website() else md_description_fallback()
documentation_comment = lambda: None
embeddable_readme = lambda: False
readme_url = lambda path: repository_file_url(path) if embeddable_readme() else path
readme_dir_url = lambda path: repository_dir_url(path) if embeddable_readme() else path

def capture_output(function):
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        function()
    return f.getvalue()

homepage_html = None
def homepage_lead():
    url = homepage()
    global homepage_html
    if not homepage_html:
        homepage_html = urllib.request.urlopen(url).read().decode('utf-8')
        homepage_html = re.sub(r'<aside.*?</aside>', '', homepage_html, flags=re.DOTALL)
    lead = re.search(r'<p>(.*?)</p>', homepage_html, re.DOTALL).group(1)
    lead = re.sub(r'<code>(.*?)</code>', r'`\1`', lead)
    lead = re.sub(r'''<a\s+href=["']([^'"]*)["']>(.*?)</a>''', lambda m: f'[{m.group(2)}]({urllib.parse.urljoin(url, m.group(1))})', lead, 0, re.DOTALL)
    lead = re.sub(r'<.*?>', '', lead, 0, re.DOTALL)
    return lead

def print_to(path, generator):
    print(f'Generating {path}...')
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as file:
        with contextlib.redirect_stdout(file):
            generator()

def print_lines(text, *, indent='', tabify=False):
    text = textwrap.dedent(text)
    if text[-1:] != '\n':
        text += '\n'
    if tabify:
        for i in range(0, 5):
            text = re.sub('^(\t*) {4}', r'\1\t', text, flags=re.MULTILINE)
    text = textwrap.indent(text, indent)
    print(text, end='')

def notice():
    print(f"Robert Važan's {pretty_name()}")
    if has_website():
        print(homepage())
    print_lines(f'''\
        Copyright {inception_year()}-{current_year()} Robert Važan and contributors
        Distributed under {license_name()}.
    ''')

def contribution_guidelines():
    print_lines(f'''\
        <!--- Generated by scripts/configure.py --->
        # How to contribute to {pretty_name()}

        Thank you for taking interest in {pretty_name()}. This document provides guidance for contributors.

        ## Authoritative repository

        Sources are mirrored on several sites. You can submit issues and pull requests on any mirror.

        * [{repository_name()} @ GitHub]({github_repository_url()})
        * [{repository_name()} @ Bitbucket]({bitbucket_repository_url()})

        ## Issues

        Both bug reports and feature requests are welcome. There is no free support,
        but it's perfectly reasonable to open issues asking for more documentation or better usability.

        ## Pull requests

        Pull requests are generally welcome.
        If you would like to make large or controversial changes, open an issue first to discuss your idea.

        Don't worry about formatting and naming too much. Code will be reformatted after merge.
        Just don't run your formatter on whole source files, because it makes diffs hard to understand.

        ## Generated code

        Some files in this repository are generated by [configure.py](scripts/configure.py),
        which in turn uses author's personal [project-config](https://github.com/robertvazan/project-config) repository.
        The intent is to enforce conventions and to reduce maintenance burden.
        If you need to modify generated files, just do so manually and I will update `configure.py` after merge.

        ## License

        Your submissions will be distributed under [{license_name()}](LICENSE).
    ''')

def readme():
    print('<!--- Generated by scripts/configure.py --->')
    if is_opensource():
        print('[![SWUbanner](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner2-direct.svg)](https://github.com/vshymanskyy/StandWithUkraine/blob/main/docs/README.md)')
        print()
    print(f'# {pretty_name()}')
    if capture_output(badges):
        print()
        badges()
    if md_description():
        print()
        print_lines(md_description())
    print()
    print('## Status')
    print()
    print_lines(project_status())
    if has_website():
        print()
        print_lines(f'''\
            ## Getting started

            See [homepage]({homepage()}).
        ''')
    if list(documentation_links()) or capture_output(documentation_comment):
        print()
        print('## Documentation')
        if list(documentation_links()):
            print()
            for title, url in documentation_links():
                print(f'* [{title}]({url})')
        if capture_output(documentation_comment):
            print()
            documentation_comment()
    elif is_opensource():
        print()
        print_lines(f'''\
            ## Documentation

            None yet. Review source code.
        ''')
    if is_opensource():
        print()
        print_lines(f'''\
            ## Feedback

            Bug reports and pull requests are welcome. See [CONTRIBUTING.md]({readme_url('CONTRIBUTING.md')}).

            ## License

            Distributed under [{license_name()}]({readme_url('LICENSE')}).
        ''')

def gitignore():
    print_lines(gitignore_text())

def license():
    print(license_text(), end='')

def remove_obsolete(path):
    if path.exists():
        print(f'Removing obsolete {path}...')
        path.unlink()
