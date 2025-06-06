import random
import simpy
import numpy as np

RANDOM_SEED = 42  # for debugging during dev
NEW_CUSTOMERS = 500  # Total number of customers

INTERVAL_CUSTOMERS = 10.0  # Generate new customers roughly every x seconds
MIN_PATIENCE = 3  # Min. customer patience
MAX_PATIENCE = 10  # Max. customer patience

AVG_SERVICE_TIME = [12, 13, 5, 30]  # 4 services



waitingtime = []
queuelgth = []

def source(env, number, interval, counters, frontcounter):
    """Source generates customers randomly"""
    #for i in range(number):

    starttime = env.now
    numcustomers = 0
    while True:
            # generator function
        service_index = random.randint(0, len(AVG_SERVICE_TIME)-1)
        c = customer(env, f'Customer{numcustomers:02d}', counters[service_index], frontcounter, time_in_bank=AVG_SERVICE_TIME[service_index])
        env.process(c)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)
        numcustomers += 1

        #queuelgth.append(len(counter.queue))

        timeelapsed = env.now - starttime
        if timeelapsed > 8*60:
            break


def customer(env, name, counter, frontcounter, time_in_bank):
    """Customer arrives, is served and leaves."""
    arrive = env.now
    print(f'{arrive:7.4f} {name}: Here I am')

    # 2) go to front counter first
    with frontcounter.request() as req:  # make a request for number
        # Wait for the frontcounter service
        yield req



    # queue at actual counter
    with counter.request() as req:
        patience = random.uniform(MIN_PATIENCE, MAX_PATIENCE)
        # Wait for the counter or abort at the end of our tether
        results = yield req | env.timeout(patience)

        wait = env.now - arrive
        waitingtime.append(wait)

        if req in results:
            # We got to the counter
            print(f'{env.now:7.4f} {name}: Waited {wait:6.3f}')

            tib = random.expovariate(1.0 / time_in_bank)
            yield env.timeout(tib)
            print(f'{env.now:7.4f} {name}: Finished')

        else:
            # We reneged
            print(f'{env.now:7.4f} {name}: RENEGED after {wait:6.3f}')


# Setup and start the simulation
print('Bank renege')
random.seed(RANDOM_SEED)
env = simpy.Environment()

# Start processes and run

# 1) create a special front counter
frontcounter = simpy.Resource(env, capacity=1)

counters = []
for i in range(len(AVG_SERVICE_TIME)):
    counters.append(simpy.Resource(env, capacity=1))

env.process(source(env, NEW_CUSTOMERS, INTERVAL_CUSTOMERS, counters, frontcounter))
env.run()

print('waiting time: ', waitingtime)
print('queues: ', queuelgth)
print('avg wait: ', np.average(waitingtime))
print('max wait: ', np.max(waitingtime))