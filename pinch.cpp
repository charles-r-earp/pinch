#include "code/binary.hpp"
//#include "model/binary/basic.hpp"
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

template<class Coder>
struct pinch_interface {
    template<typename Model>
    void compress(std::string in_name, std::string cipher_name, Model model) {
      std::fstream in, cipher;
      in.open(in_name, std::fstream::in);
      assert(in.is_open());
      cipher.open(cipher_name, std::fstream::out | std::fstream::trunc);
      assert(cipher.is_open());
      Coder::compress(in, cipher, model);
    }
    template<typename Model>
    void decompress(std::string cipher_name, std::string out_name, Model model) {
      std::fstream cipher, out;
      cipher.open(cipher_name, std::fstream::in);
      assert(cipher.is_open());
      out.open(out_name, std::fstream::out | std::fstream::trunc);
      assert(out.is_open());
      Coder::decompress(cipher, out, model);
    }
    template<typename Model>
    int bench(std::string filename, Model model) {
      auto in_size = file_size(filename);
      std::cout << "bench " << filename << " " << in_size << " bytes" << std::endl;
      float compress_time = stopwatch([=](){ compress(filename, filename+".pinch", Model(model)); });
      auto cipher_size = file_size(filename+".pinch");
      float percent = (100.0*cipher_size)/in_size;
      std::cout << std::fixed << std::setprecision(1) << filename+".pinch " << cipher_size << " bytes in " 
                << compress_time << " s " << percent << "%" << std::endl;
      float decompress_time = stopwatch([=](){ decompress(filename+".pinch", filename+".out", Model(model)); });
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
  namespace pc = pinch::code;
  pinch_interface<pc::binary> interface;
  auto model = [](int bit) { return 0.5; };
  if(argc == 2) {
    std::string filename = argv[1];
    if(!endswith(filename, ".pinch")) {
      interface.compress(filename, filename+".pinch", model);
      return 0;
    }
    else {
      filename = filename.substr(0, filename.length()-6);
      interface.compress(filename+".pinch", filename, model);
      return 0;
    }
  }
  else if(argc == 3) {
    if(std::string(argv[1]).compare("bench") == 0){
      std::string filename = argv[2];
      return interface.bench(filename, model);
    }
  }
    
  std::cout << "pinch Version 0.0.0" << std::endl
            << "usage:" << std::endl
            << argv[0] << " [file]" << std::endl
            << argv[0] << " bench [file]" << std::endl;
      
  return 0;
};