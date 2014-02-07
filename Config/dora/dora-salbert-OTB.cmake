set (ENV{DISPLAY} ":0.0")
set (ENV{LANG} "C")

set (CTEST_BUILD_CONFIGURATION "Debug")

set (CTEST_SOURCE_DIRECTORY "$ENV{HOME}/dev/source/OTB")
set (CTEST_BINARY_DIRECTORY "$ENV{HOME}/dev/build/OTB")

set (CTEST_CMAKE_GENERATOR  "Unix Makefiles" )
set (CTEST_CMAKE_COMMAND "cmake" )
set (CTEST_BUILD_COMMAND "/usr/bin/make -j4 -i -k install" )
set (CTEST_SITE "dora.c-s.fr" )
set (CTEST_BUILD_NAME "salbert_Ubuntu-12.04_x86_64_${CTEST_BUILD_CONFIGURATION}")
set (CTEST_HG_COMMAND "/usr/bin/hg")
set (CTEST_HG_UPDATE_OPTIONS "")
set (CTEST_USE_LAUNCHERS ON)

set (OTB_INSTALL_PREFIX "$ENV{HOME}/dev/install/OTB")

set (OTB_INITIAL_CACHE "
BUILDNAME:STRING=${CTEST_BUILD_NAME}
SITE:STRING=${CTEST_SITE}

OTB_DATA_USE_LARGEINPUT:BOOL=ON
OTB_DATA_LARGEINPUT_ROOT:STRING=/home/otbval/Data/OTB-LargeInput
OTB_DATA_ROOT:STRING=$ENV{HOME}/dev/source/OTB-Data

CMAKE_C_FLAGS:STRING= -fPIC -Wall
CMAKE_CXX_FLAGS:STRING= -fPIC -Wall
CMAKE_BUILD_TYPE:STRING=${CTEST_BUILD_CONFIGURATION}

BUILD_TESTING:BOOL=OFF
BUILD_EXAMPLES:BOOL=OFF
BUILD_APPLICATIONS:BOOL=ON

OTB_WRAP_QT:BOOL=ON
OTB_USE_CURL:BOOL=ON
OTB_USE_PQXX:BOOL=OFF
# ITK_USE_PATENTED:BOOL=ON
#OTB_USE_PATENTED:BOOL=ON
#BOOST_ROOT:PATH=$ENV{HOME}/OTB-OUTILS/boost/install_1_49_0

OTB_USE_EXTERNAL_BOOST:BOOL=ON
OTB_USE_EXTERNAL_EXPAT:BOOL=ON
OTB_USE_EXTERNAL_FLTK:BOOL=OFF
OTB_USE_EXTERNAL_ITK:BOOL=ON

ITK_DIR:PATH=/home/otbval/Dashboard/experimental/build/ITKv4-RelWithDebInfo
#FLTK_DIR:PATH=$ENV{HOME}/OTB-OUTILS/fltk/binaries-linux-shared-release-fltk-1.1.9

USE_FFTWD:BOOL=OFF
USE_FFTWF:BOOL=OFF
# OTB_GL_USE_ACCEL:BOOL=ON
# ITK_USE_REVIEW:BOOL=ON
# ITK_USE_OPTIMIZED_REGISTRATION_METHODS:BOOL=ON 
# OTB_USE_MAPNIK:BOOL=OFF

# MAPNIK_INCLUDE_DIR:PATH=/ORFEO/otbval/OTB-OUTILS/mapnik/install/include
# MAPNIK_LIBRARY:FILEPATH=/ORFEO/otbval/OTB-OUTILS/mapnik/install/lib/libmapnik.so

CMAKE_INSTALL_PREFIX:STRING=${OTB_INSTALL_PREFIX}

# GDALCONFIG_EXECUTABLE:FILEPATH=${OTB_GDAL_INSTALL_DIR}/bin/gdal-config
# GDAL_CONFIG:FILEPATH=${OTB_GDAL_INSTALL_DIR}/bin/gdal-config
# GDAL_INCLUDE_DIR:STRING=${OTB_GDAL_INSTALL_DIR}/include
# GDAL_LIBRARY:FILEPATH=${OTB_GDAL_INSTALL_DIR}/lib/libgdal.so
")

set (CTEST_NOTES_FILES
${CTEST_SCRIPT_DIRECTORY}/${CTEST_SCRIPT_NAME
${CTEST_BINARY_DIRECTORY}/CMakeCache.txt
)

execute_process(COMMAND ${CTEST_CMAKE_COMMAND} -E remove_directory ${OTB_INSTALL_PREFIX})
execute_process(COMMAND ${CTEST_CMAKE_COMMAND} -E make_directory ${OTB_INSTALL_PREFIX})
ctest_empty_binary_directory (${CTEST_BINARY_DIRECTORY})

ctest_start(Experimental)
ctest_update(SOURCE "${CTEST_SOURCE_DIRECTORY}")
file(WRITE "${CTEST_BINARY_DIRECTORY}/CMakeCache.txt" ${OTB_INITIAL_CACHE})
ctest_configure (BUILD "${CTEST_BINARY_DIRECTORY}")
ctest_read_custom_files(${CTEST_BINARY_DIRECTORY})
ctest_build (BUILD "${CTEST_BINARY_DIRECTORY}")
ctest_test (BUILD "${CTEST_BINARY_DIRECTORY}" PARALLEL_LEVEL 6)
ctest_submit ()

