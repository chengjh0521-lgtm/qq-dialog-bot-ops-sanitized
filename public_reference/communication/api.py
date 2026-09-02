"""通讯部门的 HTTP 边界：将用户请求转交给信息部门。"""

from fastapi import FastAPI, HTTPException

from public_reference.contracts import ManualOperationIn, MinuteBarIn, OpaqueSignalIn, PositionOut
from public_reference.information.repository import InformationRepository
from public_reference.research.algorithm_gateway import accept_algorithm_output

app = FastAPI(title="Department Collaboration Reference")
repository = InformationRepository()


@app.post("/internal/minute-bars", status_code=202)
def publish_minute_bar(bar: MinuteBarIn) -> dict[str, str]:
    repository.save_minute_bar(bar)
    return {"status": "accepted"}


@app.post("/internal/signals", status_code=202)
def publish_opaque_signal(signal: OpaqueSignalIn) -> dict[str, str]:
    repository.store_opaque_signal(accept_algorithm_output(signal))
    return {"status": "accepted"}


@app.get("/users/{user_id}/positions", response_model=PositionOut)
def get_position(user_id: str, instrument: str) -> PositionOut:
    return repository.get_position(user_id, instrument)


@app.post("/users/{user_id}/operations", response_model=PositionOut)
def create_operation(user_id: str, instrument: str, operation: ManualOperationIn) -> PositionOut:
    try:
        return repository.record_operation(user_id, instrument, operation)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
