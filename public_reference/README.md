# 部门协作参考实现

此目录是独立、可运行的协作层范例。`algorithm_gateway.py` 只定义算法服务应交付的信号信封；它不含策略规则，且不能在本仓库中补充任何策略实现。

## 调用流程

1. 研发部门调用 `POST /internal/minute-bars` 写入已获得的分钟行情。
2. 研发部门调用 `POST /internal/signals` 投递算法服务已经生成的信号。`payload` 被当作不透明 JSON 保存，不解析其含义。
3. 通讯部门调用 `GET /users/{user_id}/positions` 查询信息部门持仓。
4. 通讯部门调用 `POST /users/{user_id}/operations` 录入手动操作；信息部门以一个事务同时写入操作记录和持仓快照。

这说明各部门如何互通，不说明“何时产生何种信号”。真实系统应在网关、鉴权、审计和受控网络中替换这个示例。
