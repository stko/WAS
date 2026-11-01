from setuptools import setup, find_packages

setup(
    name="WAS",
    version="0.0.1",
    description="WAS - The Web Application Skeleton framework for building web applications with plugins",
    license="MIT",
    packages=find_packages(),
    install_requires=["Flask", "Flask-Sockets"],
    author="Steffen Köhler",
    author_email="steffen@koehlers.de",
    keywords=["web", "applications", "plugins"],
    url="https://github.com/stko/WAS",
)
