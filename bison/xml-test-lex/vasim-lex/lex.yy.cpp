#include <unistd.h>
#include <limits.h>

#include <libgen.h>
#include "lex.yy.h"
#include "tokens.h"

using std::cerr;
using std::cout;
using std::endl;
using std::stringstream;
using std::string;

static std::string get_selfpath() {
    char buff[PATH_MAX];
    ssize_t len = ::readlink("/proc/self/exe", buff, sizeof(buff)-1);
    if (len != -1) {
      buff[len] = '\0';
      return std::string(dirname(buff));
    }
    /* handle error condition */
    throw std::runtime_error("Could not find path of this binary");
}

static std::string join(std::string first, std::string second) {
  if (first[first.length()-1] == '/') {
    return first + second;
  }
  return first + "/" + second;
}

yyFlexLexer::yyFlexLexer( 
  istream* arg_yyin, 
  ostream* arg_yyout
) : state(yyFlexLexer::State::YY_INITIAL),
  pos(0),
  yyin(arg_yyin), 
  yyout(arg_yyout) {
  
  Automata ap(join(get_selfpath(), "initial.mnrl"));
  ap.finalizeAutomata();
  ap.setReport(true);
  ap.setProfile(true);
  
  machines.push_back(ap);
  
  
  ap = Automata(join(get_selfpath(), "contenu.mnrl"));
  ap.finalizeAutomata();
  ap.setReport(true);
  ap.setProfile(true);
  
  machines.push_back(ap);
  
  ap = Automata(join(get_selfpath(), "cdatasection.mnrl"));
  ap.finalizeAutomata();
  ap.setReport(true);
  ap.setProfile(true);
  
  machines.push_back(ap);

}

int yyFlexLexer::yylex() {
  stringstream buffer;
  machines[static_cast<int>(state)].reset();
  machines[static_cast<int>(state)].initializeSimulation();
  
  if (yy_flex_debug) {
    cout << "State: " << (int)state << endl;
  } 
  
  bool eof = false;
  
  do {
    try {
      char tmp = yyget();
      buffer << tmp;
      pos += 1;
      
      machines[static_cast<int>(state)].simulate(tmp);
    } catch (FlexEOF &e) {
      eof = true;
      break;
    }
    
    
  } while (machines[static_cast<int>(state)].getActivatedLastCycle().size() > 0);
  
  // we have found the next token at this point (or there was no match)
  auto reports = machines[static_cast<int>(state)].getReportVector();
  if(reports.size() == 0 ) {
    if(eof) {
      // we're at the end
      return 0;
    }
    // we didn't match anything, throw away one character?
    cerr << "unknown char: " << buffer.peek() << endl;
    string buf_tmp = buffer.str();
    yyunput(buf_tmp.substr(1));
    return yylex();
    
  } else {
    auto final_report = reports.back();
    uint64_t loc = final_report.first + 1;
    int code = stoi(machines[static_cast<int>(state)].getElement(final_report.second)->getReportCode());
    
    string buf_tmp = buffer.str();
    yytext = buf_tmp.substr(0,loc);

    
    yyunput(buf_tmp.substr(loc));
    
    try {
      return parse_code(code);
    } catch (const FlexSKIP &e) {
      return yylex();
    }
    
  }
}

int yyFlexLexer::parse_code(int code) {
  switch(state) {
    case State::YY_INITIAL:{
      switch(code) {
        case 0: /* {esp} */
          throw FlexSKIP();
          break;
          
        case 1: /* {doctype} */
          return DOCTYPE;
          
        case 2: /* "/" */
          return SLASH;
        
        case 3: /* "=" */
          return EGAL;
          
        case 4: /* {sup} */
          state = State::YY_CONTENU;
          return SUP;
          
        case 5: /* {supspecial} */
          return SUPSPECIAL;
          
        case 6: /* {nom} */
          return NOM;
          
        case 7: /* {chaine} */
          return VALEUR;
        
        case 8: /* {infspecial} */
          state = State::YY_INITIAL;
          return INFSPECIAL;
          
        case 9: /* {inf} */
          state = State::YY_INITIAL;
          return INF;
        
        case 10: /* {comment} */
          return COMMENT;
          
        default:
          throw std::runtime_error("unknown report code: INITIAL");
      }
      break;
    }
    case State::YY_CONTENU:{
      switch(code) {
        case 0: /* {cdata} */
          state = State::YY_CDATASECTION;
          return CDATABEGIN;
          
        case 1: /* {infspecial} */
          state = State::YY_INITIAL;
          return INFSPECIAL;
        
        case 2:/* {inf} */
          state = State::YY_INITIAL;
          return INF;
        
        case 3:/* {comment} */
          return COMMENT;
        
        case 4: /* {pcdata} */
          return DONNEES;
        
        default:
          throw std::runtime_error("unknown report code: CONTENU");
      }
      break;
    }
    case State::YY_CDATASECTION:{
      switch(code) {
        case 0: /* {endcdata} */
          state = State::YY_CONTENU;
          return CDATAEND;
        
        case 1: /* .|[\t\r\n ] */
          throw FlexSKIP();
        
        default:
          throw std::runtime_error("unknown report code: CDATASECTION");
      }
      break;
    }
  }
  return -2;
}

void yyFlexLexer::switch_streams(
  istream* new_in,
  ostream* new_out
) {
    if( new_in ) {
      if(yyin != &std::cin) {
        delete yyin;
      }
      yyin = new_in;
    }
    
    if( new_out ) {
      if(yyout != &std::cout) {
        delete yyout;
      }
      yyout = new_out;
    }
}

int yyFlexLexer::yylex( istream* new_in, ostream* new_out ) {
  switch_streams(new_in, new_out);
  return yylex();
}

void yyFlexLexer::yyunput(string s){
  for(string::reverse_iterator it = s.rbegin(); it != s.rend(); ++it) {
    yybuffer.putback(*it);
  }
}

char yyFlexLexer::yyget() {
  if(yyin->peek() != EOF) {
    char tmp = (char)(yyin->get());
    if(yy_flex_debug) {
      cout << "loading: " << tmp << endl;
    }
    yybuffer << tmp;
  }
  if(yybuffer.peek() != EOF) {
    char tmp = (char)(yybuffer.get());
    if(yy_flex_debug){
      cout << "returning: " << tmp << endl;
    }
    return tmp;
  } else {
    throw FlexEOF();
  }
}

yyFlexLexer::~yyFlexLexer() { }
FlexLexer::~FlexLexer() { }