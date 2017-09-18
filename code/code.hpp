#include <istream>
#include <ostream>
#include <vector>
#include <thread>
#include <iostream>

namespace pinch {
  namespace code {
    using u32 = unsigned long;
    enum Mode {encode, decode};
    template<Mode mode, typename Model, typename Coder, int size>
    class block;
    
    template<typename Model, typename Coder, int size>
    class block<Mode::encode, Model, Coder, size> {
    private:
      Model model;
      Coder coder;
      std::vector<char> plain;
    public:
      void read(std::istream& is) {
        std::cout << "block read" << std::endl;
        plain.resize(size);
        is.read(&plain[0], size);
        plain.resize(is.gcount());
        std::cout << "block read done." << std::endl;
      }
      void write(std::ostream& os) {
        std::cout << "block write" << std::endl;
        if(plain.empty())
          return;
        if(plain.size() == size)
          os.put(coder.length());
        else {
          os.put(0);
          std::cout << "plain_size: " << plain.size() << std::endl;
          os.put(plain.size());
        }
        model.write(os);
        coder.write(os);
      }
      void run() {
        std::cout << "block run" << std::endl;
        int bit = -1;
        float p;
        for(auto& byte : plain) {
          std::cout << "block run loop" << std::endl;
          for(int i=7; i>=0; --i) {
            std::cout << "a";
            p = model(bit);
            bit = (byte>>i)&1;
            coder.encode(bit, p);
          }
        }
        coder.flush();
      }
    };
      
    template<typename Model, typename Coder, int size>
    class block<Mode::decode, Model, Coder, size> {
    private:
      Model model;
      Coder coder;
      std::vector<char> plain;
      int plain_size;
    public:
      void read(std::istream& is) {
        std::cout << "block decode read" << std::endl;
        int cipher_size = is.get();
        plain_size = size;
        if(cipher_size == 0) {
          plain_size = is.get();
          cipher_size = plain_size;
        }
        std::cout << "decode plain_size: " << plain_size << std::endl;
        coder.read(is, cipher_size);
        std::cout << "block decode read done." << std::endl;
      }
      void write(std::ostream& os) {
        std::cout << "block decode write" << std::endl;
        if(!plain.empty())
          os.write(plain.data(), plain.size());
      }
      void run() {
        std::cout << "block decode write" << std::endl;
        int bit = -1;
        int byte;
        for(int u=0; u<plain_size; ++u) {
          byte = 0;
          for(int i=0; i<8; ++i) {
            bit = coder.decode(model(bit));
            byte |= bit;
            byte <<= 1;
          }
          plain.push_back(byte);
        }
      }
    };
    
    template<Mode mode, typename Model, typename Coder, int size=256>
    void process(std::istream& is, std::ostream& os, int nthreads = 1) {
      std::cout << "process" << std::endl;
      std::vector<std::thread> threads(nthreads);
      std::vector<block<mode, Model, Coder, size>> blocks(nthreads);
      bool done = false;
      while(!done) {
        done = (is.peek() == -1);
        std::cout << "process loop" << std::endl;
        for(int i=0; i<nthreads; ++i) {
          std::cout << "process loop loop" << std::endl;
          if(threads[i].joinable())
            threads[i].join();
          auto& _block = blocks[i];
          _block.write(os);
          if(is.peek() != -1) {
            _block.read(is);
            std::cout << "before peek" << std::endl;
            std::cout << "after peek" << std::endl;
            auto f = [&](){ _block.run(); };
            threads[i] = std::thread(f);
          }
        }
      }
      std::cout << "process done." << std::endl;
    }
  };
};