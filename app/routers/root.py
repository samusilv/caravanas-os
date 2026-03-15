from fastapi import APIRouter

router = APIRouter(tags=["root"])


@router.get("/", summary="API root")
def root() -> dict:
    return {"status": "ok", "message": "CaravanaOS RFID tracking backend"}
