#!/usr/bin/env python
from setuptools import setup
setup(
	name='qino',
	description='Arduino PyQt4 IDE for ino',
	version='0.0.1',
	url='http://pypi.python.org/pypi/qino/',
	author='Igor Maculan',
	author_email='n3wtron@gmail.com',
	packages=['qino','qino.uiImpl'],
	license='GPLv3',
	keywords='arduino linux macosx ide python pyQt4',
	requires=['ino', 'pyqt4'],
	classifiers=[
				"Environment :: X11 Applications :: Qt",
				"Intended Audience :: Developers",
				"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		        "Operating System :: OS Independent",
		        "Programming Language :: Python",
		        "Topic :: Software Development :: Embedded Systems",
		        "Development Status :: 4 - Beta"
			]
)
