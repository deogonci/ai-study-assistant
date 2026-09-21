from app.utils import allowed_file


def test_pdf_is_allowed():
    assert allowed_file("notes.pdf") is True


def test_txt_is_allowed():
    assert allowed_file("notes.txt") is True


def test_extensions_are_case_insensitive():
    assert allowed_file("notes.PDF") is True


def test_unsupported_file_is_rejected():
    assert allowed_file("photo.jpg") is False


def test_filename_without_extension_is_rejected():
    assert allowed_file("notes") is False