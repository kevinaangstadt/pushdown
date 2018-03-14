%{
// #define YYERROR_VERBOSE

#include <iostream>

#include "attribute.h"
#include "cd_sect.h"
#include "char_data.h"
#include "composite_element.h"
#include "content.h"
#include "doctype.h"
#include "document.h"
#include "element.h"
#include "pi.h"
#include "prolog.h"

extern char xmltext[];

int xmllex(void);

void xmlerror(Document **, std::ostream & err, const char *)
{
  static bool set = false;
  if (!set)
    err << "No root markup" << std::endl;
  set = true;
  // std::cerr << msg << std::endl;
}

%}

%union {
   char * s;
   Content * content;
   Element * element;
   PI * pi;
   Doctype * doctype;
   Document * document;
   std::vector<PI *> * pi_list;
   std::pair<Doctype *, std::vector<PI *> *> * doctype_pis;
   std::vector<Attribute *> * attribute_list;
   std::vector<Content *> * content_list;
}

%token EGAL SLASH SUP SUPSPECIAL DOCTYPE COLON INFSPECIAL INF CDATABEGIN
%token <s> VALEUR DONNEES COMMENT NOM CDATAEND

%type<document> document
%type<content> sub_element
%type<element> element
%type<pi> Misc PI
%type<doctype> doctypedecl
%type<pi_list> Misc_0_N
%type<doctype_pis> doctypedecl_Misc_0_N_0_1
%type<attribute_list> Attribute_0_N
%type<content_list> content

%parse-param {Document ** doc_ptr}
%parse-param {std::ostream & err}

// %destructor { printf ("free at %d %s\n",@$.first_line, $$); /*free($$);*/ } <s>
// %destructor { printf ("free at %d Document\n",@$.first_line); /*free($$);*/ } <document>
// %destructor { printf ("free at %d Element\n",@$.first_line); /*free($$);*/ } <element>
// %destructor { printf ("free at %d PI\n",@$.first_line); /*free($$);*/ } <pi>
// %destructor { printf ("free at %d Doctype\n",@$.first_line); /*free($$);*/ } <doctype>
// %destructor { printf ("free at %d PI_List\n",@$.first_line); /*free($$);*/ } <pi_list>
// %destructor { printf ("free at %d Doctype_PIs\n",@$.first_line); /*free($$);*/ } <doctype_pis>
// %destructor { printf ("free at %d Attribute_List\n",@$.first_line); /*free($$);*/ } <attribute_list>
// %destructor { printf ("free at %d Content_List\n",@$.first_line); /*free($$);*/ } <content_list>
// %destructor { printf ("free at %d Content\n",@$.first_line); /*free($$);*/ } <content>

%%

document
  : Misc_0_N doctypedecl_Misc_0_N_0_1 element Misc_0_N
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "----- : document" << std::endl;
    #endif
    #endif
    $$ = new Document(new Prolog(*$1, $2->first, *$2->second), $3, *$4);
    delete $1;
    delete $2->second;
    delete $2;
    delete $4;
    *doc_ptr = $$;
  }
  | Misc_0_N doctypedecl_Misc_0_N_0_1 error
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "ERROR : document" << std::endl;
    #endif
    #endif
    $$ = new Document(new Prolog(*$1, $2->first, *$2->second), nullptr, std::vector<PI *>());
    delete $1;
    delete $2->second;
    delete $2;
    *doc_ptr = $$;
  }
  | Misc_0_N doctypedecl_Misc_0_N_0_1 element Misc_0_N error
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "ERROR : document" << std::endl;
    #endif
    #endif
    $$ = new Document(new Prolog(*$1, $2->first, *$2->second), $3, *$4);
    delete $1;
    delete $2->second;
    delete $2;
    delete $4;
    *doc_ptr = $$;
  }
  ;

Misc_0_N
  : Misc_0_N Misc
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "----- : Misc_0_N" << std::endl;
    #endif
    #endif
    if ($2 != nullptr)
      $1->push_back($2);
    $$ = $1;
  }
  | /* empty */
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "----- : Misc_0_N empty" << std::endl;
    #endif
    #endif
    $$ = new std::vector<PI *>();
  }
  ;

Misc
  : COMMENT
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "----- : Misc - Comment" << std::endl;
    #endif
    #endif
    $$ = nullptr;
    free($1);
  }
  | PI
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "----- : Misc - PI" << std::endl;
    #endif
    #endif
    $$ = $1;
  }
  ;

PI
  : INFSPECIAL NOM Attribute_0_N SUPSPECIAL
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "----- : PI - " << $2 << std::endl;
    #endif
    #endif
    $$ = new PI($2, *$3);
    free($2);
    delete $3;
  }
  | INFSPECIAL error SUPSPECIAL
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "ERROR : PI" << std::endl;
    #endif
    #endif
    $$ = nullptr;
  }
  ;

