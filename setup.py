from setuptools import setup, find_packages

print find_packages()

setup(
    name='django-credit-services',
    version='0.1',
    description='Allows users to prepay some services.',
    author='Vaclav Klecanda',
    author_email='vencax77@gmail.com',
    url='https://github.com/applecat/django-simple-poll',
    packages=find_packages(),
    include_package_data=True,
)
