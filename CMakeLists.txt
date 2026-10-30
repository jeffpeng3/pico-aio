cmake_minimum_required(VERSION 3.13)

option(ENABLE_EMULATION "Build the host emulation binary" OFF)
set(PICO_AIO_USB_PROFILE "default" CACHE STRING "USB profile: default, local, or yubikey5")
set(PICO_AIO_USB_VID "" CACHE STRING "Override USB VID")
set(PICO_AIO_USB_PID "" CACHE STRING "Override USB PID")
set(PICO_AIO_USB_MANUFACTURER "" CACHE STRING "Override USB manufacturer string")
set(PICO_AIO_USB_PRODUCT "" CACHE STRING "Override USB product string")

set(PICO_AIO_SDK_DIR "${CMAKE_CURRENT_SOURCE_DIR}/third_party/pico-keys-sdk" CACHE PATH "Pico Keys SDK source")
set(PICO_AIO_FIDO_DIR "${CMAKE_CURRENT_SOURCE_DIR}/third_party/pico-fido" CACHE PATH "Pico FIDO source")
set(PICO_AIO_OPENPGP_DIR "${CMAKE_CURRENT_SOURCE_DIR}/third_party/pico-openpgp" CACHE PATH "Pico OpenPGP source")
set(PICO_AIO_PICO_SDK_DIR "${CMAKE_CURRENT_SOURCE_DIR}/third_party/pico-sdk" CACHE PATH "Pico SDK source")

if(NOT PICO_SDK_PATH)
    set(PICO_SDK_PATH "${PICO_AIO_PICO_SDK_DIR}" CACHE PATH "Raspberry Pi Pico SDK" FORCE)
endif()
if(NOT PICO_BOARD)
    set(PICO_BOARD "pico2" CACHE STRING "Pico board")
endif()

string(TOLOWER "${PICO_AIO_USB_PROFILE}" PICO_AIO_USB_PROFILE_LC)
set(USB_MANUFACTURER "Pico AIO")
set(USB_PRODUCT "Pico AIO")

if(PICO_AIO_USB_PROFILE_LC STREQUAL "default")
    set(USB_VID 0xFEFF)
    set(USB_PID 0xFCFD)
elseif(PICO_AIO_USB_PROFILE_LC STREQUAL "local")
    set(USB_VID 0x2E8A)
    set(USB_PID 0x10FE)
elseif(PICO_AIO_USB_PROFILE_LC STREQUAL "yubikey5")
    set(VIDPID "Yubikey5" CACHE STRING "Known VID/PID profile" FORCE)
    set(USB_VID 0x1050)
    set(USB_PID 0x0407)
    set(USB_MANUFACTURER "Yubico")
    set(USB_PRODUCT "Yubico YubiKey")
else()
    message(FATAL_ERROR "Unknown PICO_AIO_USB_PROFILE '${PICO_AIO_USB_PROFILE}'")
endif()

if(PICO_AIO_USB_VID)
    set(USB_VID "${PICO_AIO_USB_VID}")
endif()
if(PICO_AIO_USB_PID)
    set(USB_PID "${PICO_AIO_USB_PID}")
endif()
if(PICO_AIO_USB_MANUFACTURER)
    set(USB_MANUFACTURER "${PICO_AIO_USB_MANUFACTURER}")
endif()
if(PICO_AIO_USB_PRODUCT)
    set(USB_PRODUCT "${PICO_AIO_USB_PRODUCT}")
endif()

if(NOT ENABLE_EMULATION)
    set(PICO_USE_FASTEST_SUPPORTED_CLOCK 1)
    include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/pico_sdk_import.cmake)
endif()

project(pico_fido2 C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

find_package(Git REQUIRED)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/check_patches.cmake)

if(NOT ENABLE_EMULATION)
    add_executable(pico_fido2)
else()
    add_executable(pico_fido2)
endif()

set(USB_ITF_HID 1)
set(USB_ITF_CCID 1)
set(USB_ITF_WCID 1)
set(ENABLE_LIBCVC 1)
set(ENABLE_EDDSA 1)
set(ENABLE_OATH_APP 1)
set(ENABLE_OTP_APP 1)
set(ENABLE_ADMINLESS_MODE 1)

