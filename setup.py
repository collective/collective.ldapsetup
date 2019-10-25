from setuptools import setup, find_packages

version = "1.0.0.dev0"

setup(
    name="collective.ldapsetup",
    version=version,
    description="Example LDAP setup",
    long_description=open("README.rst").read() + "\n" + open("CHANGES.rst").read(),
    # Get more strings from https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.1",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="collective ldap",
    author="Zest Software",
    author_email="info@zestsoftware.nl",
    url="https://github.com/collective/pas.plugins.ldap",
    license="GPL",
    packages=find_packages(),
    namespace_packages=["collective"],
    include_package_data=True,
    zip_safe=False,
    install_requires=["setuptools", "node.ext.ldap >= 1.0b11", "pas.plugins.ldap>=1.5.4", "bda.cache[libmc]"],
    entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
)
