from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(name='ecs-logger',
      description='ECS Logger',
      long_description=long_description,
      long_description_content_type="text/markdown",
      version='0.0.2',
      url='https://github.com/hampsterx/ecs-logger',
      author='Tim van der Hulst',
      author_email='tim.vdh@gmail.com',
      license='Apache2',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3'
      ],
      packages=['ecs_logger'],
      install_requires=[
            'requests>=2',
            'coloredlogs==10.0'
      ]

)