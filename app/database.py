import sqlite3
import os


DATABASE_PATH = os.path.join(
    os.path.dirname(__file__),
    "study_assistant.db"
)


def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection

def initialise_database():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()

def save_document(document_id, filename, filepath):
    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO documents (document_id, filename, filepath)
        VALUES (?, ?, ?)
        """,
        (document_id, filename, filepath)
    )

    connection.commit()
    connection.close()

def get_all_documents():
    connection = get_db_connection()

    documents = connection.execute(
        """
        SELECT id, document_id, filename, uploaded_at
        FROM documents
        ORDER BY uploaded_at DESC
        """
    ).fetchall()

    connection.close()

    return documents

def get_document(document_id):
    connection = get_db_connection()

    document = connection.execute(
        """
        SELECT *
        FROM documents
        WHERE document_id = ?
        """,
        (document_id,)
    ).fetchone()

    connection.close()

    return document

def delete_document(document_id):
    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM documents
        WHERE document_id = ?
        """,
        (document_id,)
    )

    connection.commit()
    connection.close()