function(pico_aio_require_patch repo patch)
    execute_process(
        COMMAND ${GIT_EXECUTABLE} -C ${repo} apply --reverse --check ${patch}
        RESULT_VARIABLE patch_result
        OUTPUT_QUIET
        ERROR_QUIET
    )
    if(NOT patch_result EQUAL 0)
        message(FATAL_ERROR
            "Required patch is not applied: ${patch}\n"
            "Run tools/apply-patches.sh before configuring."
        )
    endif()
endfunction()

pico_aio_require_patch(
    ${PICO_AIO_SDK_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/patches/pico-keys-sdk/0001-fs-initialize-dynamic-file-entries.patch
)
pico_aio_require_patch(
    ${PICO_AIO_SDK_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/patches/pico-keys-sdk/0002-main-longest-aid-match.patch
)
pico_aio_require_patch(
    ${PICO_AIO_SDK_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/patches/pico-keys-sdk/0003-usb-descriptor-overrides.patch
)
pico_aio_require_patch(
    ${PICO_AIO_SDK_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/patches/pico-keys-sdk/0004-import-relative-paths.patch
)
pico_aio_require_patch(
    ${PICO_AIO_SDK_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/patches/pico-keys-sdk/0005-led-force-board-ws2812.patch
)
pico_aio_require_patch(
    ${PICO_AIO_SDK_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/patches/pico-keys-sdk/0006-usb-config-header.patch
)
pico_aio_require_patch(
    ${PICO_AIO_SDK_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/patches/pico-keys-sdk/0007-usb-config-include.patch
)
pico_aio_require_patch(
    ${PICO_AIO_SDK_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/patches/pico-keys-sdk/0008-board-header-path.patch
)
pico_aio_require_patch(
    ${PICO_AIO_OPENPGP_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/patches/pico-openpgp/0001-piv-rename-cmd-version.patch
)
pico_aio_require_patch(
    ${PICO_AIO_OPENPGP_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/patches/pico-openpgp/0002-files-combined-table-guard.patch
)
pico_aio_require_patch(
    ${PICO_AIO_FIDO_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/patches/pico-fido/0001-files-combined-table-guard.patch
)
