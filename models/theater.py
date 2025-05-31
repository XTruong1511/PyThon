# models/theater.py
class Theater:
    """
    Lớp đại diện cho một phòng chiếu
    """
    def __init__(self, id="", name="", type="", capacity=0, layout=None):
        self.id = id
        self.name = name
        self.type = type  # Loại: Thường, VIP, 3D, IMAX, 4DX
        self.capacity = capacity
        self.layout = layout if layout else {"rows": 0, "cols": 0}
    
    @classmethod
    def from_dict(cls, data):
        """
        Tạo đối tượng Theater từ dictionary
        """
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            type=data.get("type", ""),
            capacity=data.get("capacity", 0),
            layout=data.get("layout", {"rows": 0, "cols": 0})
        )
    
    def to_dict(self):
        """
        Chuyển đối tượng Theater thành dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "capacity": self.capacity,
            "layout": self.layout
        }
