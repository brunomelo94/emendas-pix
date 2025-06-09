from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

try:
    # When executed as part of the package
    from .party_service import add_parties_to_csv
except ImportError:  # pragma: no cover - fallback for running as a script
    # When running `python src/app.py`, relative imports are not resolved
    from party_service import add_parties_to_csv

app = FastAPI(title="Emendas Party Service")


class AddPartiesRequest(BaseModel):
    csv_path: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/add-parties")
def add_parties(request: AddPartiesRequest) -> dict[str, int]:
    try:
        rows = add_parties_to_csv(request.csv_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"rows": rows}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.app:app", host="0.0.0.0", port=8000)
