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

    connection.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            percentage INTEGER NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id)
                REFERENCES documents (document_id)
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
        DELETE FROM quiz_results
        WHERE document_id = ?
        """,
        (document_id,)
    )

    connection.execute(
        """
        DELETE FROM documents
        WHERE document_id = ?
        """,
        (document_id,)
    )

    connection.commit()
    connection.close()


def save_quiz_result(document_id, score, total, percentage):
    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO quiz_results (
            document_id,
            score,
            total,
            percentage
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            document_id,
            score,
            total,
            percentage
        )
    )

    connection.commit()
    connection.close()

def get_quiz_results():
    connection = get_db_connection()

    results = connection.execute(
        """
        SELECT
            quiz_results.id,
            documents.filename,
            quiz_results.score,
            quiz_results.total,
            quiz_results.percentage,
            quiz_results.completed_at
        FROM quiz_results
        JOIN documents
            ON quiz_results.document_id = documents.document_id
        ORDER BY quiz_results.completed_at DESC
        """
    ).fetchall()

    connection.close()

    return results

def get_dashboard_stats():
    connection = get_db_connection()

    document_count = connection.execute(
        "SELECT COUNT(*) FROM documents"
    ).fetchone()[0]

    quiz_count = connection.execute(
        "SELECT COUNT(*) FROM quiz_results"
    ).fetchone()[0]

    average_score = connection.execute(
        "SELECT AVG(percentage) FROM quiz_results"
    ).fetchone()[0]

    connection.close()

    if average_score is None:
        average_score = 0

    return {
        "document_count": document_count,
        "quiz_count": quiz_count,
        "average_score": round(average_score)
    }

def delete_orphaned_quiz_results():
    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM quiz_results
        WHERE document_id NOT IN (
            SELECT document_id
            FROM documents
        )
        """
    )

    connection.commit()
    connection.close()