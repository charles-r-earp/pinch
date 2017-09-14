set(models bin_rnn.py)
foreach(model "${models}")
    execute_process(
        COMMAND "python" "${model}" "save" "${CMAKE_CURRENT_BINARY_DIR}"
 #       WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
    )
)
endforeach(model)