import time
from collections import deque
from threading import Lock




# All these algorithms do a user based rate limiting. This gives each user equal quota to utilise the applicaiton.
# There are certain global level rate limiters also, which does rate limiting on IP basis. 
# in clean up use ttl from redis or if we want manual cleanup then use cleanup_expired_users with an self.expiry time.

class FixedWindowRateLimiter:
    def __init__(self, max_requests, window_seconds, expiry_seconds=None):
        self.max_requests = max_requests
        self.window = window_seconds
        self.expiry = expiry_seconds if expiry_seconds is not None else window_seconds * 2
        self.counters = {}  # userID -> [count, window_start]
        self.lock = Lock()

    def cleanup_expired_users(self):
        now = time.time()
        to_delete = [user_id for user_id, (_, start) in self.counters.items()
                     if now - start > self.expiry]
        for user_id in to_delete:
            del self.counters[user_id]

    def allow_request(self, user_id):
        with self.lock:
            self.cleanup_expired_users()  

            now = time.time()
            window_start = int(now // self.window) * self.window  # we are fixing the window boundary here
            if user_id not in self.counters:
                self.counters[user_id] = [0, window_start]
            count, start = self.counters[user_id]
            if start != window_start: # if the last request which came by this user is outside window so start fresh
                count, start = 0, window_start
            if count < self.max_requests: # if the last request which came by this user is inside window so check count and update counter
                self.counters[user_id] = [count + 1, start]
                print(self.counters)
                return True
            print(self.counters)
            return False



class TokenBucketRateLimiter:
    def __init__(self, max_tokens, refill_rate_per_sec, expiry_seconds=None):
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate_per_sec
        self.expiry = expiry_seconds if expiry_seconds is not None else (max_tokens / refill_rate_per_sec) * 2
        self.buckets = {}  # userID -> [tokens, startTime]
        self.lock = Lock()

    def cleanup_expired_users(self):
        now = time.time()
        to_delete = [user_id for user_id, (_, last) in self.buckets.items()
                     if now - last > self.expiry]
        for user_id in to_delete:
            del self.buckets[user_id]

    def allow_request(self, user_id):
        with self.lock:
            self.cleanup_expired_users()

            now = time.time()
            if user_id not in self.buckets:
                self.buckets[user_id] = [self.max_tokens, now]
            tokens, last = self.buckets[user_id]
            new_tokens = (now - last) * self.refill_rate
            tokens = min(self.max_tokens, tokens + new_tokens)
            if tokens >= 1:
                self.buckets[user_id] = [tokens - 1, now]
                print(self.buckets)
                return True
            # self.buckets[user_id][1] = now # this will prevent token accumulation during idle times. If we don't do this then we are granting a large burst of tokens instantly where our app might crash
            print(self.buckets)
            return False



class LeakyBucketRateLimiter:
    def __init__(self, capacity, leak_rate_per_sec, expiry_seconds=None):
        self.capacity = capacity
        self.leak_rate = leak_rate_per_sec
        self.expiry = expiry_seconds if expiry_seconds is not None else 60
        self.buckets = {}  # {user_id : [deque([time]), time]}
        self.lock = Lock()

    def cleanup_expired_users(self):
        now = time.time()
        to_delete = [user_id for user_id, (_, start) in self.buckets.items()
                     if now - start > self.expiry]
        for user_id in to_delete:
            del self.buckets[user_id]

# last_leak - It marks the point in time when the bucket was last drained (leaked) partially or fully.
# last_leak= last_leak+ leak_rate/leaked 
# Suppose the time now is 2.5 sec elapsed the last requests came at 0.1, 0.2, 0.3.... the requests leak at 1 req/sec and the capacity of queue is 3. Now, the queue is full.
# we do this calculation because, if you see closely the last request came at 0.3 and requests leak at 1 req/sec so, the 2 requests will leak between t = 0.3 and t = 2.5sec.
# But, these requests will not leak at t = 2.5 accourding to bucket but at t = 2.3 which is 2 + 0.3sec, so we store it like that to avoid fractional failures later.
 
    def allow_request(self, user_id):
        with self.lock:
            self.cleanup_expired_users()

            now = time.time()
            if user_id not in self.buckets:
                self.buckets[user_id] = [deque(), now]
            q, last_leak = self.buckets[user_id]
            leaked = int((now - last_leak) * self.leak_rate)
            for _ in range(min(leaked, len(q))):
                q.popleft()
            last_leak = (last_leak + leaked / self.leak_rate) if leaked else now # This moves the leak clock forward exactly by the elapsed leaking time to synchronize the bucket's internal clock with real time.
            self.buckets[user_id][1] = last_leak
            if len(q) < self.capacity:
                print(self.buckets)
                q.append(now)
                return True
            print(self.buckets)
            return False


# we are not setting up any window start and the window moves. The window now starts from log[0] to time.time(). 
class SlidingWindowLogRateLimiter:
    def __init__(self, max_requests, window_seconds, expiry_seconds=None):
        self.max_requests = max_requests
        self.window = window_seconds
        self.expiry = expiry_seconds if expiry_seconds is not None else window_seconds * 2
        self.logs = {}  # user_id -> deque of timestamps
        self.lock = Lock()

    def cleanup_expired_logs(self):
        now = time.time()
        to_delete = [user_id for user_id, timestamps in self.logs.items()
                     if not timestamps or now - timestamps[-1] > self.expiry]
        for user_id in to_delete:
            del self.logs[user_id]

    def allow_request(self, user_id):
        with self.lock:
            self.cleanup_expired_logs()  

            now = time.time()
            if user_id not in self.logs:
                self.logs[user_id] = deque()
            log = self.logs[user_id]
            while log and now - log[0] > self.window:
                log.popleft()
            if len(log) < self.max_requests:
                print(self.logs)
                log.append(now)
                return True
            print(self.logs)
            return False



class SlidingWindowCounterWithWeightedWindow:
    def __init__(self, max_requests, window_seconds, expiry_seconds=None):
        self.max_requests = max_requests
        self.window = window_seconds
        self.expiry = expiry_seconds if expiry_seconds is not None else window_seconds * 2
        self.counters = {}  # user_id -> {window_start: count}
        self.lock = Lock()

    def _get_window_start(self, now):
        return int(now // self.window) * self.window

    def _cleanup_user_windows(self, user_id, now):
        """Keep only current and previous window for a user."""
        window_start = self._get_window_start(now)
        prev_window_start = window_start - self.window

        if user_id not in self.counters:
            return
        user_windows = self.counters[user_id]

        # Drop anything older than prev_window_start
        for ws in list(user_windows.keys()):
            if ws < prev_window_start:
                del user_windows[ws]

        # Drop user entirely if no activity for too long
        if not user_windows:
            del self.counters[user_id]

    def _cleanup_all_users(self):
        """Global cleanup to evict users idle beyond expiry."""
        now = time.time()
        to_delete = []
        for user_id, user_windows in self.counters.items():
            # Find the latest window recorded for this user
            last_activity = max(user_windows.keys()) if user_windows else 0
            if now - last_activity > self.expiry:
                to_delete.append(user_id)
        for user_id in to_delete:
            del self.counters[user_id]

    def allow_request(self, user_id):
        with self.lock:
            now = time.time()
            window_start = self._get_window_start(now)
            prev_window_start = window_start - self.window

            self._cleanup_user_windows(user_id, now)
            self._cleanup_all_users()

            if user_id not in self.counters:
                self.counters[user_id] = {}

            user_windows = self.counters[user_id]

            user_windows.setdefault(window_start, 0)
            user_windows.setdefault(prev_window_start, 0) # previous window gets created automatically when the user first made requests in it

            curr_count = user_windows[window_start]
            prev_count = user_windows[prev_window_start]

            elapsed = now - window_start
            fraction = elapsed / self.window  # how far into window

            effective_count = curr_count + prev_count * (1 - fraction) # Because curr_count already contains the requests so far in curr window. 
            #The approximation in this approach only tracks the contribution of the previous bucket and not the curr one, forget the theory.
            # print(effective_count)
            if effective_count < self.max_requests:
                user_windows[window_start] = curr_count + 1
                print(self.counters)
                return True
            print(self.counters)
            return False




class SlidingWindowSubCounterRateLimiter:
    def __init__(self, max_requests, window_seconds, num_sub_windows=10):
        self.max_requests = max_requests
        self.window = window_seconds
        self.sub_window_size = window_seconds / num_sub_windows
        self.num_sub_windows = num_sub_windows
        self.counters = {}  # user_id -> deque of (sub_window_start, count)
        self.lock = Lock()

    def _cleanup_user(self, user_id, now):
        """Remove old sub-windows outside of the main window."""
        if user_id not in self.counters:
            return
        window_start_cutoff = now - self.window
        user_deque = self.counters[user_id]

        while user_deque and user_deque[0][0] <= window_start_cutoff:
            user_deque.popleft()

        if not user_deque:  # if no activity, free memory
            del self.counters[user_id]

    def allow_request(self, user_id):
        with self.lock:
            now = time.time()
            self._cleanup_user(user_id, now)

            if user_id not in self.counters:
                self.counters[user_id] = deque()
            user_deque = self.counters[user_id]

            # find current sub-window start
            sub_window_start = int(now // self.sub_window_size) * self.sub_window_size

            if user_deque and user_deque[-1][0] == sub_window_start:
                # already in same sub-window, so increment
                user_deque[-1] = (user_deque[-1][0], user_deque[-1][1] + 1)
            else:
                # push a new sub-window
                user_deque.append((sub_window_start, 1))

            # compute total in the last full window
            total_count = sum(count for _, count in user_deque) # we don't check the last window size and then check it's subwindows for finding totals
            # this is because we are evicting everything older than now - window, all remaining sub-windows are automatically inside the current sliding window. 
            # check this line - window_start_cutoff = now - self.window
            print(self.counters)
            if total_count <= self.max_requests:
                return True
            else:
                return False


import time

def main():
    user = "user_123"

    # print("=== Fixed Window Rate Limiter ===")
    # fixed_limiter = FixedWindowRateLimiter(max_requests=3, window_seconds=12)
    # for i in range(5):
    #     allowed = fixed_limiter.allow_request(user)
    #     print(f"Request {i+1}: {'ALLOWED ✅' if allowed else 'BLOCKED ❌'}")
    #     time.sleep(1)
    # time.sleep(5)  # wait for window reset
    # print("After window reset:")
    # print(fixed_limiter.allow_request(user))  # should be allowed



    # print("\n=== Token Bucket Rate Limiter ===")
    # token_limiter = TokenBucketRateLimiter(max_tokens=3, refill_rate_per_sec=1)
    # for i in range(20):
    #     allowed = token_limiter.allow_request(user)
    #     print(f"Request {i+1}: {'ALLOWED ✅' if allowed else 'BLOCKED ❌'}")
    #     time.sleep(0.5)  # refill happens over time
    # time.sleep(3)
    # print("After refill:")
    # print(token_limiter.allow_request(user))  # should be allowed



    # print("\n=== Leaky Bucket Rate Limiter ===")
    # leaky_limiter = LeakyBucketRateLimiter(capacity=3, leak_rate_per_sec=1)
    # for i in range(5):
    #     allowed = leaky_limiter.allow_request(user)
    #     print(f"Request {i+1}: {'ALLOWED ✅' if allowed else 'BLOCKED ❌'}")
    #     time.sleep(0.5)
    # time.sleep(4)
    # print("After leak:")
    # print(leaky_limiter.allow_request(user))  # should be allowed



    # print("\n=== Sliding Window Log Rate Limiter ===")
    # sliding_log_limiter = SlidingWindowLogRateLimiter(max_requests=3, window_seconds=5)
    # for i in range(15):
    #     allowed = sliding_log_limiter.allow_request(user)
    #     print(f"Request {i+1}: {'ALLOWED ✅' if allowed else 'BLOCKED ❌'}")
    #     time.sleep(1)
    # time.sleep(5)
    # print("After window reset:")
    # print(sliding_log_limiter.allow_request(user))  # should be allowed


    # print("\n=== Sliding Window Counter (Weighted) ===")
    # sliding_weighted_limiter = SlidingWindowCounterWithWeightedWindow(max_requests=3, window_seconds=5)
    # for i in range(15):
    #     allowed = sliding_weighted_limiter.allow_request(user)
    #     print(f"Request {i+1}: {'ALLOWED ✅' if allowed else 'BLOCKED ❌'}")
    #     time.sleep(1)
    # time.sleep(5)
    # print("After window reset:")
    # print(sliding_weighted_limiter.allow_request(user))  # should be allowed


    # print("\n=== Sliding Window Sub-Counter Rate Limiter ===")
    # sliding_sub_counter_limiter = SlidingWindowSubCounterRateLimiter(max_requests=3, window_seconds=5, num_sub_windows=5)
    # for i in range(5):
    #     allowed = sliding_sub_counter_limiter.allow_request(user)
    #     print(f"Request {i+1}: {'ALLOWED ✅' if allowed else 'BLOCKED ❌'}")
    #     time.sleep(1)
    # time.sleep(5)
    # print("After window reset:")
    # print(sliding_sub_counter_limiter.allow_request(user))  # should be allowed


if __name__ == "__main__":
    main()



# app = FastAPI()
# @app.get("/data")
# @rate_limit(type="token_bucket", limit=5, per=10)
# def get_data():
#     return {"msg": "Success!"}


# storage.py(for persistence)
import time
from abc import ABC, abstractmethod

class Storage:
    def __init__(self, store):
        self.store = store
        pass

    @abstractmethod
    def get(self, key):
        pass
    
    @abstractmethod
    def set(self, key, value):
        pass

    @abstractmethod
    def delete(self, key):
        pass


import threading

class InMemoryStore:
    # make this singleton
    _object = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._object == None:
                cls._object = super(InMemoryStore, cls).__new__(cls)
                cls._object.store = {}
        return cls._object

    @abstractmethod
    def getInstance(cls):
        return InMemoryStore()

    
    def get(self, key):
        return self.store.get(key)

    def set(self, key, value):
        self.store[key] = value

    def delete(self, key):
        del self.store[key]

from threading import Lock
from collections import deque


class FixedWindowRateLimiter:
    pass

# factory.py # if you add it later
class RateLimiterFactory:

    def get_rate_limiter(self, limiter_type, key, max_requests, window_seconds, storage):
        if limiter_type == "token_bucket":
            return FixedWindowRateLimiter(key, max_requests, window_seconds, storage)
        # elif limiter_type == "leaky_bucket":
            # return LeakyBucketLimiter(key, max_requests, window_seconds, storage)
        else:
            raise ValueError(f"Unknown rate limiter type: {limiter_type}")


from functools import wraps
class Decorator:
    def __init__(self) -> None:
        self.store = InMemoryStore()  # shared singleton
        self.RateLimiterFactory = RateLimiterFactory()

    def rate_limit(self, type, limit=10, per=60):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = f"{func.__name__}"  # could use user_id, IP, etc.
                limiter = self.RateLimiterFactory.get_rate_limiter(type, key, limit, per, self.store)
                if not limiter.allow_request():
                    return {"error": "Too Many Requests"}, 429
                return func(*args, **kwargs)
            return wrapper
        return decorator
