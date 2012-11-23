#!/usr/bin/env python
from distutils.core import setup
setup(
	name='qino',
	description='Arduino PyQt4 IDE for ino',
	author='Igor Maculan',
	author_email='n3wtron@gmail.com',
	packages=['qino','qino.uiImpl'],
	licence='GPLv3',
	keywords='arduino linux macosx ide python pyQt4',
	install_requires=['ino', 'pyqt4'],
	classifiers=[
				"Environment :: X11 Applications :: Qt",
				"Intended Audience :: Developers",
				"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		        "Operating System :: OS Independent",
		        "Programming Language :: Python",
		        "Topic :: Software Development :: Embedded Systems",
			]
)
