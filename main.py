from client import client

if __name__ == '__main__':
    pids = ['1Iqp8L8dSUFhpCWfGFb9t3',
            '2xhS724IWN6GEYPOwGxs7a',
            '3HLMmCcl83B8u23ASFxFCQ',
            '4j3idaHG0tnKKyfovyA1B7',
            '5eXFv8u2tyiuTGT2vxeWVh',
            '1trvdVRA6BfcRzdf2SV33K',
            '2nlzz09kBv8EHHV7dFjk74',
            '4J8JzkN98EJQ9fJnEIjtfl',
            '7CJG2aKJthZ9RcS1BGjvtE',
            '15ZKyAKWbOEWaGZYLlpz9N']
    
    for pid in pids:
        rv = client.run(pid, 'push')
        print(rv)
    
    print('Done...')
