#include <cassert>
#include <istream>
#include <ostream>
#include <iomanip>
#include <iostream>

namespace pinch {
  using uint = unsigned int;
  class arithmetic_coder {
    uint x, x1, x2;
    static const uint pmax = 4095;
    void reset() { x=-1; x1 = 0; x2 = 0xffffffff; }
    void encode(std::ostream& out, uint p, int y) {
      const uint xmid = x1 + ((x2-x1) >> 12)*p;
      assert(xmid >= x1 && xmid < x2);
      if (y)
        x2=xmid;
      else
        x1=xmid+1;
      while (((x1^x2)&0xff000000)==0) {
        out.put(x2>>24);
        x1<<=8;
        x2=(x2<<8)+255;
      }
    }
    void flush(std::ostream& out) {
      while (((x1^x2)&0xff000000)==0) {
        out.put(x2>>24);
        x1<<=8;
        x2=(x2<<8)+255;
      }
      out.put(x2>>24);
    }
    int decode(std::istream& in, uint p) {
      if (x == -1) {
        x = 0;
        for (int i=0; i<4; ++i) {
          int c = 0;
          if (in)  c = in.get();
            x=(x<<8)+(c&0xff);
          }
        }    
        const uint xmid = x1 + ((x2-x1) >> 12)*p;
        assert(xmid >= x1 && xmid < x2);
        int y=0;
        if (x<=xmid) {
          y=1;
          x2=xmid;
        }
        else
          x1=xmid+1;
        while (((x1^x2)&0xff000000)==0) {
          x1<<=8;
          x2=(x2<<8)+255;
          int c = 0;
          if (in) c = in.get();
          x=(x<<8)+c;
        }
        return y;
      }
  public:
    template<typename Model>
    void compress(std::istream& in, std::ostream& out, Model &model) {
      reset();
      in.seekg(0, std::istream::end);
      uint length = in.tellg();
      in.seekg(0, std::istream::beg);
      for(int i = 3; i >= 0; --i) {
        char c = (length>>(8*i));
        out.put(c);
      }
      int c = in.get();
      int bit = -1;
      uint p = pmax*model(bit);
      int u = 0;
      while (in) {
        for(int i = 7; i >= 0; --i) {
          bit = (c>>i)&1;
          encode(out, p, bit);
          p = pmax*model(bit);
        }
        c = in.get();
        if (u % 1000 == 0) {
          std::cout << std::setprecision(1) << std::fixed << float(100*u)/length << "%\r";
          std::cout.flush();
        }
        ++u;
      } 
      flush(out);
    }
    template<typename Model>
    void decompress(std::istream& in, std::ostream& out, Model &model) {
      reset();
      uint length = 0;
      for(int i = 3; i >= 0; --i) {
        int c = in.get();
        length |= c << (i*8);
      }
      assert(length > 0);
      int bit = -1, c;
      uint p = pmax*model(bit);
      int u = 0;
      while(u<length) {
        c = 0;
        for(int i = 7; i >= 0; --i) {
          bit = decode(in, p);
          p = pmax*model(bit);
          c |= bit<<i;
        }
        out.put(c);
        if (u % 1000 == 0) {
          std::cout << std::setprecision(1) << std::fixed << float(100*u)/length << "%\r";
          std::cout.flush();
        }
        ++u;
      }
    }
  };
};

