exec((config_directory()/'src'/'common.py').read_text())

import uuid

# resources and constants
lang_directory = lambda: resource_directory()/'net'

# general info
pretty_name = lambda: root_namespace()

# project info
nuget_title = lambda: pretty_name()
nuget_description = lambda: None
nuget_tags = lambda: None
nuget_icon = lambda: 'icon.png' if (project_directory()/root_namespace()/'icon.png').exists() else None

# code structure
is_library = lambda: True
root_namespace = lambda: repository_name()
extra_sln_projects = lambda: []
def sln_projects():
    yield root_namespace()
    if has_tests():
        yield f'{root_namespace()}.Tests'
    yield from extra_sln_projects()

# build features
target_framework = lambda: '5.0'
nuget_release = lambda: is_library() and is_opensource()
has_tests = lambda: is_library()

# dependencies
dependencies = lambda: None
def standard_test_dependencies():
    use_nunit()
    use_nunit_adapter()
    use_mstest()
test_dependencies = lambda: standard_test_dependencies()

# readme
md_description_fallback = lambda: nuget_description()
embeddable_readme = lambda: True
def standard_badges():
    if nuget_release():
        print(f'[![Nuget](https://img.shields.io/nuget/v/{root_namespace()})](https://www.nuget.org/packages/{root_namespace()}/)')

def use_xml(xml): print_csproj(2, xml)
def use(dependency):
    package, version = dependency.split(':')
    use_xml(f'<PackageReference Include="{package}" Version="{version}" />')
def define_use(dependency): return lambda: use(dependency)
use_nunit = define_use('NUnit:3.13.3')
use_nunit_adapter = define_use('NUnit3TestAdapter:4.2.1')
use_mstest = define_use('Microsoft.NET.Test.Sdk:17.2.0')

def release_workflow():
    # GitHub Actions cannot run the whole release procedure.
    # Releases are initiated by running a script on developer machine, which then triggers this workflow via REST API.
    print_lines(f'''\
        # Generated by scripts/configure.py
        name: release
        on: workflow_dispatch
        jobs:
          release:
            uses: robertvazan/project-config/.github/workflows/net-release.yml@master
            with:
              dotnet-version: {target_framework()}.x
            secrets:
              nuget-token: ${{{{ secrets.NUGET_TOKEN }}}}
    ''')

def print_csproj(indent, text):
    print_lines(text, indent=indent * '  ')

def csproj():
    print_lines(f'''\
        <!-- Generated by scripts/configure.py -->
        <Project Sdk="Microsoft.NET.Sdk">
          <PropertyGroup>
            <TargetFramework>net{target_framework()}</TargetFramework>
            <Version>{project_version()}</Version>
            <Authors>robertvazan</Authors>
            <Title>{nuget_title()}</Title>
            <PackageProjectUrl>{homepage() if has_website() else repository_url()}</PackageProjectUrl>
            <RepositoryUrl>{repository_url()}.git</RepositoryUrl>
            <PackageLicenseExpression>{license_id()}</PackageLicenseExpression>
            <GenerateDocumentationFile>true</GenerateDocumentationFile>
            <PackageReadmeFile>README.md</PackageReadmeFile>
    ''')
    if nuget_description():
        print_csproj(2, f'<Description>{nuget_description()}</Description>')
    if nuget_tags():
        print_csproj(2, f'<PackageTags>{nuget_tags()}</PackageTags>')
    if nuget_icon():
        print_csproj(2, f'<PackageIcon>{nuget_icon()}</PackageIcon>')
    print_csproj(1, '''\
        </PropertyGroup>
        <ItemGroup>
          <None Include="../README.md" Pack="true" PackagePath="/" />
    ''')
    if nuget_icon():
        print_csproj(2, f'<None Include="{nuget_icon()}" Pack="true" PackagePath="/" />')
    print_csproj(1, '</ItemGroup>')
    if capture_output(dependencies):
        print_csproj(1, '<ItemGroup>')
        dependencies()
        print_csproj(1, '</ItemGroup>')
    print('</Project>')

def test_csproj():
    print_lines(f'''\
        <!-- Generated by scripts/configure.py -->
        <Project Sdk="Microsoft.NET.Sdk">
          <PropertyGroup>
            <TargetFramework>net{target_framework()}</TargetFramework>
            <IsPackable>false</IsPackable>
            <RootNamespace>{root_namespace()}</RootNamespace>
          </PropertyGroup>
          <ItemGroup>
            <ProjectReference Include="../{root_namespace()}/{root_namespace()}.csproj" />
          </ItemGroup>
          <ItemGroup>
    ''')
    test_dependencies()
    print_csproj(0, '''\
          </ItemGroup>
        </Project>
    ''')

def guid(project):
    author = uuid.uuid5(uuid.NAMESPACE_DNS, 'machinezoo.com')
    repository = uuid.uuid5(author, repository_name())
    return uuid.uuid5(repository, project)

def sln():
    print_lines('''\
        # Generated by scripts/configure.py
        Microsoft Visual Studio Solution File, Format Version 12.00
    ''')
    for project in sln_projects():
        print_lines(f'''\
            Project("{{{guid(project)}}}") = "{project}", "{project}/{project}.csproj", "{{{guid(project)}}}"
            EndProject
        ''')
    print_lines('''\
        Global
            GlobalSection(SolutionConfigurationPlatforms) = preSolution
                Debug|Any CPU = Debug|Any CPU
                Release|Any CPU = Release|Any CPU
            EndGlobalSection
            GlobalSection(ProjectConfigurationPlatforms) = postSolution
    ''', tabify=True)
    for project in sln_projects():
        print_lines(f'''\
            {{{guid(project)}}}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
            {{{guid(project)}}}.Debug|Any CPU.Build.0 = Debug|Any CPU
            {{{guid(project)}}}.Release|Any CPU.ActiveCfg = Release|Any CPU
            {{{guid(project)}}}.Release|Any CPU.Build.0 = Release|Any CPU
        ''', indent='\t\t')
    print_lines('''\
            EndGlobalSection
        EndGlobal
    ''', tabify=True)

def generate():
    print_to(project_directory()/'.gitignore', gitignore)
    if is_opensource():
        print_to(project_directory()/'LICENSE', license)
        print_to(project_directory()/'NOTICE', notice)
    if nuget_release():
        print_to(workflows_directory()/'release.yml', release_workflow)
    print_to(project_directory()/root_namespace()/f'{root_namespace()}.csproj', csproj)
    if has_tests():
        print_to(project_directory()/f'{root_namespace()}.Tests'/f'{root_namespace()}.Tests.csproj', test_csproj)
    print_to(project_directory()/f'{root_namespace()}.sln', sln)
    if is_opensource():
        print_to(project_directory()/'CONTRIBUTING.md', contribution_guidelines)
    print_to(project_directory()/'README.md', readme)
    remove_obsolete(workflows_directory()/'nuget-release.yml')
    print(f'Updated {pretty_name()} configuration.')