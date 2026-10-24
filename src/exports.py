"""Bounded-memory CSV serialization for browser downloads."""
from tempfile import TemporaryFile

def sales_csv_file(data):
    """Return a seekable temporary CSV; serialize in chunks rather than one string.

    Streamlit reads this file when the user requests a download. The returned
    handle owns the temporary file and closes it when released.
    """
    handle = TemporaryFile(mode='w+b')
    try:
        data.to_csv(handle, index=False, chunksize=10000)
        handle.seek(0)
    except Exception:
        handle.close()
        raise
    return handle
