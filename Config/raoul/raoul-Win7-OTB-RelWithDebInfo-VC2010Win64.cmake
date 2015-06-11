# Client maintainer: julien.malik@c-s.fr
set(OTB_PROJECT OTB) # OTB / Monteverdi / Monteverdi2
set(OTB_ARCH amd64) # x86 / amd64
set(CTEST_BUILD_CONFIGURATION RelWithDebInfo)
set(CTEST_BUILD_TARGET INSTALL)
include(${CTEST_SCRIPT_DIRECTORY}/raoul_common.cmake)


set(OSGE04W_TESTING "C:/TEST_PKG_x64") 

macro(dashboard_hook_init)
  set(dashboard_cache "${dashboard_cache}
  
CMAKE_INSTALL_PREFIX:PATH=${CTEST_DASHBOARD_ROOT}/install/${OTB_PROJECT}-vc10-${OTB_ARCH}-${CTEST_BUILD_CONFIGURATION}

BUILD_TESTING:BOOL=ON
BUILD_EXAMPLES:BOOL=OFF

OTB_WRAP_PYTHON:BOOL=ON
OTB_WRAP_JAVA:BOOL=ON
OTB_WRAP_QT:BOOL=ON

OTB_DATA_ROOT:STRING=${CTEST_DASHBOARD_ROOT}/src/OTB-Data
OTB_DATA_USE_LARGEINPUT:BOOL=ON
OTB_DATA_LARGEINPUT_ROOT:PATH=${CTEST_DASHBOARD_ROOT}/src/OTB-LargeInput

CMAKE_PREFIX_PATH:PATH=${OSGEO4W_ROOT}

SWIG_EXECUTABLE:FILEPATH=${CTEST_DASHBOARD_ROOT}/tools/swigwin-3.0.5/swig.exe

PYTHON_EXECUTABLE:FILEPATH=${OSGEO4W_ROOT}/bin/python.exe
PYTHON_INCLUDE_DIR:PATH=${OSGEO4W_ROOT}/apps/Python27/include
PYTHON_LIBRARY:FILEPATH=${OSGEO4W_ROOT}/apps/Python27/libs/python27.lib

OTB_USE_CURL:BOOL=ON
OTB_USE_LIBKML:BOOL=ON
OTB_USE_LIBSVM:BOOL=ON
OTB_USE_MUPARSER:BOOL=ON
OTB_USE_MUPARSERX:BOOL=ON
OTB_USE_OPENCV:BOOL=ON
OTB_USE_OPENJPEG:BOOL=ON
OTB_USE_QT4:BOOL=ON

OpenJPEG_DIR:PATH=${OSGEO4W_ROOT}/lib/openjpeg-2.0

Boost_INCLUDE_DIR:PATH=${OSGE04W_TESTING}/include/boost-1_56
Boost_LIBRARY_DIR:PATH=${OSGE04W_TESTING}/lib

ITK_DIR:PATH=${OSGE04W_TESTING}/lib/cmake/ITK-4.7

OpenCV_DIR:PATH=${OSGE04W_TESTING}/share/OpenCV

LIBSVM_INCLUDE_DIR:PATH=${OSGE04W_TESTING}/include
LIBSVM_LIBRARY:FILEPATH=${OSGE04W_TESTING}/lib/libsvm.lib

LIBKML_INCLUDE_DIR:PATH=${OSGE04W_TESTING}/include
LIBKML_BASE_LIBRARY:FILEPATH=${OSGE04W_TESTING}/lib/kmlbase.lib;${OSGEO4W_ROOT}/lib/libexpat.lib
LIBKML_CONVENIENCE_LIBRARY:FILEPATH=${OSGE04W_TESTING}/lib/kmlconvenience.lib
LIBKML_DOM_LIBRARY:FILEPATH=${OSGE04W_TESTING}/lib/kmldom.lib
LIBKML_ENGINE_LIBRARY:FILEPATH=${OSGE04W_TESTING}/lib/kmlengine.lib
LIBKML_MINIZIP_LIBRARY:FILEPATH=${OSGE04W_TESTING}/lib/minizip.lib;${OSGEO4W_ROOT}/lib/zlib.lib
LIBKML_REGIONATOR_LIBRARY:FILEPATH=${OSGE04W_TESTING}/lib/kmlregionator.lib
LIBKML_XSD_LIBRARY:FILEPATH=${OSGE04W_TESTING}/lib/kmlxsd.lib

MUPARSERX_INCLUDE_DIR:PATH=${OSGE04W_TESTING}/include
MUPARSERX_LIBRARY:FILEPATH=${OSGE04W_TESTING}/lib/muparserx.lib

MUPARSER_INCLUDE_DIR:PATH=${OSGE04W_TESTING}/include
MUPARSER_LIBRARY:FILEPATH=${OSGE04W_TESTING}/lib/muparser.lib

TINYXML_INCLUDE_DIR:PATH=${OSGE04W_TESTING}/include
TINYXML_LIBRARY:FILEPATH=${OSGE04W_TESTING}/lib/tinyxml.lib


    ")
endmacro()

include(${CTEST_SCRIPT_DIRECTORY}/../otb_common.cmake)
