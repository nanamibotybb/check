all: name2uid-parse

name2uid-parse: name2uid-parse.c cJSON.c
	tcc -Wall -lm $^ -o $@ 
