all: main

main: lex.yy.c main.c
	gcc -o main lex.yy.c main.c

lex.yy.c: ex1.l
	flex --header-file=lex.yy.h ex1.l
	
clean:
	rm main *.o lex.yy.*