doctypedecl_Misc_0_N_0_1
  : doctypedecl Misc_0_N
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "----- : doctypedecl_Misc_0_N_0_1" << std::endl;
    #endif
    #endif
    $$ = new std::pair<Doctype *, std::vector<PI *> *>($1, $2);
  }
  | /* empty */
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "----- : doctypedecl_Misc_0_N_0_1 empty" << std::endl;
    #endif
    #endif
    $$ = new std::pair<Doctype *, std::vector<PI *> *>(nullptr,
      new std::vector<PI *>());
  }
  ;

doctypedecl
  : DOCTYPE NOM SUP
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "----- : doctypedecl_0_N - 1 : " << $2 << std::endl;
    #endif
    #endif
    $$ = new Doctype($2, std::string(), std::string());
    free($2);
  }
  | DOCTYPE NOM NOM SUP
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "----- : doctypedecl_0_N - 2 : " << $2 << " " << $3 << std::endl;
    #endif
    #endif
    $$ = new Doctype($2, $3, "");
    free($2);
    free($3);
  }
  | DOCTYPE NOM NOM VALEUR SUP
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "----- : doctypedecl_0_N - 3 : " << $2 << " " << $3 << " " << $4 << std::endl;
    #endif
    #endif
    $$ = new Doctype($2, $3, $4);
    free($2);
    free($3);
    free($4);
  }
  | DOCTYPE error SUP
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "ERROR : doctypedecl" << std::endl;
    #endif
    #endif
    $$ = nullptr;
  }
  ;

Attribute_0_N
  : Attribute_0_N NOM EGAL VALEUR
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "----- : Attribute_0_N - " << $2 << " " << $4 << std::endl;
    #endif
    #endif
    $1->push_back(new Attribute($2, $4));
    $$ = $1;
    free($2);
    free($4);
  }
  | /* empty */
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "----- : Attribute_0_N empty" << std::endl;
    #endif
    #endif
    $$ = new std::vector<Attribute *>();
  }
  | Attribute_0_N error NOM EGAL VALEUR
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "ERROR : attribute" << std::endl;
    #endif
    #endif
    $$ = $1;
    free($3);
    free($5);
  }
  ;

element
  : INF NOM Attribute_0_N SLASH SUP
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "----- : element - empty : " << $2 << std::endl;
    #endif
    #endif
    $$ = new Element($2, *$3);
    free($2);
    delete $3;
  }
  | INF NOM Attribute_0_N SUP content INF SLASH NOM SUP
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "----- : element - composite : " << $2 << " - " << $8 << std::endl;
    #endif
    #endif
    $$ = new CompositeElement($2, $8, *$3, *$5);
    free($2);
    delete $3;
    delete $5;
    free($8);
  }
  | INF NOM Attribute_0_N SUP content error
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "ERROR : element" << $2 << std::endl;
    #endif
    #endif
    /*err << "No root markup" << std::endl;*/
    xmlerror(nullptr, err, nullptr);
    $$ = new CompositeElement($2, "", *$3, *$5);
    free($2);
    delete $3;
    delete $5;
  }
  | INF NOM Attribute_0_N error SUP content INF SLASH NOM SUP
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "ERROR : element" << $2 << std::endl;
    #endif
    #endif
    /*err << "No root markup" << std::endl;*/
    xmlerror(nullptr, err, nullptr);
    $$ = new CompositeElement($2, $9, *$3, *$6);
    free($2);
    delete $3;
    delete $6;
    free($9);
  }
  // | INF error SUP
  // {
  //   #ifdef YYERROR_VERBOSE
  //   #if YYERROR_VERBOSE == 1
  //   std::cout << "ERROR : element" << std::endl;
  //   #endif
  //   #endif
  //   $$ = nullptr;
  // }
  ;

content
  : content sub_element
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "----- : content" << std::endl;
    #endif
    #endif
    if($2 != nullptr)
      $1->push_back($2);
    $$ = $1;
  }
  | /* empty */
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "----- : content empty" << std::endl;
    #endif
    #endif
    $$ = new std::vector<Content *>();
  }
  ;

sub_element
  : DONNEES
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "----- : sub_element - DONNEES : " << $1 << std::endl;
    #endif
    #endif
    $$ = new CharData($1);
  }
  | element
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "----- : sub_element - element" << std::endl;
    #endif
    #endif
    $$ = $1;
  }
  | CDATABEGIN CDATAEND
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "----- : sub_element - CDSect : " << $2 << std::endl;
    #endif
    #endif
    $$ = new CDSect($2);
  }
  | CDATABEGIN error CDATAEND
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "ERROR : CDSect" << std::endl;
    #endif
    #endif
    $$ = new CDSect($3);
  }
  | PI
  {
    #ifdef YYERROR_VERBOSE
    #if YYERROR_VERBOSE == 1
    std::cout << "----- : sub_element - PI" << std::endl;
    #endif
    #endif
    $$ = $1;
  }
  | COMMENT
  {
    $$ = nullptr;
    free($1);
  }
  ;
