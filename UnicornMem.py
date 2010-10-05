import sys
import re
import subprocess

class UnicornMem:
        def __init__(self, agentConfig, checksLogger, rawConfig):
                checksLogger.debug("In init")
                self.agentConfig = agentConfig
                self.checksLogger = checksLogger
                self.rawConfig = rawConfig

        def run(self):
                self.checksLogger.debug('UnicornMem.run: start')

                unicorn_stats = {}
                processes = self.getProcesses()
                for process in processes:
                        if len(process) and re.match("unicorn", process[1]):
                                worker_re = re.match("^worker\[([0-9]+)\]", process[2])
                                if worker_re:
                                        worker_name = "Worker(%s)" % worker_re.group(1)
                                        worker_mem = int(process[0]) / 1024
                                        unicorn_stats[worker_name] = worker_mem
                return unicorn_stats

        # Copied from checks.py
        def getProcesses(self):
                self.checksLogger.debug('getProcesses: start')

                # Memory logging (case 27152)
                if self.agentConfig['debugMode'] and sys.platform == 'linux2':
                        mem = subprocess.Popen(['free', '-m'], stdout=subprocess.PIPE, close_fds=True).communicate()[0]
                        self.checksLogger.debug('getProcesses: memory before Popen - ' + str(mem))

                # Get output from ps
                try:
                        self.checksLogger.debug('getProcesses: attempting Popen')

                        # ps = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE, close_fds=True).communicate()[0]
                        ps = subprocess.Popen(['ps', '-eo', 'vsize,cmd'], stdout=subprocess.PIPE, close_fds=True).communicate()[0]

                except Exception, e:
                        import traceback
                        self.checksLogger.error('getProcesses: exception = ' + traceback.format_exc())
                        return False

                self.checksLogger.debug('getProcesses: Popen success, parsing')

                # Memory logging (case 27152)
                if self.agentConfig['debugMode'] and sys.platform == 'linux2':
                        mem = subprocess.Popen(['free', '-m'], stdout=subprocess.PIPE, close_fds=True).communicate()[0]
                        self.checksLogger.debug('getProcesses: memory after Popen - ' + str(mem))

                # Split out each process
                processLines = ps.split('\n')

                del processLines[0] # Removes the headers
                processLines.pop() # Removes a trailing empty line

                processes = []

                self.checksLogger.debug('getProcesses: Popen success, parsing, looping')

                for line in processLines:
                        line = line.split(None, 10)
                        processes.append(line)

                self.checksLogger.debug('getProcesses: completed, returning')

                return processes

