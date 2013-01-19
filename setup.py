import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install


class MyInstall(install):
    def run(self):
        projpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'creditservices')
        print 'Generating MO files in %s' % projpath
        subprocess.call(['django-admin.py', 'compilemessages'],
                        cwd=projpath)
        install.run(self)

setup(
    name='django-credit-services',
    version='0.1',
    description='Allows users to prepay some services.',
    author='Vaclav Klecanda',
    author_email='vencax77@gmail.com',
    url='www.vxk.cz',
    packages=find_packages(),
    include_package_data=True,
    cmdclass={'install': MyInstall},
)
