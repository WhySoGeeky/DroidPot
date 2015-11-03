/*
author: Tan RongShun
*/

#ifndef _ZYGOTEW_H_
#define _ZYGOTEW_H_

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
strdup: Allocate memory for char* return
returns: char*
*/
char* strdup(const char* org);
/*
watchAndStraceZygote: watch zygote and extract it's pid and traces the system calls
returns: void
*/
void watchAndStraceZygote();

/*
monitorProcessForkIfExist: trace the system call of targeted process
returns: void
*/
void monitorProcessForkIfExist();

/*
checkAgainstWhitelist: check pid against whitelisted processes
returns: 1 if match, 0 if not match
*/
int checkAgainstWhitelist(char *pid);

/*
findZygotePid: find zygote's pid
returns: int pid
*/
int findZygotePid();

/*
addToMonitoringListIfNotExist: add process struct to monitoring list
returns: int, 1 for added, 0 for not added
*/
int addToMonitoringListIfNotExist(struct process);
#endif
