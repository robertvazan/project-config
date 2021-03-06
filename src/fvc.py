exec((config_directory()/'src'/'net.py').read_text())

benchmark_name = lambda: None
benchmark_abbreviation = lambda: None
benchmark_url = lambda: None
is_extractor_part = lambda: False
is_matcher_part = lambda: False
is_multipart_submission = lambda: is_extractor_part() or is_matcher_part()
bundled_sister_projects = lambda: []
has_submission_zip = lambda: not is_multipart_submission() or bundled_sister_projects()
submission_zip = lambda: f'sourceafis-fvc-{benchmark_abbreviation().lower()}.zip'

subdomain = lambda: 'sourceafis'
homepage = lambda: website() + 'fvc'
is_library = lambda: False
assembly_name = lambda: 'enroll' if is_extractor_part() else 'match'
namespace_suffix = lambda: '.Extractor' if is_extractor_part() else '.Matcher' if is_matcher_part() else ''
root_namespace = lambda: f'SourceAFIS.FVC.{benchmark_abbreviation()}{namespace_suffix()}'
name_suffix = lambda: ' extractor' if is_extractor_part() else ' matcher' if is_matcher_part() else ''
pretty_name = lambda: f'SourceAFIS{name_suffix()} for FVC {benchmark_abbreviation()}'
md_description = lambda: f'''\
	Submission of [SourceAFIS](https://sourceafis.machinezoo.com/){name_suffix()}
	to [{benchmark_name()}]({benchmark_url()}) benchmark
	in [FVC-onGoing](https://biolab.csr.unibo.it/FVCOnGoing/UI/Form/Home.aspx) competition.

	More on [homepage]({homepage()}).
'''

def documentation_links():
    yield from standard_documentation_links()
    yield 'SourceAFIS overview', 'https://sourceafis.machinezoo.com/'
    yield f'FVC-onGoing {benchmark_abbreviation()} benchmark', benchmark_url()

def dependencies():
    use('SourceAFIS:3.14.0')

def publish_script():
    print('#/bin/sh -e')
    print('# Generated by scripts/configure.py')
    print('cd `dirname $0`/..')
    print('dotnet publish -c release -r win-x86')
    if has_submission_zip():
        print(f'rm -rf {root_namespace()}/bin/{{submission,{submission_zip()}}}')
        print(f'mkdir -p {root_namespace()}/bin/submission')
        for project in bundled_sister_projects():
            print(f'cp ../{project}/*/bin/Release/net*/win-x86/publish/* {root_namespace()}/bin/submission/')
        print(f'cp */bin/Release/net*/win-x86/publish/* {root_namespace()}/bin/submission/')
        print(f'cd {root_namespace()}/bin/submission')
        print(f'zip ../{submission_zip()} *')

generate_net = generate

def generate():
    ps = project_directory()/'scripts'/'publish.sh'
    print_to(ps, publish_script)
    ps.chmod(ps.stat().st_mode | 0o111)
    generate_net()
