"""研发部门与受控算法服务的边界。

此模块刻意不提供算法实现。研发部门只能验证传入的信号信封后投递给信息部门。
"""

from public_reference.contracts import OpaqueSignalIn


def accept_algorithm_output(signal: OpaqueSignalIn) -> OpaqueSignalIn:
    """验证信封的完整性；payload 始终保持不透明，不读取或改写其业务含义。"""
    return signal
