from fastapi import APIRouter

router = APIRouter(prefix="/demo", tags=["Demo (temporary)"])


@router.get("/validation")
def validation_demo(number: int):
    """Send ?number=abc to see a 422 validation error."""
    return {"number": number}


@router.get("/crash")
def crash_demo():
    """Deliberately crashes to show the 500 error handler."""
    raise RuntimeError("This is a deliberate test crash")