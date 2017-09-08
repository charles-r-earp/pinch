cmake_minimum_required(VERSION 3.5)
project(pinch)
# c++ standard
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_executable(pinch pinch.cpp)
target_include_directories(pinch PUBLIC code)
configure_file(in.txt in.txt COPYONLY)