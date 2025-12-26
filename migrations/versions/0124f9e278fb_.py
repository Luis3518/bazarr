"""empty message

Revision ID: 0124f9e278fb
Revises: df76a4410347
Create Date: 2025-12-21 21:54:24.686059

"""
from alembic import op
import sqlalchemy as sa
import ast

from app.database import TableEpisodes, TableMovies, TableEpisodesSubtitles, TableMoviesSubtitles, select


# revision identifiers, used by Alembic.
revision = '0124f9e278fb'
down_revision = 'df76a4410347'
branch_labels = None
depends_on = None

bind = op.get_context().bind


def parse_language(language):
    split_language = language.split(':')
    return (
        split_language[0],
        bool(split_language[1] == 'hi') if len(split_language) > 1 else False,
        bool(split_language[1] == 'forced') if len(split_language) > 1 else False
    )


def upgrade():
    episodes = bind.execute(
        select(TableEpisodes.sonarrEpisodeId,
               TableEpisodes.sonarrSeriesId,
               TableEpisodes.subtitles)
        .where(TableEpisodes.subtitles.is_not(None), TableEpisodes.subtitles != '[]')
    ).all()

    for episode in episodes:
        try:
            subtitles = ast.literal_eval(episode.subtitles)
        except Exception:
            continue
        else:
            for subtitle in subtitles:
                subtitle_language = parse_language(subtitle[0])
                bind.execute(sa.insert(TableEpisodesSubtitles).values(
                    sonarrEpisodeId=episode.sonarrEpisodeId,
                    sonarrSeriesId=episode.sonarrSeriesId,
                    language=subtitle_language[0],
                    hi=subtitle_language[1],
                    forced=subtitle_language[2],
                    path=subtitle[1],
                    size=subtitle[2]
                ))

    op.drop_column(column_name='subtitles', table_name='table_episodes')

    movies = bind.execute(
        select(TableMovies.radarrId,
               TableMovies.subtitles)
        .where(TableMovies.subtitles.is_not(None), TableMovies.subtitles != '[]')
    ).all()

    for movie in movies:
        try:
            subtitles = ast.literal_eval(movie.subtitles)
        except Exception:
            continue
        else:
            for subtitle in subtitles:
                subtitle_language = parse_language(subtitle[0])
                bind.execute(sa.insert(TableMoviesSubtitles).values(
                    radarrId=movie.radarrId,
                    language=subtitle_language[0],
                    hi=subtitle_language[1],
                    forced=subtitle_language[2],
                    path=subtitle[1],
                    size=subtitle[2]
                ))

    op.drop_column(column_name='subtitles', table_name='table_movies')


def downgrade():
    pass
