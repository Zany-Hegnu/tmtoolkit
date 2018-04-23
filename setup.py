"""
tmtoolkit setuptools based setup module
"""

from setuptools import setup
import tmtoolkit

setup(
    name=tmtoolkit.__title__,
    version=tmtoolkit.__version__,
    description='Text Mining and Topic Modeling Toolkit',
    long_description="""tmtoolkit is a set of tools for text mining and topic modeling with Python. It contains
functions for text preprocessing like lemmatization, stemming or POS tagging especially for English and German
texts. Preprocessing is done in parallel by using all available processors on your machine. The topic modeling
features include topic model evaluation metrics, allowing to calculate models with different parameters in parallel
and comparing them (e.g. in order to find the best number of topics for a given set of documents). Topic models can
be generated in parallel for different copora and/or parameter sets using the LDA implementations either from
lda, scikit-learn or gensim.""",
    url='https://github.com/WZBSocialScienceCenter/tmtoolkit',

    author=tmtoolkit.__author__,
    author_email='markus.konrad@wzb.eu',

    license=tmtoolkit.__license__,

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',

        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',

        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],

    keywords='textmining textanalysis text mining analysis preprocessing topicmodeling topic modeling evaluation',

    packages=['tmtoolkit', 'tmtoolkit.topicmod', 'ClassifierBasedGermanTagger'],
    include_package_data=True,
    python_requires='>=2.7',
    install_requires=['six>=1.10.0', 'numpy>=1.13.0', 'scipy>=1.0.0', 'pandas>=0.20.0', 'nltk>=3.0.0', 'pyphen>=0.9.0'],
    extras_require={
        'improved_german_lemmatization':  ['pattern'],
        'excel_export': ['openpyxl'],
        'plotting': ['matplotlib'],
        'wordclouds': ['wordcloud', 'Pillow'],
        'topic_modeling_lda': ['lda'],
        'topic_modeling_sklearn': ['scikit-learn>=0.18.0'],
        'topic_modeling_gensim': ['gensim'],
        'topic_modeling_eval_griffiths_2004': ['gmpy2'],
        'topic_modeling_coherence': ['gensim>=3.4.0'],
    }
)
