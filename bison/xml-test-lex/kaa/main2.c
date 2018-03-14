#include <stdio.h>

#include "tokens.h"
#include "lex.yy.h" 

extern struct { // WRW hack, why aren't they just using yylval? 
  char * s; 
} xmllval; 

int main(int argc, char *argv[]) {

  if (argc > 1) {
    /* read from file */ 
    yyin = fopen(argv[1],"r"); 
  } /* else: read from stdin */ 

  int this_token;
  while ( (this_token = yylex()) ) { 
    printf("%c", this_token);
    xmllval.s = NULL; 
  }
  printf("%c", $end);

  return 0; 
} 
