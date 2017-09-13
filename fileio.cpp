#include <iomanip>
#include <iostream>
#include <fstream>

template<typename F, typename ... Args>
double stopwatch(F f, Args ... args) {
    auto start = time(NULL);
    f(args...);
    auto end = time(NULL);
    return difftime(end, start);
}

int file_size(std::string filename) {
    std::fstream f;
    f.open(filename, std::fstream::in);
    f.seekp(0, std::fstream::end);
    auto pos = f.tellp();
    f.close();
    return pos;
}

void fstream_by_char(std::string filename){
    std::fstream in, out;
    in.open(filename, std::fstream::in);
    out.open(filename+".fstream_by_char", std::fstream::out | std::fstream::trunc);
    char c = in.get();
    while(in) {
        out.put(c);
        c = in.get();
    }
    in.close();
    out.close();
}

void print_results(std::string name, double rate) {
    std::cout << name << ": " << std::setprecision(1) << std::fixed << rate << std::endl;
}

int main(int argc, char** argv) {
    std::string filename = argv[1];
    auto size = file_size(filename);
    
    print_results("fstream_by_char", size/stopwatch(fstream_by_char, filename));
    
}