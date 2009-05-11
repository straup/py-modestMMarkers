# $Id: setup.py,v 1.1 2009/05/09 17:05:26 asc Exp $

# http://peak.telecommunity.com/DevCenter/setuptools
# http://ianbicking.org/docs/setuptools-presentation/

try:
    from setuptools import setup, find_packages
except:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

readme = file('README','rb').read()

local__name = 'modestMMarkers'
local__version = '0.2'
local__url = 'http://www.aaronland.info/python/%s' % local__name
local__download = '%s/%s-%s.tar.gz' % (local__url, local__name, local__version)

setup(
    name = local__name,
    version = local__version,

    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    exclude_package_data={'':["examples", "README", "ez_setup*"]},

    # TO DO: proper packages for ModestMaps...
    
    install_requires = ['pycairo', 'Imaging', 'elementtree'],
    dependency_links = ['http://www.pythonware.com/products/pil/'],

    author = "Aaron Straup Cope",
    author_email = "aaron@aaronland.net",
    description = "",
    long_description=readme,
    
    license = "BSD",
    keywords = "maps modestmaps papernet pdf pocketmap print",
    url = local__url,
    download_url = local__download,
    
    # Uncomment when you need to sanity check the
    # stuff that actually gets installed...
    zip_safe=False    
    )
