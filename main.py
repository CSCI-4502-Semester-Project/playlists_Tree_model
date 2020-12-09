from client import client
import os

if __name__ == '__main__':

    inp = 'D:\\spotify_data_dump\\integrated_data\\'
    
    N = 0
    break_num = 10000

    for filename in os.listdir(inp):
        if filename.endswith('.INDEX'):
            pid = filename.split('.')[0]

            rv = client.run(pid, 'push')            
        if rv == True:
            print(pid)
        else:
            print('ERROR ----- %s' % pid)

        if N >= break_num:
            break;
        
        N+=1
    print('Done...')
