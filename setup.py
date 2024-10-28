from setuptools import find_packages, setup

setup(
    name='l2p',
    version='0.1.0',
    packages=find_packages(),
    description='Library to connect LLMs and planning tasks',
    author='Marcus Tantakoun',
    author_email='mtantakoun@gmail.com',
    url='https://github.com/MarcusTantakoun/L2P-Library-Kit.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ], 
    python_requires='>=3.6',
)