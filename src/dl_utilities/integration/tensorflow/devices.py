import tensorflow as tf
from typing import Optional, TypedDict

from ...hardware import gpu_memory

# Type Definitions ---------------------------------------------------------------------------------

GpuMemoryInfo = TypedDict("GpuMemoryInfo", {"used": int, "free": int, "total": int})

# Interface Functions ------------------------------------------------------------------------------

def best_gpus(
    gpus: Optional[list[tf.config.PhysicalDevice]] = None,
    count: int = 1
) -> list[tf.config.PhysicalDevice]:
    """
    Select the given number of GPUs. The selected devices are prioritized by their available memory.
    """
    memory_utilization = {gpu: memory["free"] for gpu, memory in zip(gpu_list(), gpu_memory())}
    if gpus is None:
        gpus = gpu_list()
    # Sort gpus list by memory utilization
    gpus.sort(key=lambda gpu: memory_utilization[gpu], reverse=True)
    return gpus[:count]


def cpu_list() -> list[tf.config.PhysicalDevice]:
    """
    Get the list of visible CPU devices.
    """
    return tf.config.list_physical_devices("CPU")


def gpu_list() -> list[tf.config.PhysicalDevice]:
    """
    Get the list of visible GPU devices.
    """
    return tf.config.list_physical_devices("GPU")


def use(
    *device_or_devices: tf.config.PhysicalDevice|list[tf.config.PhysicalDevice],
    use_dynamic_memory: bool = True
) -> list[tf.config.PhysicalDevice]:
    """
    Select the specified devices.
    """
    devices = []
    for device in device_or_devices:
        if isinstance(device, tf.config.PhysicalDevice):
            devices.append(device)
        elif isinstance(device, list):
            devices += device
        else:
            raise TypeError(f"Expected PhysicalDevice or list[PhysicalDevice], got {type(device)}")
    cpus = []
    gpus = []
    for device in devices:
        if device.device_type == "CPU":
            cpus.append(device)
        elif device.device_type == "GPU":
            gpus.append(device)
    if len(cpus) > 0:
        tf.config.set_visible_devices(cpus, "CPU")
    if len(gpus) > 0:
        tf.config.set_visible_devices(gpus, "GPU")
    for device in gpus:
        tf.config.experimental.set_memory_growth(device, use_dynamic_memory)
    return tf.config.get_visible_devices()