include(${PICO_AIO_SDK_DIR}/picokeys_sdk_import.cmake)

add_compile_definitions(
    ENABLE_OATH_APP=1
    ENABLE_OTP_APP=1
    ENABLE_ADMINLESS_MODE=1
    ENABLE_POWER_ON_RESET=1
    PICO_FIDO2_COMBINED_FILES=1
    PICO_BUILD_NUMBER=1
)
if(ENABLE_EMULATION)
    add_compile_definitions(__FOR_CI=1)
endif()

file(GLOB FIDO_SOURCES CONFIGURE_DEPENDS ${PICO_AIO_FIDO_DIR}/src/fido/*.c)
file(GLOB OPENPGP_SOURCES CONFIGURE_DEPENDS
    ${PICO_AIO_OPENPGP_DIR}/src/openpgp/*.c
    ${PICO_AIO_OPENPGP_DIR}/src/piv/*.c
)

list(REMOVE_ITEM OPENPGP_SOURCES
    ${PICO_AIO_OPENPGP_DIR}/src/openpgp/management.c
    ${PICO_AIO_OPENPGP_DIR}/src/openpgp/defs.c
)

find_package(Python3 REQUIRED COMPONENTS Interpreter)
set(GENERATED_DIR ${CMAKE_CURRENT_BINARY_DIR}/generated)
set(COMBINED_FILES ${GENERATED_DIR}/files_combined.c)

add_custom_command(
    OUTPUT ${COMBINED_FILES}
    COMMAND ${CMAKE_COMMAND} -E make_directory ${GENERATED_DIR}
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/gen_files.py
            --sdk-dir ${PICO_AIO_SDK_DIR}
            --fido-dir ${PICO_AIO_FIDO_DIR}
            --openpgp-dir ${PICO_AIO_OPENPGP_DIR}
            --output ${COMBINED_FILES}
    DEPENDS
        ${CMAKE_CURRENT_SOURCE_DIR}/tools/gen_files.py
        ${PICO_AIO_FIDO_DIR}/src/fido/files.c
        ${PICO_AIO_FIDO_DIR}/src/fido/files.h
        ${PICO_AIO_OPENPGP_DIR}/src/openpgp/files.c
        ${PICO_AIO_OPENPGP_DIR}/src/openpgp/files.h
        ${PICO_AIO_SDK_DIR}/src/fs/file.h
    VERBATIM
)

set(SOURCES
    ${PICOKEYS_SOURCES}
    ${FIDO_SOURCES}
    ${OPENPGP_SOURCES}
    ${COMBINED_FILES}
)

set(INCLUDES
    ${INCLUDES}
    ${PICO_AIO_OPENPGP_DIR}/src/openpgp
    ${PICO_AIO_OPENPGP_DIR}/src/piv
    ${PICO_AIO_FIDO_DIR}/src/fido
    ${CMAKE_CURRENT_BINARY_DIR}/generated
)

target_sources(pico_fido2 PRIVATE ${SOURCES})
target_include_directories(pico_fido2 PRIVATE ${INCLUDES})
target_compile_options(pico_fido2 PRIVATE -Wall)
target_compile_definitions(pico_fido2 PRIVATE
    "USB_MANUFACTURER_STR=\"${USB_MANUFACTURER}\""
    "USB_PRODUCT_STR=\"${USB_PRODUCT}\""
)

if(ENABLE_EMULATION)
    target_link_libraries(pico_fido2 PRIVATE picokeys_sdk mbedtls)
    if(NOT MSVC)
        target_link_libraries(pico_fido2 PRIVATE pthread m)
    endif()
else()
    pico_add_extra_outputs(pico_fido2)
endif()

message(STATUS "pico-aio USB profile: ${PICO_AIO_USB_PROFILE_LC}")
message(STATUS "pico-aio USB VID/PID:  ${USB_VID}:${USB_PID}")
message(STATUS "pico-aio USB strings:  ${USB_MANUFACTURER} / ${USB_PRODUCT}")
message(STATUS "pico-aio board:        ${PICO_BOARD}")
