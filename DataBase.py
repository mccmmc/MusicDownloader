import sqlite3
import json

conn = sqlite3.connect(r'data\Downloaded_tracks.sqlite')
cursor = conn.cursor()


def update_db(artist_names, album_title, album_cover_link, track_title):
    artists_id = []
    for artist in artist_names:
        cursor.execute(f"""INSERT OR IGNORE INTO Artists(TITLE)
    VALUES ('{artist}')""")  # add artist in db

        artists_id.append(*cursor.execute(f"""SELECT ID
             FROM Artists
             WHERE TITLE = '{artist}'""").fetchone())  # reception artists_id
    artist_id_string = json.dumps(artists_id)
    cursor.execute(f"""INSERT OR IGNORE INTO Albums(TITLE, AUTHOR, COVER_LINK)
    VALUES ('{album_title[0]}',
            ?,
            '{album_cover_link}');""", (artist_id_string,))  # add album in db

    cursor.execute(f"""INSERT OR IGNORE INTO Tracks(TITLE, ALBUM)
VALUES ('{track_title}',
        (SELECT ID
         FROM Albums
         WHERE TITLE = '{album_title[0]}'));""")  # add track in db

    conn.commit()


def clear_db():  # clear db
    cursor.execute("""DELETE 
    from Artists""")
    cursor.execute("""UPDATE SQLITE_SEQUENCE 
    SET SEQ=0 
    WHERE NAME = 'Artists'""")
    cursor.execute("""DELETE 
    from Albums""")
    cursor.execute("""UPDATE SQLITE_SEQUENCE 
    SET SEQ=0 
    WHERE NAME = 'Albums'""")
    cursor.execute("""DELETE 
    from Tracks""")
    cursor.execute("""UPDATE SQLITE_SEQUENCE 
    SET SEQ=0 
    WHERE NAME = 'Tracks'""")
    conn.commit()


if __name__ == '__main__':
    clear_db()
