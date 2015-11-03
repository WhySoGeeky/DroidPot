/*
author: Tan RongShun
*/

#ifndef _ZYGOTECHILDTRACE_H_
#define _ZYGOTECHILDTRACE_H_

struct process
{
	int pid;
	char *name;
};

/*
strace: starts strace command
returns: void
*/
void strace(int pid, char *outputFile);

/*
getProcName: gets the process anme form /proc/<pid>/status
returns: char* process name
*/
char* getProcName(int pid);

/*
findZygotePid: find zygote's pid
returns: int pid
*/
int findZygotePid();

/*
watchAndStraceZygote: watch zygote and extract it's pid and traces the system calls
returns: void
*/
void watchAndStraceZygote();

/*
strdup: Allocate memory for char* return
returns: char*
*/
char* strdup(const char* org);

#endif