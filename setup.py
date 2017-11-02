from setuptools import setup, find_packages
import fondum

entry_points = {
    "console_scripts": [
        "fondum = fondum.cli:main",
    ]
}

# with open("requirements.txt") as f:
#     requires = [l for l in f.read().splitlines() if l]
requires = []

setup(
    name='Fondum',
    version=fondum.__version__,
    packages=find_packages(),
    include_package_data=True,
    description='Super-Framework for Flask/Oauth/NGINX/Docker/Unicorn/MongoDB (and More!)',
    long_description=open('README.md').read(),
    url='https://github.com/JohnAD/fondum',
    author='John Dupuy',
    author_email='john@cattailcreek9.com',
    license='MIT',
    keywords='flask oauth nginx docker unicorn mongodb mongoengine super framework generator',
    install_requires=requires,
    entry_points=entry_points,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
