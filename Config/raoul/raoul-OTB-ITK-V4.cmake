# Client maintainer: julien.malik@c-s.fr

SET (CTEST_SOURCE_DIRECTORY "C:/Users/jmalik/Dashboard/src/OTB-ITKv4")
SET (CTEST_BINARY_DIRECTORY "C:/Users/jmalik/Dashboard/build/OTB-ITKv4-Release-MVSC2010")

SET (CTEST_CMAKE_GENERATOR  "Visual Studio 10" )
SET (CTEST_CMAKE_COMMAND "C:/Program Files (x86)/CMake 2.8/bin/cmake.exe")
SET (CTEST_SITE "raoul.c-s.fr" )
SET (CTEST_BUILD_NAME "OTB-ITKv4-Win7-MVSC2010-Release-Static")
SET (CTEST_BUILD_CONFIGURATION "Release")
SET (CTEST_HG_COMMAND "C:/Program Files (x86)/Mercurial/hg.exe")
SET (CTEST_HG_UPDATE_OPTIONS "-C")

SET (OTB_INITIAL_CACHE "
BUILDNAME:STRING=${CTEST_BUILD_NAME}
SITE:STRING=${CTEST_SITE}

BUILD_TESTING:BOOL=OFF
BUILD_EXAMPLES:BOOL=ON
BUILD_APPLICATIONS:BOOL=ON

OTB_WRAP_PYTHON:BOOL=OFF
OTB_WRAP_QT:BOOL=ON

OTB_USE_CPACK:BOOL=OFF

OTB_DATA_ROOT:STRING=C:/Users/jmalik/Dashboard/src/OTB-Data
OTB_DATA_USE_LARGEINPUT:BOOL=OFF
OTB_DATA_LARGEINPUT_ROOT:PATH=C:/Users/jmalik/Dashboard/src/OTB-LargeInput

OTB_USE_EXTERNAL_FLTK:BOOL=OFF
OTB_USE_EXTERNAL_OSSIM:BOOL=ON

OTB_USE_CURL:BOOL=ON
OTB_USE_EXTERNAL_EXPAT:BOOL=ON
OTB_USE_LIBLAS:BOOL=ON
OTB_USE_EXTERNAL_LIBLAS:BOOL=ON
OTB_USE_GETTEXT:BOOL=OFF
OTB_USE_JPEG2000:BOOL=ON

CMAKE_INCLUDE_PATH:PATH=$ENV{OSGEO4W_ROOT}/include
CMAKE_LIBRARY_PATH:PATH=$ENV{OSGEO4W_ROOT}/lib

OTB_USE_EXTERNAL_ITK:BOOL=ON
ITK_DIR:PATH=C:/Users/jmalik/Dashboard/build/ITKv4-Release
")

#remove build dir
ctest_empty_binary_directory (${CTEST_BINARY_DIRECTORY})

SET (CTEST_NOTES_FILES
${CTEST_SCRIPT_DIRECTORY}/${CTEST_SCRIPT_NAME}
${CTEST_BINARY_DIRECTORY}/CMakeCache.txt
)

ctest_start(Experimental)
ctest_update(SOURCE "${CTEST_SOURCE_DIRECTORY}")
file(WRITE "${CTEST_BINARY_DIRECTORY}/CMakeCache.txt" ${OTB_INITIAL_CACHE})
ctest_configure (BUILD "${CTEST_BINARY_DIRECTORY}")
ctest_read_custom_files(${CTEST_BINARY_DIRECTORY})
#ctest_submit (PARTS Start Update Configure)
ctest_build (BUILD "${CTEST_BINARY_DIRECTORY}")
#ctest_submit (PARTS Start Update Configure Build)
ctest_test (BUILD "${CTEST_BINARY_DIRECTORY}" PARALLEL_LEVEL 4)
ctest_submit ()
