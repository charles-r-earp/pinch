#include "code/bin_acode.hpp"
#include "model/bin_rnn.hpp"
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

template<typename Model, typename Coder, int block_size>
struct pinch_interface {
    void compress(std::string in_name, std::string cipher_name) {
      std::cout << "compress" << std::endl;
      std::fstream in, cipher;
      in.open(in_name, std::fstream::in);
      assert(in.is_open());
      cipher.open(cipher_name, std::fstream::out | std::fstream::trunc);
      assert(cipher.is_open());
      namespace pc = pinch::code;
      pc::process<pc::Mode::encode, Model, Coder>(in, cipher);
      std::cout << "compress done." << std::endl;
    }
    void decompress(std::string cipher_name, std::string out_name) {
      std::fstream cipher, out;
      cipher.open(cipher_name, std::fstream::in);
      assert(cipher.is_open());
      out.open(out_name, std::fstream::out | std::fstream::trunc);
      assert(out.is_open());
      namespace pc = pinch::code;
      pc::process<pc::Mode::decode, Model, Coder>(cipher, out);
    }
    int bench(std::string filename) {
      auto in_size = file_size(filename);
      std::cout << "bench " << filename << " " << in_size << " bytes" << std::endl;
      float compress_time = stopwatch([&](){ compress(filename, filename+".pinch"); });
      auto cipher_size = file_size(filename+".pinch");
      float percent = (100.0*cipher_size)/in_size;
      std::cout << std::fixed << std::setprecision(1) << filename+".pinch " << cipher_size << " bytes in " 
                << compress_time << " s " << percent << "%" << std::endl;
      float decompress_time = stopwatch([&](){ decompress(filename+".pinch", filename+".out"); });
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
  namespace pm = pinch::model;
  pinch_interface<pm::bin_rnn, pc::bin_acode, 256> interface;
  if(argc == 2) {
    std::string filename = argv[1];
    if(!endswith(filename, ".pinch")) {
      interface.compress(filename, filename+".pinch");
      return 0;
    }
    else {
      filename = filename.substr(0, filename.length()-6);
      interface.compress(filename+".pinch", filename);
      return 0;
    }
  }
  else if(argc == 3) {
    if(std::string(argv[1]).compare("bench") == 0){
      std::string filename = argv[2];
      return interface.bench(filename);
    }
  }
    
  std::cout << "pinch Version 0.0.0" << std::endl
            << "usage:" << std::endl
            << argv[0] << " [file]" << std::endl
            << argv[0] << " bench [file]" << std::endl;
      
  return 0;
};