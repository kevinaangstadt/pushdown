all: main main2

main2: tokens.h lex.yy.c main2.c
	gcc -o main2 lex.yy.c main2.c

main: lex.yy.c main.c
	gcc -o main lex.yy.c main.c

lex.yy.c: xml.l
	flex --header-file=lex.yy.h xml.l
	
clean:
	rm main main2 *.o lex.yy.*