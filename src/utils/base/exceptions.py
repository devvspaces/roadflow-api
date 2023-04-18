from rest_framework.exceptions import ParseError  # pragma: no cover


class QueryParseError(ParseError):  # pragma: no cover
    default_detail = 'Malformed or Incomplete query data'
    default_code = 'baq_query_data'
