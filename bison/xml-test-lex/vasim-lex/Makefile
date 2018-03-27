VASIM = /home/kaa2nx/AP/vasim-dpda
VASIMLIB = $(VASIM)/libvasim.a
MNRLLIB = $(VASIM)/libs/MNRL/C++/libmnrl.a

CXX = g++

CPPFLAGS = -I$(VASIM)/include -I$(VASIM)/libs/MNRL/C++/include -I$(VASIM)/libs/pugixml/src

CXXFLAGS = -std=c++1z -Wconversion -Wall -Wextra 

# list of sources used in project
SOURCES     = $(wildcard *.cpp)
OBJECTS     = $(SOURCES:%.cpp=%.o)

main: $(OBJECTS)
	$(CXX) $(LDFLAGS) -o $@ $^ $(VASIMLIB) $(MNRLLIB)
	
%.o: %.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c -o $@ $< 
	
clean:
	rm *.o main
