cmake_minimum_required(VERSION 3.5)
project(pinch)
# c++ standard
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_executable(pinch pinch.cpp)
target_include_directories(pinch PUBLIC code model "${CMAKE_BINARY_DIR}/model")
# caffe2
# caffe2 -> eigen 
find_package(Eigen3 REQUIRED)
# caffe2 -> protobuf
find_library(protobuf_lib "libprotobuf.so.14.0.0" HINTS "/usr/local/lib")
message("protobuf_lib: ${protobuf_lib}")
find_path(caffe2_include NAME "caffe2/core/net.h" HINTS "/usr/local/include")
message("caffe2_include: ${caffe2_include}")
target_include_directories(pinch PRIVATE caffe2_include "${EIGEN3_INCLUDE_DIR}")
#find_path(caffe2_lib NAME "libCaffe2_CPU.so" HINTS "/usr/local/lib")
#message("caffe2_lib: ${caffe2_lib}")
target_link_libraries(pinch Caffe2_CPU "${protobuf_lib}" glog pthread)
add_subdirectory(model)
#add_executable(fileio fileio.cpp)
# benchmarking and testing on build
file(GLOB benchfiles "bench/*")
add_custom_target(pinch-test ALL DEPENDS pinch)
foreach(file ${benchfiles})
  get_filename_component(name "${file}" NAME)
  file(COPY "bench/${name}" DESTINATION "bench/")
  add_custom_command(TARGET pinch-test POST_BUILD COMMAND "./pinch" "bench" "bench/${name}")
endforeach(file)