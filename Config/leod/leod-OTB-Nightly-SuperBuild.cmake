# Client maintainer: julien.malik@c-s.fr
set(dashboard_model Nightly)
set(CTEST_BUILD_CONFIGURATION Release)
set(CTEST_BUILD_NAME "MacOSX10.10-SuperBuild")
set(dashboard_no_install 1)
include(${CTEST_SCRIPT_DIRECTORY}/leod_common.cmake)

string(TOLOWER ${dashboard_model} lcdashboard_model)

set(dashboard_root_name "tests")
set(dashboard_source_name "${lcdashboard_model}/OTB-${CTEST_BUILD_CONFIGURATION}/src/SuperBuild")
set(dashboard_binary_name "${lcdashboard_model}/OTB-SuperBuild/build")

set(OTB_INSTALL_PREFIX ${CTEST_DASHBOARD_ROOT}/${lcdashboard_model}/OTB-SuperBuild/install)

set(dashboard_git_url "https://git@git.orfeo-toolbox.org/git/otb.git")
set(dashboard_update_dir ${CTEST_DASHBOARD_ROOT}/${lcdashboard_model}/OTB-${CTEST_BUILD_CONFIGURATION}/src)
set(dashboard_git_branch release-5.4)

set(CTEST_NIGHTLY_START_TIME "20:00:00 CEST")
set(CTEST_DROP_METHOD "http")
set(CTEST_DROP_SITE "dash.orfeo-toolbox.org")
set(CTEST_DROP_LOCATION "/submit.php?project=OTB")
set(CTEST_DROP_SITE_CDASH TRUE)

list(APPEND CTEST_TEST_ARGS
  BUILD ${CTEST_DASHBOARD_ROOT}/${dashboard_binary_name}/OTB/build
)
list(APPEND CTEST_NOTES_FILES
  ${CTEST_DASHBOARD_ROOT}/${dashboard_binary_name}/OTB/build/CMakeCache.txt
  ${CTEST_DASHBOARD_ROOT}/${dashboard_binary_name}/OTB/build/otbConfigure.h
)

set(GDAL_EXTRA_OPT "--with-gif=/opt/local")

macro(dashboard_hook_init)
  set(dashboard_cache "${dashboard_cache}
CMAKE_INSTALL_PREFIX:PATH=${OTB_INSTALL_PREFIX}
CMAKE_BUILD_TYPE:STRING=${CTEST_BUILD_CONFIGURATION}
OTB_DATA_ROOT:PATH=$ENV{HOME}/Data/OTB-Data
DOWNLOAD_LOCATION:PATH=$ENV{HOME}/Data/SuperBuild-archives
CTEST_USE_LAUNCHERS:BOOL=${CTEST_USE_LAUNCHERS}

USE_SYSTEM_ZLIB:BOOL=OFF
USE_SYSTEM_PNG:BOOL=OFF
USE_SYSTEM_SQLITE:BOOL=OFF
USE_SYSTEM_JPEG:BOOL=OFF
USE_SYSTEM_TIFF:BOOL=OFF
USE_SYSTEM_GEOTIFF:BOOL=OFF
USE_SYSTEM_EXPAT:BOOL=OFF
USE_SYSTEM_OPENJPEG:BOOL=OFF
USE_SYSTEM_GEOS:BOOL=OFF
USE_SYSTEM_OPENSSL:BOOL=OFF
USE_SYSTEM_CURL:BOOL=OFF
USE_SYSTEM_BOOST:BOOL=OFF
USE_SYSTEM_LIBKML:BOOL=OFF
USE_SYSTEM_PROJ:BOOL=OFF
USE_SYSTEM_GDAL:BOOL=OFF

USE_SYSTEM_FFTW:BOOL=OFF
USE_SYSTEM_ITK:BOOL=OFF

USE_SYSTEM_OPENTHREADS:BOOL=OFF
USE_SYSTEM_OSSIM:BOOL=OFF

USE_SYSTEM_LIBSVM:BOOL=OFF

USE_SYSTEM_OPENCV:BOOL=OFF

USE_SYSTEM_TINYXML:BOOL=OFF

USE_SYSTEM_GLUT:BOOL=OFF
USE_SYSTEM_GLFW:BOOL=OFF
USE_SYSTEM_GLEW:BOOL=OFF

USE_SYSTEM_QT4:BOOL=OFF
USE_SYSTEM_QWT:BOOL=OFF

OTB_USE_CURL:BOOL=ON

OTB_USE_MUPARSER:BOOL=ON

OTB_USE_MUPARSERX:BOOL=ON

OTB_USE_QT4:BOOL=ON

OTB_USE_OPENGL:BOOL=ON
OTB_USE_GLEW:BOOL=ON
OTB_USE_GLEW:BOOL=ON
OTB_USE_GLUT:BOOL=ON

OTB_USE_OPENJPEG:BOOL=OFF

OTB_USE_6S:BOOL=ON

OTB_USE_LIBKML:BOOL=ON

OTB_USE_LIBSVM:BOOL=ON

OTB_USE_MAPNIK:BOOL=OFF

OTB_USE_OPENCV:BOOL=ON

OTB_USE_SIFTFAST:BOOL=ON

ENABLE_MONTEVERDI:BOOL=ON

ENABLE_OTB_LARGE_INPUTS:BOOL=ON
OTB_DATA_LARGEINPUT_ROOT:PATH=$ENV{HOME}/Data/OTB-LargeInput
GDAL_SB_EXTRA_OPTIONS:STRING=${GDAL_EXTRA_OPT}
OTB_WRAP_PYTHON:BOOL=OFF
OTB_WRAP_JAVA:BOOL=OFF
BUILD_TESTING:BOOL=ON
")
endmacro()

macro(dashboard_hook_test)
# before testing, set the DYLD_LIBRARY_PATH
set(ENV{DYLD_LIBRARY_PATH} ${OTB_INSTALL_PREFIX}/lib)
endmacro()

execute_process(COMMAND ${CMAKE_COMMAND} -E remove_directory ${OTB_INSTALL_PREFIX})
execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory ${OTB_INSTALL_PREFIX})
execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory ${OTB_INSTALL_PREFIX}/lib)
execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory ${OTB_INSTALL_PREFIX}/bin)
execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory ${OTB_INSTALL_PREFIX}/include)

include(${CTEST_SCRIPT_DIRECTORY}/../otb_common.cmake)
