from setuptools import setup, find_packages

setup(
    name="concoursekit",
    author="Anthony Hawkins",
    author_email="ahawkins.mail@gmail.com",
    version="0.1.3",
    description="A Concourse CI Pipeline Generator Utility.",
    keywords=["concourse", "yaml generator", "pipeline manager", "ci", "cd"],
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[ 
        "pytoml",
        "yamlmaker",
        "pytest",
        "pyyaml"
    ],
    entry_points='''
        [console_scripts]
        cck=concoursekit:main
    ''',
    classifiers=[
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
    ],
    url="https://github.com/anthonyhawkins/concourse-kit"
)