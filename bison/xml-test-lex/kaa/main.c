#include <stdio.h>

#include "lex.yy.h" 

extern struct { // WRW hack, why aren't they just using yylval? 
  char * s; 
} xmllval; 

char * token_to_str[] = {
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

  if (argc > 1) {
    /* read from file */ 
    yyin = fopen(argv[1],"r"); 
  } /* else: read from stdin */ 

  while (1) { 
    int this_token;
    xmllval.s = NULL; 
    
    this_token = yylex(); 
    printf("token = %02x = %s", this_token, token_to_str[this_token]); 
    if (xmllval.s) printf(" [%s]", xmllval.s);
    printf("\n"); 

    if (this_token <= 0) break; 
  } 

  return 0; 
} 
