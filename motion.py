import mpu6050 as mpu
import timer
import sys
from logger import log as log
import asyncio
import time

# have to use an asynio timer instead to read MPU6050
# TODO: add a interrupt pin option

print_every_sample = False # print every sample
print_theshold_sample = False # print data past a threshold diff from one sample to the next
print_thresh = 500

class motion_data:
    __slots__ = ["ax", "ay", "az", "gx", "gy", "gz"]
    def __init__(self):
        self.ax = sys.maxsize # instantaneous motion
        self.ay = sys.maxsize
        self.az = sys.maxsize
        self.gx = sys.maxsize
        self.gy = sys.maxsize
        self.gz = sys.maxsize

class Motion:
    def __init__(self, swing_detected, hit_detected):
        self.mpu_time = 0.025 # 25 ms
        self.data = motion_data()
        self.last_data = motion_data()

        self.swing_change_cnt = 0
        self.hit_change_cnt = 0
        self.swing_diff = 400
        self.swing_cnt = 3
        self.swing_debounce = 0.5 # read time isn't exactly mpu_time above. so tweaking this lower to come out to about 1sec
        # we want to debounce swing sounds, but not debounce readings
        # so we can detect a hit at the end.
        self.swing_debounce_acc = 0.0

        self.hit_diff = 15000
        self.hit_cnt = 1
        self.hit_debounce = 1.0
        self.hit_ignore_next = True # ignore the very first

        self.swing_detected = swing_detected
        self.hit_detected = hit_detected

        self.IOError = False

        mpu.MPU_Init()
        self.timer = 0
        #timer.Timer(self.mpu_time, self.mpu_timer_callback, True)

    def start(self):
        self.timer = timer.Timer(self.mpu_time, self.mpu_timer_callback, True)

    def stop(self):
        self.timer.cancel()


    def cache_data(self):
        self.last_data.ax = self.data.ax
        self.last_data.ay = self.data.ay
        self.last_data.az = self.data.az
        self.last_data.gx = self.data.gx
        self.last_data.gy = self.data.gy
        self.last_data.gz = self.data.gz

    async def mpu_timer_callback(self, repeat, timeout):
        try:
            # we had an IOError last time - try to fix it.
            if self.IOError:
                mpu.MPU_Init()
                # assume it worked. if still broken will get caught below
                self.IOError = False
        except Exception as e:
            log.error(">>>>Error>>>> {} (still down)".format(e))

        # sometimes we may get a bus error which results in an exception
        # we need to ignore this and continue taking samples
        try:
            # save power reading raw values
            self.data.ax = mpu.read_raw_data(mpu.ACCEL_XOUT_H)
            self.data.ay = mpu.read_raw_data(mpu.ACCEL_YOUT_H)
            self.data.az = mpu.read_raw_data(mpu.ACCEL_ZOUT_H)
            self.data.gx = mpu.read_raw_data(mpu.GYRO_XOUT_H)
            self.data.gy = mpu.read_raw_data(mpu.GYRO_YOUT_H)
            self.data.gz = mpu.read_raw_data(mpu.GYRO_ZOUT_H)
        except Exception as e:
            log.error(">>>> MPU Error>>>> {} ".format(e))
            # possible we lost power to the MPU
            # wait a second longer than normal and set IOError so
            # we will reinitialize next time
            self.IOError = True
            self.data.__init__()
            self.timer = timer.Timer(self.mpu_time + 1, self.mpu_timer_callback, True)
            return

        # if readings change from one to the next by a certain amount
        # we can detect motion
        if self.data.ax == sys.maxsize or self.hit_ignore_next:
            # make sure we start with a valid reading
            self.cache_data()
            self.hit_ignore_next = False
            self.timer = timer.Timer(self.mpu_time, self.mpu_timer_callback, True)
            return

        diff_ax = abs(abs(self.last_data.ax) - abs(self.data.ax))
        #log.debug("diff_ax {} self.last_data.ax {} acc_x {}", format(diff_ax,self.last_data.ax, acc_x))
        diff_ay = abs(abs(self.last_data.ay) - abs(self.data.ay))
        diff_az = abs(abs(self.last_data.az) - abs(self.data.az))
        diff_gz = abs(abs(self.last_data.gz) - abs(self.data.gz))

        printv = False
        if print_every_sample: printv = True
        if print_theshold_sample and (
            diff_ax > print_thresh or
            diff_ay > print_thresh or
            diff_az > print_thresh 
        ): printv = True

        if printv:
            log.debug("ax %6d\t ay %6d\t az %6d\t dx %6d\t dy %6d\t dz %6d\t gx %6d\t gy %6d\t gz %6d\t",
                self.data.ax, self.data.ay, self.data.az, 
                diff_ax, diff_ay, diff_az,
                self.data.gx, self.data.gy, self.data.gz      )

        if diff_ax > self.hit_diff or \
        diff_ay > self.hit_diff or \
        diff_az > self.hit_diff:
            self.hit_change_cnt += 1
            log.debug("hit {}".format(self.hit_change_cnt))
            if self.hit_change_cnt >= self.hit_cnt:
                await self.hit_detected()
                self.hit_change_cnt = 0
                self.cache_data()
                self.timer = timer.Timer(self.hit_debounce, self.mpu_timer_callback, True)
                # and ignore the next reading
                self.hit_ignore_next = True
                return       
        else:
            self.hit_change_cnt = 0

        # only look for swing if we haven't detected a hit. ? (handled by hit debounce)
        # if we're debouncing a swing wait until we reevaludate
        self.swing_debounce_acc -= self.mpu_time
        #print(self.swing_debounce_acc)
        if self.swing_debounce_acc <= 0.0:
            
            if diff_gz > self.swing_diff:
                self.swing_change_cnt += 1
                log.debug("swing {}".format(self.swing_change_cnt))
                if self.swing_change_cnt >= self.swing_cnt:
                    await self.swing_detected()
                    self.swing_change_cnt = 0
                    self.cache_data()
                    self.swing_debounce_acc = self.swing_debounce
                    self.timer = timer.Timer(self.mpu_time, self.mpu_timer_callback, True)
                    return
            else:
                if self.swing_change_cnt > 0:
                    self.swing_change_cnt -= 1
                else:
                    self.swing_change_cnt = 0
            self.swing_debounce_acc = 0.0
    
        self.cache_data()
        self.timer = timer.Timer(self.mpu_time, self.mpu_timer_callback, True)
