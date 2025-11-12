from concurrent.futures import ThreadPoolExecutor
from enum import Enum
import queue
import uuid
from datetime import datetime

# main.py -> EventBus(PubThreads, SubThreads), add publisher, add subscriber, add topic, create event, (push event, pull event) -> Executor.push, Executor.pull 

class EventType(Enum):
    log = 1
    failure = 2


class Event:
    def __init__(self, publisher, eventType: EventType, description, creationTime):
        self.publisher = publisher
        self.eventType = eventType
        self.id = str(uuid.uuid4())
        self.description = description
        self.creationTime = creationTime

    def getId(self):
        return self.id

    def getPublisher(self):
        return self.publisher

    def getEventType(self):
        return self.eventType
    
    def getDescription(self):
        return self.description

    def getCreationTime(self):
        return self.creationTime


class FailureEvent(Event):
    def __init__(self, event, publisher, throwable):
        super().__init__(publisher, EventType.failure, str(throwable), datetime.now())
        self.event = event
        self.throwable = throwable
    
    def getThrowable(self):
        return self.throwable

    def getEvent(self):
        return self.event


class Executor:
    def __init__(self, subscriberThreads, publisherThreads) -> None:
        self.PublisherExecutors = [ThreadPoolExecutor(max_workers=1) for _ in range(publisherThreads)]
        self.SubscriberExecutors = [ThreadPoolExecutor(max_workers=1) for _ in range(subscriberThreads)]

    def push(self, event, q, key):
        return self.PublisherExecutors[hash(key) % len(self.PublisherExecutors)].submit(q.put, event)

    def pull(self, q, key):
        return self.SubscriberExecutors[hash(key) % len(self.SubscriberExecutors)].submit(q.get)


class EventBus:
    def __init__(self, subscriberThreads, publisherThreads):
        self.executor = Executor(subscriberThreads, publisherThreads)
        self.topics = {}
        self.subscribers = {} # maintain topic : [subscribers]
        self.publishers = {} # maintain topic : [publishers]

    def addTopics(self, topic):
        self.topics[topic] = queue.Queue()

    def addSubscribers(self, subscriber, topic):
        if topic in self.subscribers:
            self.subscribers[topic].append(subscriber)
        else:
            self.subscribers[topic] = [subscriber]

    def addPublishers(self, publisher, topic):
        if topic in self.publishers:
            self.publishers[topic].append(publisher)
        else:
            self.publishers[topic] = [publisher]

    def push(self, event:Event, publisher, topic):
        return self.executor.push(event, self.topics[topic], publisher + topic)

    def pull(self, subscriber, topic):
        return self.executor.pull(self.topics[topic], subscriber + topic)


if __name__ == "__main__":
    eventBus = EventBus(10, 10)
    eventBus.addTopics('log')
    eventBus.addPublishers('Mayank', 'log')
    eventBus.addSubscribers('Kunal', 'log')

    event = Event('Mayank', EventType.log, 'testEvent', datetime.now())
    eventBus.push(event, 'Mayank', 'log')
    result = eventBus.pull('Kunal', 'log').result()
    print(result.getId())

    # event2 = Event('Mayank', EventType.log, 'testEvent', datetime.now())
    # failureEvent = FailureEvent(event2, 'Mayank', 24)
    # eventBus.push(failureEvent, 'Mayank', 'log')
    # result = eventBus.pull('Kunal', 'log').result()
    # print(result.getThrowable())


    


