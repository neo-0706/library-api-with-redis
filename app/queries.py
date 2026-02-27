SEARCH_AUTHORS_QUERY = """
    SELECT
        authors.id,
        authors.name AS author_name,
        COUNT(books.id) AS book_count
    FROM authors
    LEFT JOIN books ON authors.id = books.author_id
    WHERE authors.name ILIKE %s
    GROUP BY authors.id, authors.name
    ORDER BY book_count DESC, authors.name ASC
    LIMIT %s;
    """

GET_AUTHOR_BOOKS_QUERY = """
    SELECT
        books.id,
        books.title
    FROM books
    WHERE books.author_id = %s
    ORDER BY books.title;
    """
