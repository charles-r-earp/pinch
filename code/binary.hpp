#include "code.hpp"
#include <cassert>
#include <istream>
#include <ostream>


//#include <typeinfo>
#include <iostream>

namespace pinch {
  namespace code {
    struct binary {
      class coder {
      public:
        static const u32 pmax = 4095;
      protected:
        u32 x1 = 0, x2 = 0xffffffff;
      };
      class encoder : public coder {
      public:
        void encode(int y, std::ostream& out, u32 p) {
          const u32 xmid = x1 + ((x2-x1) >> 12) * p;
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
      };
      class decoder : public coder {
        u32 x = -1;
      public:
        int decode(std::istream& in, u32 p) {
          if (x == -1) {
            x = 0;
            for (int i=0; i<4; ++i) {
              int c = 0;
              if (in)  c = in.get();
              x=(x<<8)+(c&0xff);
            }
          }    
          const u32 xmid = x1 + ((x2-x1) >> 12) * p;
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
      };
      template<typename Model>
      static void compress(std::istream& in, std::ostream& out, Model &model) {
        encoder e;
        in.seekg(0, std::istream::end);
        u32 length = in.tellg();
        in.seekg(0, std::istream::beg);
        for(int i = 3; i >= 0; --i) {
            char c = (length>>(8*i));
            out.put(c);
        }
        int c = in.get();
        int bit = -1;
        u32 p = coder::pmax*model(bit);
        while (in) {
          ++length;
          for(int i = 7; i >= 0; --i) {
            bit = (c>>i)&1;
            e.encode(bit, out, p);
            p = coder::pmax*model(bit);
          }
          c = in.get();
        } 
        e.flush(out);
      }
      template<typename Model>
      static void decompress(std::istream& in, std::ostream& out, Model &model) {
        decoder d;
        u32 length = 0;
        for(int i = 3; i >= 0; --i) {
            int c = in.get();
            length |= c << (i*8);
        }
        assert(length > 0);
        int bit = -1, c;
        u32 p = coder::pmax*model(bit);
        while(length-->0) {
          c = 0;
          for(int i = 7; i >= 0; --i) {
            bit = d.decode(in, p);
            p = coder::pmax*model(bit);
            c |= bit<<i;
          }
          out.put(c);
        }
      }
    };
  };
};

