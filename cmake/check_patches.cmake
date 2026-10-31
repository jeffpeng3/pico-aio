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
    ${PICO_AIO_OPENPGP_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/patches/pico-openpgp/0001-piv-rename-cmd-version.patch
)
pico_aio_require_patch(
    ${PICO_AIO_OPENPGP_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/patches/pico-openpgp/0002-files-combined-table-guard.patch
)
pico_aio_require_patch(
    ${PICO_AIO_OPENPGP_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/patches/pico-openpgp/0003-namespace-applets.patch
)
pico_aio_require_patch(
    ${PICO_AIO_FIDO_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/patches/pico-fido/0001-files-combined-table-guard.patch
)
pico_aio_require_patch(
    ${PICO_AIO_FIDO_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/patches/pico-fido/0002-namespace-applets.patch
)
