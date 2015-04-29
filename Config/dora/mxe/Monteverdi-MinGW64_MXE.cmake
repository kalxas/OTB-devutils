# Maintainers : OTB developers team
# Cross compilation of OTB library using MXE (M cross environment)
set(dashboard_model Nightly)
set(CTEST_DASHBOARD_ROOT "/home/otbval/Dashboard")
set(CTEST_SITE "dora.c-s.fr")
set(CTEST_BUILD_CONFIGURATION Release)
set(MXE_ROOT "/home/otbval/Tools/mxe")
set(MXE_TARGET_ARCH "x86_64")
set(PROJECT "Monteverdi")
set(dashboard_source_name "src/Monteverdi")
set(dashboard_binary_name "build/${PROJECT}-${MXE_TARGET_ARCH}-MXE")

include(${CTEST_SCRIPT_DIRECTORY}/../../mxe_common.cmake)

macro(dashboard_hook_init)
set(dashboard_cache "${dashboard_cache}

CMAKE_C_FLAGS:STRING=-Wall -Wshadow -Wno-uninitialized -Wno-unused-variable

CMAKE_CXX_FLAGS:STRING=-Wall -Wno-deprecated -Wno-uninitialized -Wno-unused-variable

BUILD_TESTING:BOOL=OFF

")
endmacro()

set(dashboard_no_test 1)
