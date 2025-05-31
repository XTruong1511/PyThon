# models/movie.py
from datetime import datetime

class Movie:
    """
    Lớp đại diện cho một bộ phim
    """
    def __init__(self, id="", title="", director="", duration=0, genre=None, 
                 release_date="", rating=0, description="", poster_url="", trailer_url=""):
        self.id = id
        self.title = title
        self.director = director
        self.duration = duration
        self.genre = genre if genre else []
        self.release_date = release_date
        self.rating = rating
        self.description = description
        self.poster_url = poster_url
        self.trailer_url = trailer_url
    
    @classmethod
    def from_dict(cls, data):
        """
        Tạo đối tượng Movie từ dictionary
        """
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            director=data.get("director", ""),
            duration=data.get("duration", 0),
            genre=data.get("genre", []),
            release_date=data.get("release_date", ""),
            rating=data.get("rating", 0),
            description=data.get("description", ""),
            poster_url=data.get("poster_url", ""),
            trailer_url=data.get("trailer_url", "")
        )
    
    def to_dict(self):
        """
        Chuyển đối tượng Movie thành dictionary
        """
        return {
            "id": self.id,
            "title": self.title,
            "director": self.director,
            "duration": self.duration,
            "genre": self.genre,
            "release_date": self.release_date,
            "rating": self.rating,
            "description": self.description,
            "poster_url": self.poster_url,
            "trailer_url": self.trailer_url
        }
