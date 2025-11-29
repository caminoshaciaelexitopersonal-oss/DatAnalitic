# backend/tests/test_etl_pipeline.py
import os
import tempfile
import sqlite3
import pandas as pd
import pytest

from backend.mpa.etl.service import EtlService


class MockStateStore:
    """
    Minimal in-memory state store for tests.
    save_dataframe(session_id, df, append=True)
    load_dataframe(session_id) -> df or None
    """
    def __init__(self):
        self._store = {}

    def save_dataframe(self, session_id: str, df: pd.DataFrame, append: bool = True):
        if session_id in self._store and append:
            existing = self._store[session_id]
            # align columns (union)
            df = pd.concat([existing, df], ignore_index=True, sort=False)
        self._store[session_id] = df.reset_index(drop=True)

    def load_dataframe(self, session_id: str):
        return self._store.get(session_id)


@pytest.fixture
def state_store():
    return MockStateStore()


@pytest.fixture
def etl_service(state_store):
    return EtlService(state_store)


def test_csv_ingest_and_metadata(tmp_path, etl_service, state_store):
    data = "city,pop\nMadrid,6700000\nBarcelona,5600000\n"
    f = tmp_path / "pop.csv"
    f.write_text(data, encoding="utf-8")

    meta = etl_service.ingest_file(str(f), session_id="s1")
    assert meta["rows"] == 2
    assert "city" in meta["columns"]
    df = state_store.load_dataframe("s1")
    assert df.shape == (2, 2)
    assert df["pop"].dtype.kind in ("i", "f") or pd.api.types.is_numeric_dtype(df["pop"])


def test_xlsx_ingest(tmp_path, etl_service, state_store):
    df_input = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    f = tmp_path / "sheet.xlsx"
    df_input.to_excel(str(f), index=False)

    meta = etl_service.ingest_file(str(f), session_id="s2")
    assert meta["rows"] == 2
    df = state_store.load_dataframe("s2")
    assert list(df["a"]) == [1, 2]


def test_json_ingest(tmp_path, etl_service, state_store):
    df_input = pd.DataFrame({"k": ["x", "y"], "v": [10, 20]})
    f = tmp_path / "data.json"
    f.write_text(df_input.to_json(orient="records"), encoding="utf-8")

    meta = etl_service.ingest_file(str(f), session_id="s3")
    assert meta["rows"] == 2
    df = state_store.load_dataframe("s3")
    assert "k" in df.columns


@pytest.mark.skip(reason="Legacy ETL module and test structure is outdated.")
def test_sql_ingest(tmp_path, etl_service, state_store):
    # create sqlite db and table
    db_path = tmp_path / "test.db"
    con = sqlite3.connect(str(db_path))
    cur = con.cursor()
    cur.execute("CREATE TABLE people (city TEXT, pop INTEGER);")
    cur.execute("INSERT INTO people VALUES ('Madrid', 6700000);")
    cur.execute("INSERT INTO people VALUES ('Barcelona', 5600000);")
    con.commit()
    con.close()

    # write select query to file
    qfile = tmp_path / "query.sql"
    qfile.write_text("SELECT * FROM people;", encoding="utf-8")

    meta = etl_service.ingest_file(str(qfile), session_id="s_sql", db_uri=str(db_path))
    assert meta["rows"] == 2
    df = state_store.load_dataframe("s_sql")
    assert "city" in df.columns
    assert set(df["city"].tolist()) == {"Madrid", "Barcelona"}


def test_multiple_files_unification(tmp_path, etl_service, state_store):
    # first CSV
    f1 = tmp_path / "part1.csv"
    f1.write_text("id,val\n1,10\n2,20\n", encoding="utf-8")
    # second CSV
    f2 = tmp_path / "part2.csv"
    f2.write_text("id,val\n3,30\n", encoding="utf-8")

    # ingest both into same session
    etl_service.ingest_file(str(f1), session_id="session_merge")
    etl_service.ingest_file(str(f2), session_id="session_merge")

    df = state_store.load_dataframe("session_merge")
    assert df.shape[0] == 3
    assert set(df["id"].astype(int).tolist()) == {1, 2, 3}
