import subprocess
import threading
import time
import datetime
import re
wait=1

lock=threading.Lock()

def cpu_info(file):
    command = ['wmic', 'cpu', 'get', 'Name,LoadPercentage,CurrentClockSpeed,ThreadCount']
    cfg = subprocess.run(command, capture_output=True, shell=True, text=True, check=True)
    output_lines = cfg.stdout.strip().splitlines()

    cpu_info_list = re.split('\s{2,}', output_lines[2].strip())
    cpu_name=cpu_info_list[2]
    clock_speed=cpu_info_list[0]
    load_percentage=cpu_info_list[1]
    thread_number=cpu_info_list[3]
    lock.acquire()
    file.write("CPU INFORMATION\t--time stamp: {}\n".format(datetime.datetime.now()))
    file.write('Name: {}\n'.format(cpu_name))
    file.write('Current clock speed: {}\n'.format(clock_speed))
    file.write('Load Percentage: {}\n'.format(load_percentage))
    file.write('Number of threads: {}\n'.format(thread_number))
    lock.release()

def cpu_fast(file):
    command = ['wmic', 'cpu', 'get', 'Name,CurrentClockSpeed,ThreadCount']
    cfg = subprocess.run(command, capture_output=True, shell=True, text=True, check=True)
    output_lines = cfg.stdout.strip().splitlines()

    cpu_info_list = re.split('\s{2,}', output_lines[2].strip())
    cpu_name=cpu_info_list[1]
    clock_speed=cpu_info_list[0]

    thread_number=cpu_info_list[2]
    lock.acquire()
    file.write("CPU INFORMATION\t--time stamp: {}\n".format(datetime.datetime.now()))
    file.write('Name: {}\n'.format(cpu_name))
    file.write('Current clock speed: {}\n'.format(clock_speed))
    file.write('Number of threads: {}\n'.format(thread_number))
    lock.release()

def gpu_info(file):
    command = ['nvidia-smi', '--query-gpu=name,temperature.gpu,memory.used,memory.total',
               '--format=csv,noheader,nounits']
    cfg = subprocess.run(command, capture_output=True, shell=True, text=True, check=True)
    gpu_data = cfg.stdout.strip().split(',')
    gpu_name = gpu_data[0]
    gpu_temperature = gpu_data[1]
    gpu_usedmem = int(gpu_data[2])
    gpu_totalmem = int(gpu_data[3])
    div = gpu_usedmem/gpu_totalmem
    lock.acquire()
    file.write("GPU INFORMATION\t--time stamp: {}\n".format(datetime.datetime.now()))
    file.write("Name: {}\n".format(gpu_name))
    file.write("Temp in celcius: {}\n".format(gpu_temperature))
    file.write("Total vram: {}\n".format(gpu_totalmem))
    file.write("Used vram: {}\n".format(gpu_usedmem))
    file.write("Used vram ratio: {}\n".format(div))
    lock.release()

def memory_info(file):
    command = ['wmic', 'OS', 'get', 'FreePhysicalMemory,TotalVisibleMemorySize']
    cfg = subprocess.run(command, capture_output=True, shell=True, text=True, check=True)
    data = cfg.stdout.strip().split()
    used=int(data[2])
    total=int(data[3])
    lock.acquire()
    file.write("MEMORY INFORMATION\t--time stamp: {}\n".format(datetime.datetime.now()))
    file.write('Total memory: {}\n'.format(total))
    file.write('Used memory: {}\n'.format(used))
    file.write('Used memory ratio: {}\n'.format(used / total))
    lock.release()

def mem_cont(file):
    mem_command = ['wmic', 'OS', 'get', 'FreePhysicalMemory,TotalVisibleMemorySize']
    cfg = subprocess.run(mem_command, capture_output=True, shell=True, text=True, check=True)
    # memory
    data = cfg.stdout.strip().split()
    mem_used = int(data[2])
    mem_total = int(data[3])
    lock.acquire()
    file.write('Used memory ratio: {}\t Time stamp: {}\n'.format(mem_used / mem_total, datetime.datetime.now()))
    lock.release()

def cpu_cont(file):
    command = ['wmic', 'cpu', 'get', 'CurrentClockSpeed']
    cfg = subprocess.run(command, capture_output=True, shell=True, text=True, check=True)
    output_lines = cfg.stdout.strip().splitlines()

    clock_speed = output_lines[2]


    lock.acquire()
    file.write('Current cpu clock speed: {}\t Time stamp: {}\n'.format(clock_speed, datetime.datetime.now()))
    lock.release()

def gpu_cont(file):
    gpu_command = ['nvidia-smi', '--query-gpu=temperature.gpu,memory.used,memory.total',
                   '--format=csv,noheader,nounits']
    cfg = subprocess.run(gpu_command, capture_output=True, shell=True, text=True, check=True)
    # gpu
    gpu_data = cfg.stdout.strip().split(',')
    gpu_temperature = gpu_data[0]
    gpu_usedmem = int(gpu_data[1])
    gpu_totalmem = int(gpu_data[2])
    div = gpu_usedmem / gpu_totalmem
    lock.acquire()
    file.write("GPU-Temp in celcius: {}\t Time stamp: {}\n".format(gpu_temperature, datetime.datetime.now()))
    file.write("Total vram: {}\n".format(gpu_totalmem))
    file.write("Used vram: {}\n".format(gpu_usedmem))
    file.write("Used vram ratio: {}\n".format(div))
    lock.release()
output_file = open("system_info.txt", "w")

task1=threading.Thread(target=cpu_fast,args=[output_file])
task2=threading.Thread(target=gpu_info,args=[output_file])
task3=threading.Thread(target=memory_info,args=[output_file])

task1.start()
task2.start()
task3.start()
task1.join()
task2.join()
task3.join()

task4 = threading.Thread(target=cpu_cont,args=[output_file])
task5 = threading.Thread(target=gpu_cont,args=[output_file])
task6 = threading.Thread(target=mem_cont,args=[output_file])
while True:
    try:

        task4.start()
        task5.start()
        task6.start()
        task4.join()
        task5.join()
        task6.join()
        output_file.write("SLEEPING\n")
        output_file.write("SLEEPING\n")
        output_file.write("SLEEPING\n")
        time.sleep(wait)
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Terminating...")
        print(task6.is_alive())
        break
output_file.close()
