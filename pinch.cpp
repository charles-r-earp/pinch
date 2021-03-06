#include "code/arithmetic.hpp"
#include <ctime>
#include <sstream>
#include <iostream>
#include <fstream>
#include <string>
#include <iomanip>

bool endswith(std::string s, std::string end) {
  if(s.length() >= end.length()) {
    return 0 == s.compare(s.length()-end.length(), end.length(), end);
  }
  else return false;
}

bool match(std::istream& s1, std::istream& s2) {
  std::string str1, str2;
  do {
    s1 >> str1;
    s2 >> str2;
    if(str1.compare(str2) != 0) return false;
  } while(!s1.eof() && !s2.eof());
  return s1.eof() && s2.eof();
}

bool match(std::string fname1, std::string fname2) {
    std::fstream f1, f2;
    f1.open(fname1, std::fstream::in);
    f2.open(fname2, std::fstream::in);
    bool success = match(f1, f2);
    f1.close();
    f2.close();
    return success;
}

int file_size(std::string filename) {
    std::fstream f;
    f.open(filename, std::fstream::in);
    f.seekp(0, std::fstream::end);
    auto pos = f.tellp();
    f.close();
    return pos;
}

template<typename F>
double stopwatch(F f) {
    auto start = time(NULL);
    f();
    auto end = time(NULL);
    return difftime(end, start);
}

struct pinch_interface {
  template<typename Coder, typename Model>
  void compress(std::string in_name, std::string cipher_name, Coder& coder, Model& model) {
    //const size_t nBufferSize = 16184;
    //char in_buffer[nBufferSize], cipher_buffer[nBufferSize];
    //f.rdbuf()->pubsetbuf(buffer, nBufferSize);
    std::fstream in, cipher;
    //in.rdbuf()->pubsetbuf(in_buffer, nBufferSize);
    //cipher.rdbuf()->pubsetbuf(cipher_buffer, nBufferSize);
    in.open(in_name, std::fstream::in);
    assert(in.is_open());
    cipher.open(cipher_name, std::fstream::out | std::fstream::trunc);
    assert(cipher.is_open());
    coder.compress(in, cipher, model);
  }
  template<typename Coder, typename Model>
  void decompress(std::string cipher_name, std::string out_name, Coder& coder, Model &model) {
    std::fstream cipher, out;
    cipher.open(cipher_name, std::fstream::in);
    assert(cipher.is_open());
    out.open(out_name, std::fstream::out | std::fstream::trunc);
    assert(out.is_open());
    coder.decompress(cipher, out, model);
  }
  template<typename Coder, typename Model>
  int bench(std::string filename, Coder& coder, Model &model) {
    auto in_size = file_size(filename);
    std::cout << "bench " << filename << " " << in_size << " bytes" << std::endl;
    float compress_time = stopwatch([&](){ compress(filename, filename+".pinch", coder, model); });
    auto cipher_size = file_size(filename+".pinch");
    float percent = (100.0*cipher_size)/in_size;
    std::cout << std::fixed << std::setprecision(1) << filename+".pinch " << cipher_size << " bytes in " 
              << compress_time << " s " << percent << "%" << std::endl;
    float decompress_time = stopwatch([&](){ decompress(filename+".pinch", filename+".out", coder, model); });
    auto success = match(filename, filename+".out");
    std::cout << std::setprecision(1) << filename+".out " << decompress_time << " s " << (success ? "success" : "fail")
              << std::endl << std::endl;
    if(success) 
      return 0;
    else 
      return 1;
  }
};

int main(int argc, char** argv) {
  auto coder = pinch::arithmetic_coder();
  auto model = [](const int bit) { return 0.6; };
  pinch_interface interface;
  if(argc == 2) {
    std::string filename = argv[1];
    if(!endswith(filename, ".pinch")) {
      interface.compress(filename, filename+".pinch", coder, model);
      return 0;
    }
    else {
      filename = filename.substr(0, filename.length()-6);
      interface.compress(filename+".pinch", filename, coder, model);
      return 0;
    }
  }
  else if(argc == 3) {
    if(std::string(argv[1]).compare("bench") == 0){
      std::string filename = argv[2];
      return interface.bench(filename, coder, model);
    }
  }
    
  std::cout << "pinch Version 0.0.0" << std::endl
            << "usage:" << std::endl
            << argv[0] << " [file]" << std::endl
            << argv[0] << " bench [file]" << std::endl;
      
  return 0;
};