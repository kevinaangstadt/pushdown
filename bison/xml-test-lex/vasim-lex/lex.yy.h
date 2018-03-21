#ifndef yyHEADER_H
#define yyHEADER_H

#include <iostream>
#include <string>
#include <sstream>
#include <stdexcept>

#include "automata.h"

using std::istream;
using std::ostream;
using std::string;
using std::stringstream;

class FlexEOF : public std::exception {
  const char * what () const throw () {
    return "FlexEOF";
  }
};

class FlexSKIP : public std::exception {
  const char * what () const throw () {
    return "FlexSKIP";
  }
};

class FlexLexer {
public:
  virtual ~FlexLexer() = 0;
  virtual const char* YYText()  { return yytext.c_str(); };
  virtual int YYLeng() { return (int) yytext.size(); };
  virtual int lineno() const { return 0; };
  virtual void set_debug( int flag ) { yy_flex_debug = flag; }
  virtual int debug() const { return yy_flex_debug; }
  
protected:
  int yy_flex_debug = 0;
  std::string yytext;
};

class yyFlexLexer : public FlexLexer {
public:
  yyFlexLexer( istream* arg_yyin = &std::cin, ostream* arg_yyout = &std::cout );
  virtual ~yyFlexLexer();
  virtual int yylex();
  virtual uint64_t YYCycles() { return pos; };
  virtual void switch_streams(istream* new_in = 0, ostream* new_out = 0);
  int yylex( istream* new_in, ostream* new_out );
  
private:
  void yyunput(string s);
  int parse_code(int code);
  
  char yyget();
  
  enum class State {
    YY_INITIAL = 0,
    YY_CONTENU,
    YY_CDATASECTION
  };
  
  std::vector<Automata> machines;
  State state;
  uint64_t pos;
  
  stringstream yybuffer;
  
  istream* yyin;
  ostream* yyout;
};

#endif