file(GLOB_RECURSE models "*.py")
foreach(model "${models}")
    file(RELATIVE_PATH model "${CMAKE_CURRENT_SOURCE_DIR}" "${model}")
    string(REPLACE "/" ";" path ${model})
    list(GET path 0 folder)
    list(GET path -1 model)
    execute_process(
        COMMAND "python" "${model}" "${CMAKE_CURRENT_BINARY_DIR}/${folder}"
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/${folder}"
    )
    
endforeach(model)