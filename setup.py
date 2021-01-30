from distutils.core import setup
setup(
  name='fregeindexerlib',
  packages=['fregeindexerlib'],
  version='0.4.0',
  license='gpl-3.0',
  description='Library for a indexers in a Frege project',
  author='Michał Piotrowski',
  author_email='michal@piotrowski.biz.pl',
  url='https://github.com/Software-Engineering-Jagiellonian/frege-indexer-lib',
  download_url='https://github.com/Software-Engineering-Jagiellonian/frege-indexer-lib/archive/v_0.4.0.tar.gz',
  keywords=['Jagiellonian University', 'Frege', 'Indexer'],
  install_requires=[
          'pika',
          'sqlalchemy',
          'psycopg2-binary'
      ],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 3'
  ],
)
