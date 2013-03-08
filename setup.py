from distutils.core import setup
setup(
    name='Cloud Images Query',
    version='0.1.0',
    packages=['cloud_images'],
    author='Chris R. Bennett',
    author_email='source@mruser.com',
    url='https://github.com/mruser/cloud_images/',
    description='Query tool for Ubuntu cloud-images',
    long_description='',
    license='License :: OSI Approved :: MIT License',
    requires=['boto (>=2.8)', 'urllib3 (>=1.5)', 'argparse'],
    scripts=['scripts/cloud_images'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Software Distribution'
    ]
)
