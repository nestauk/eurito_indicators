from eurito_indicators.getters.cord.articles import Article
from eurito_indicators.getters.cord.orm_utils import object_to_dict, db_session, get_mysql_engine

def get_cord_articles(db_path, limit=None):
    chunksize = 10000
    if limit is not None:
        chunksize = min(chunksize, limit)
    arts = []
    engine = get_mysql_engine(db_path)
    with db_session(engine) as session:
        query = session.query(Article)
        # .order_by(Article.id)
        # .filter(Article.article_source == 'cord')
        while True:
            actual_query = query
            if len(arts) > 0:
                max_id = arts[-1]['id']
                actual_query = query.filter(Article.id > max_id)
            new_arts = [object_to_dict(obj) for obj in actual_query.limit(chunksize)]
            print(len(new_arts))
            arts += new_arts
            if len(new_arts) < chunksize:
                break
            if limit is not None and len(arts) >= limit:
                break
    return arts



