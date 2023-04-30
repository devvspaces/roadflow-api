import mindsdb_sdk
from django.conf import settings
from Curriculum.models import CurriculumReview

username = settings.MINDSDB_SERVER_USERNAME
password = settings.MINDSDB_SERVER_PASSWORD

server = None


def connect_server():
    global server
    if not server:
        server = mindsdb_sdk.connect(
            'https://cloud.mindsdb.com',
            login=username,
            password=password
        )
    return server


def make_query(text: str, model: str):
    return f"""
    SELECT *
    FROM mindsdb.{model}
    WHERE text = '{text}'
    """


def classify_text(text: str):
    server = connect_server()
    project = server.get_project('mindsdb')
    max_label = ""
    max_score = 0

    df = project.query(make_query(text, "hf_classify")).fetch()
    data = df['PRED_explain'][0]
    for k, v in CurriculumReview.LABEL:
        current = data.get(v)
        if current > max_score:
            max_score = current
            max_label = k

    return max_label


def sentiment_text(text: str):
    server = connect_server()
    project = server.get_project('mindsdb')
    max_label = ""
    max_score = 0

    df = project.query(make_query(text, "hf_sentiment")).fetch()
    data = df['PRED_explain'][0]
    for k, v in CurriculumReview.SENTIMENT:
        current = data.get(v)
        if current > max_score:
            max_score = current
            max_label = k
    return max_label
