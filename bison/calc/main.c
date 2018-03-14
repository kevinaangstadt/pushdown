#include <stdio.h>

#include "tokens.h"
#include "lex.yy.h" 

extern union {
  int val;
  char sym;
} yylval;

int main(int argc, char *argv[]) {

  if (argc > 1) {
    /* read from file */ 
    yyin = fopen(argv[1],"r"); 
  } /* else: read from stdin */ 

  int this_token;
  while ( (this_token = yylex()) ) { 
    printf("%c", this_token);
  }
  printf("%c", $end);

  return 0; 
} 