from app.ai.operation_summary import summarize_lot_validation
from app.routers.ai import lot_summary
from app.schemas import LotSummaryRequest


def test_summarize_lot_validation_spanish_sentence():
    result = summarize_lot_validation(
        scanned_count=84,
        unknown_count=2,
        duplicate_count=1,
        missing_count=3,
    )
    assert result == (
        "Se leyeron 84 animales, hay 2 desconocidos, 1 duplicado y faltan 3 respecto al lote esperado."
    )


def test_lot_summary_endpoint_function_returns_summary():
    payload = LotSummaryRequest(
        expected_count=87,
        scanned_count=84,
        duplicate_rfid_codes=["RFID-1"],
        unknown_rfid_codes=["RFID-X", "RFID-Y"],
        missing_count_estimate=3,
        status_summary="Conteo incompleto",
    )

    result = lot_summary(payload)
    assert result["summary"] == (
        "Se leyeron 84 animales, hay 2 desconocidos, 1 duplicado y faltan 3 respecto al lote esperado."
    )
