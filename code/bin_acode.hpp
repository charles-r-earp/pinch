#include "code.hpp"
#include <cassert>


namespace pinch {
  namespace code {
    class bin_acode {
    private:
      std::vector<char> cipher;
      std::vector<char>::iterator it;
      static const u32 pmax = 4095;
      u32 x1 = 0, x= -1, x2 = 0xffffffff;
    public:
      int length() {
        return cipher.size(); 
      }
      // encode
      void write(std::ostream& os) {
        std::cout << "bin_acode write: ";
        for (auto byte : cipher)
            std::cout << u32(byte) << " ";
        std::cout << std::endl;
        os.write(cipher.data(), cipher.size());
        cipher.clear();
        x1 = 0; x2 = 0xffffffff;
      }
      void encode(int y, float p) {
        std::cout << "bin_acode encode: " << y << " p = " << p << std::endl; 
        std::cout << "x1 = " << x1 << " x2 = " << x2 << std::endl;
        u32 pval = pmax * p;
        if(!pval)
          pval = 1;
        const u32 xmid = x1 + ((x2-x1) >> 12) * pval;
        assert(xmid >= x1 && xmid < x2);
        if (y)
          x2=xmid;
        else
          x1=xmid+1;
        
        while (((x1^x2)&0xff000000)==0) {
          cipher.push_back(x2>>24);
          x1<<=8;
          x2=(x2<<8)+255;
        }
        std::cout << "bin_acode done. cipher.size(): " << cipher.size() << std::endl;
      }
      void flush() {
        while (((x1^x2)&0xff000000)==0) {
          cipher.push_back(x2>>24);
          x1<<=8;
          x2=(x2<<8)+255;
        }
        cipher.push_back(x2>>24);
        std::cout << "bin_acode flush cipher.size(): " << cipher.size() << std::endl;
      }
      // decode
      void read(std::istream& is, int n) {
          cipher.resize(n);
          is.read(cipher.data(), n);
          cipher.resize(is.gcount());
          std::cout << "bin_acode read: ";
          for(auto byte : cipher)
            std::cout << u32(byte) << " ";
          std::cout << std::endl;
          it = cipher.begin();
          x1 = 0; x = -1; x2 = 0xffffffff;
      }
      int decode(float p) {
          std::cout << "bin_acode decode p = " << p << std::endl; 
          std::cout << "x1 = " << x1 << " x = " << x << " x2 = " << x2 << std::endl;
          u32 pval(pmax * p);
          int c;
          if(!p)
            p = 1;
          if (x == -1) {
            x = 0;
            for (int i=0; i<4; ++i) {
              c = (it - cipher.begin()) < cipher.size() ? *(it++) : 0;
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
            c = (it - cipher.begin()) < cipher.size() ? *(it++) : 0;
            x=(x<<8)+c;
          }
          std::cout << "bin_acode decode done: " << y << std::endl; 
          return y;
        }
    };
      
      /*
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
        int u = 0;
        while (in) {
          for(int i = 7; i >= 0; --i) {
            bit = (c>>i)&1;
            e.encode(bit, out, p);
            p = coder::pmax*model(bit);
          }
          c = in.get();
          if (u % 1000 == 0) {
            std::cout << std::setprecision(1) << std::fixed << float(100*u)/length << "%\r";
            std::cout.flush();
          }
          ++u;
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
        int u = 0;
        while(u<length) {
          c = 0;
          for(int i = 7; i >= 0; --i) {
            bit = d.decode(in, p);
            p = coder::pmax*model(bit);
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
    };*/
  };
};

