def list_files():
    """
    Mock Google Drive file listing.
    """

    files = [
        {"id": "1", "name": "Agenda.pdf"},
        {"id": "2", "name": "Project_Plan.docx"},
        {"id": "3", "name": "Budget.xlsx"},
    ]

    return files
