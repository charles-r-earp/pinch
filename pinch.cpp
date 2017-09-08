#include "code/binary.hpp"
#include <sstream>
#include <iostream>
#include <fstream>

bool endswith(std::string s, std::string end) {
  if(s.length() >= end.length()) {
    return 0 == s.compare(s.length()-end.length(), end.length(), end);
  }
  else return false;
}

int main(int argc, char** argv) {
  namespace pc = pinch::code;
  const pc::u32 p = pc::binary::coder::pmax/2; 
  if(argc == 2) {
    std::string filename = argv[1];
    if(!endswith(filename, ".pinch")) {
      std::cout << "compressing..." << std::endl;
      std::fstream in, cipher;
      in.open(filename, std::fstream::in);
      assert(in.is_open());
      cipher.open(filename+".pinch", std::fstream::out);
      assert(cipher.is_open());
      pc::binary::compress(in, cipher, p);
    }
    else{
      std::cout << "decompressing..." << std::endl;
      std::fstream cipher;
      std::stringstream out;
      cipher.open(filename, std::fstream::in);
      assert(cipher.is_open());
      pc::binary::decompress(cipher, out, p);
      std::cout << out.str() << std::endl;
    }
  }
  return 0;
};