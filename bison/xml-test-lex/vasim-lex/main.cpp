#include <stdio.h>
#include <iostream>
#include <string>

#include "lex.yy.h" 
#include "tokens.h"

using std::cerr;
using std::endl;

char *token_to_str[] = {
  "MY_EOF",
  "COMMENT",
  "NOM",
  "CDATAEND",
  "EGAL",
  "CDATABEGIN",
  "error",
  "INFSPECIAL",
  "DOCTYPE",
  "SUPSPECIAL",
  "COLON",
  "VALEUR",
  "SLASH",
  "SUP",
  "INF",
  "DONNEES",
  "$end"
} ;

int main(int argc, char *argv[]) {
  
  yyFlexLexer l;

  if (argc > 1) {
    /* read from file */ 
    if (!freopen(argv[1],"r", stdin)) {
        cerr << "freopen() failed, file not found" << endl;
        exit(1);
    } 
  } /* else: read from stdin */ 

  int this_token;
  uint64_t tok_cnt = 0;
  
  while ( (this_token = l.yylex()) ) { 
    //printf("token = %02x = %s [%s]\n", this_token, token_to_str[this_token], l.YYText());
    printf("%c", this_token);
    cerr << ++tok_cnt << ", " << l.YYCycles() << "\n";
    
  }
  printf("%c", $end);

  return 0;  
} 