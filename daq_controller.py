import nidaqmx
from nidaqmx.constants import Level, AcquisitionType

class DAQController:
    def __init__(self):
        self.ao_task_x = nidaqmx.Task()
        self.ao_task_y = nidaqmx.Task()
        self.ctr_task_on = nidaqmx.Task()
        self.ctr_task_off = nidaqmx.Task()

        self.setup_tasks()
        self.is_running = True  # 新增状态标志

    def setup_tasks(self):
        # Clear existing tasks to prevent duplication
        self.ao_task_x.close()
        self.ao_task_y.close()
        self.ctr_task_on.close()
        self.ctr_task_off.close()

        # Re-create tasks to ensure they are clean
        self.ao_task_x = nidaqmx.Task()
        self.ao_task_y = nidaqmx.Task()
        self.ctr_task_on = nidaqmx.Task()
        self.ctr_task_off = nidaqmx.Task()

        # Add channels
        self.ao_task_x.ao_channels.add_ao_voltage_chan("Dev1/ao0")
        self.ao_task_y.ao_channels.add_ao_voltage_chan("Dev1/ao1")
        # ... rest of your setup

        channel_on = self.ctr_task_on.co_channels.add_co_pulse_chan_freq(
            "Dev1/ctr0", idle_state=Level.LOW, initial_delay=0.5e-3, freq=1000, duty_cycle=0.01
        )
        channel_off = self.ctr_task_off.co_channels.add_co_pulse_chan_freq(
            "Dev1/ctr1", idle_state=Level.LOW, initial_delay=0, freq=1000, duty_cycle=0.5
        )

        self.ctr_task_on.timing.cfg_implicit_timing(sample_mode=AcquisitionType.FINITE, samps_per_chan=1)
        self.ctr_task_off.timing.cfg_implicit_timing(sample_mode=AcquisitionType.FINITE, samps_per_chan=1)

        channel_on.co_pulse_term = "/Dev1/PFI12"
        channel_off.co_pulse_term = "/Dev1/PFI12"

    def write_voltage(self, x_voltage, y_voltage):
        self.ao_task_x.write(x_voltage)
        self.ao_task_y.write(y_voltage)

    def start_scan(self, on=True):
        if on:
            self.ctr_task_on.start()
            while self.is_running:
                if self.ctr_task_on.is_task_done():
                    break
            self.ctr_task_on.stop()
        else:
            self.ctr_task_off.start()
            while self.is_running:
                if self.ctr_task_off.is_task_done():
                    break
            self.ctr_task_off.stop()
    def close(self):
        # 更改状态以停止任务
        self.is_running = False
        self.actual_close()

    def actual_close(self):
        # 真正关闭所有任务的方法
        self.ao_task_x.close()
        self.ao_task_y.close()
        self.ctr_task_on.close()
        self.ctr_task_off.close()

    def __del__(self):
        # 确保对象被删除时所有任务都被关闭
        self.actual_close()

if __name__ == "__main__":
    controller = DAQController()
    try:
        controller.start_scan(on=True)
    except KeyboardInterrupt:
        controller.close()
    finally:
        controller.close()

